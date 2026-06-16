import ast
import zipfile
from typing import List, Set
from src.Analyzer.parsers.base import BaseASTParser
from src.Analyzer.models.ast_data import ASTContext, MethodInvocation

class PythonASTParser(BaseASTParser):
    def extract(self, zip_path: str) -> List[ASTContext]:
        if not self._is_valid_zip(zip_path): return []
        
        contexts = []
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_path in z.namelist():
                if file_path.endswith('.py') and 'test' in file_path.lower():
                    source = z.read(file_path).decode('utf-8', errors='ignore')
                    contexts.extend(self._process_file(source, file_path))
        return contexts

    def _process_file(self, source: str, file_path: str) -> List[ASTContext]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        # 1. Coleta Imports globais do arquivo
        imported_libs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names: imported_libs.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_libs.add(node.module)

        contexts = []
        # 2. Busca os métodos de teste
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test'):
                contexts.append(self._extract_method_context(node, file_path, imported_libs))
                
        return contexts

    def _extract_method_context(self, method_node: ast.FunctionDef, file_path: str, global_imports: Set[str]) -> ASTContext:
        invocations = set()
        mocked_types = set()
        
        # Analisa os decoradores (ex: @patch('pacote.Modulo'))
        for dec in method_node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, 'id', '') == 'patch':
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    mocked_types.add(dec.args[0].value)

        # Analisa o corpo do método
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                # Captura chamadas do tipo objeto.metodo()
                if isinstance(node.func, ast.Attribute):
                    # Se for var.metodo(), 'value' é a var e 'attr' é o metodo
                    caller = getattr(node.func.value, 'id', 'UNKNOWN')
                    if caller == 'self': # Ignora o self do python e pega o proximo nivel se existir
                         caller = getattr(node.func.value, 'attr', 'UNKNOWN')
                         
                    method = node.func.attr
                    invocations.add(MethodInvocation(caller_type=caller, method_name=method))
                    
                # Captura mocks instanciados: mock_obj = MagicMock()
                elif getattr(node.func, 'id', '') in ['Mock', 'MagicMock']:
                    mocked_types.add("ManualMockInstance")

        return ASTContext(
            method_name=method_node.name,
            file_path=file_path,
            invocations=invocations,
            mocked_types=mocked_types,
            imported_libs=global_imports
        )