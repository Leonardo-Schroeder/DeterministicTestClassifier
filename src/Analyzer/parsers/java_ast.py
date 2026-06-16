import zipfile
from typing import List, Set, Dict
from src.Analyzer.parsers.base import BaseASTParser
from src.Analyzer.models.ast_data import ASTContext, MethodInvocation
import javalang

class JavaASTParser(BaseASTParser):
    def extract(self, zip_path: str) -> List[ASTContext]:
        if not self._is_valid_zip(zip_path): return []
        
        contexts = []
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_path in z.namelist():
                if file_path.endswith('.java') and 'test' in file_path.lower():
                    source = z.read(file_path).decode('utf-8', errors='ignore')
                    contexts.extend(self._process_file(source, file_path))
        return contexts

    def _process_file(self, source: str, file_path: str) -> List[ASTContext]:
        try:
            tree = javalang.parse.parse(source)
        except Exception:
            return []
        
        class_annotations = []
        parent_class = ""
        
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            if node.extends:
                parent_class = node.extends.name
            if node.annotations:
                class_annotations = [ann.name for ann in node.annotations]
            break # Só precisamos da classe principal

        # 1. Mapeia Imports (Para resolver FQN depois)
        # Ex: 'Connection' -> 'java.sql.Connection'
        import_map = {}
        for imp in tree.imports:
            class_name = imp.path.split('.')[-1]
            import_map[class_name] = imp.path

        # 2. Mapeia variáveis de classe (Fields) declaradas com @Mock
        class_fields = {}
        mocked_fields = set()
        for path, node in tree.filter(javalang.tree.FieldDeclaration):
            # Ex: private UserRepository repo;
            field_type = node.type.name
            for declarator in node.declarators:
                class_fields[declarator.name] = field_type
                # Verifica anotação de mock
                if any(ann.name in ['Mock', 'MockBean', 'Spy'] for ann in node.annotations):
                    # Salva o pacote completo (FQN) se existir no import_map
                    mocked_fields.add(import_map.get(field_type, field_type))

        contexts = []
        # 3. Analisa os métodos
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            
            # Regra 1: Padrão Moderno (Anotações JUnit 4/5 e TestNG)
            has_modern_annotation = any(
                ann.name in ['Test', 'ParameterizedTest', 'RepeatedTest', 'TestFactory', 'TestTemplate'] 
                for ann in node.annotations
            )
            
            # Regra 2: Padrão Legado (JUnit 3 - O caso do Elasticsearch)
            # Para evitar falsos positivos, exigimos que seja 'public', retorne 'void' e comece com 'test'
            is_legacy_test = (
                node.name.startswith('test') and 
                node.return_type is None and 
                'public' in node.modifiers
            )
            
            # Se bater com qualquer uma das duas regras, extrai o contexto!
            if has_modern_annotation or is_legacy_test:
                contexts.append(
                    self._extract_method_context(
                        node, 
                        file_path, 
                        import_map, 
                        class_fields, 
                        mocked_fields, 
                        class_annotations, 
                        parent_class
                    )
                )
                
        return contexts

    def _extract_method_context(self, method_node, file_path: str, import_map: Dict, class_fields: Dict, mocked_fields: Set, class_annotations: list, parent_class: str) -> ASTContext:
        invocations = set()
        method_mocked_types = set(mocked_fields) # Herda os mocks da classe
        
        # Mapeia variáveis locais do método
        local_vars = {}
        for path, node in method_node.filter(javalang.tree.LocalVariableDeclaration):
            for declarator in node.declarators:
                local_vars[declarator.name] = node.type.name

        # Busca todas as chamadas de método
        for path, node in method_node.filter(javalang.tree.MethodInvocation):
            caller_var = node.qualifier # O que vem antes do ponto (ex: 'repo'.save())
            method_name = node.member   # O que vem depois do ponto (ex: repo.'save'())
            
            # Se for chamando algo de uma variável (não é chamada estática ou interna)
            if caller_var:
                # Resolve o tipo da variável (local ou da classe)
                var_type = local_vars.get(caller_var, class_fields.get(caller_var, caller_var))
                # Resolve o Fully Qualified Name (FQN) com base nos imports
                resolved_type = import_map.get(var_type, var_type)
                invocations.add(MethodInvocation(caller_type=resolved_type, method_name=method_name))
            else:
                # Chamadas diretas (ex: mock(), verify(), assertEquals())
                invocations.add(MethodInvocation(caller_type="UNKNOWN", method_name=method_name))
                if method_name in ['mock', 'spy']:
                    method_mocked_types.add("InlineMockInstance")

        return ASTContext(
            method_name=method_node.name,
            file_path=file_path,
            invocations=invocations,
            mocked_types=method_mocked_types,
            imported_libs=set(import_map.values()),
            class_annotations=class_annotations,
            parent_class=parent_class
        )