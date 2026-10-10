import re
from src.Analyzer.models.enums import TestGroup
from src.Analyzer.models.ast_data import ASTContext
from src.Analyzer.models.reports import TestCaseAnalysis

class DeterministicClassifier:
    def __init__(self):

        self.total_invocacoes = 0
        self.total_unknowns = 0

        self.io_namespaces = (
            'java.sql', 'java.net', 'java.io', 'java.nio', 'javax.net',
            'org.apache.http', 'okhttp3', 'requests', 'urllib', 'aiohttp', 'socket',
            'feign', 'retrofit2',
            'org.hibernate', 'javax.persistence', 'org.springframework.data',
            'com.mongodb', 'org.postgresql', 'redis.clients', 'com.datastax',
            'org.testcontainers', 'com.github.dockerjava', 'org.apache.kafka', 
            'software.amazon.awssdk', 'com.amazonaws'
        )
        self.assert_namespaces = (
            'org.junit.Assert', 'org.junit.jupiter.api.Assertions', 
            'org.mockito.Mockito', 'org.assertj.core.api.Assertions', 
            'org.hamcrest.MatcherAssert'
        )
        self.assert_keywords = {'assert', 'verify', 'expect', 'fail', 'should'}
        self.ignore_namespaces = (
            'org.slf4j', 'org.apache.logging', 'java.util', 'java.lang',
            'org.apache.commons', 'com.google.common', 'org.springframework.util'
        )
        self.integration_markers = (
            'SpringBootTest', 'DataJpaTest', 'Testcontainers', 'WebMvcTest',
            'ESIntegTestCase'
        )
    
    def _matches_parent(self, marker: str, parent_class: str) -> bool:
        return bool(re.search(rf'\b{re.escape(marker)}\b', parent_class))

    def classify(self, ast_context: ASTContext) -> TestCaseAnalysis:
        has_real_io = False
        has_assertions = False
        domain_types_called = set()

        # 1. VARREDURA DE MÉTODOS
        for inv in ast_context.invocations:
            self.total_invocacoes += 1
            if inv.caller_type == 'UNKNOWN':
                self.total_unknowns += 1

            caller_lower = inv.caller_type.lower()
            method_lower = inv.method_name.lower()

            # Checagem de Asserção
            if any(inv.caller_type.startswith(ns) for ns in self.assert_namespaces) or any(kw in method_lower for kw in self.assert_keywords):
                has_assertions = True
                continue

            # Checagem de I/O
            if any(inv.caller_type.startswith(ns) for ns in self.io_namespaces):
                has_real_io = True
                continue

            # Checagem de Domínio (Com filtro anti-ruído)
            is_java_native = inv.caller_type.startswith('java.') or inv.caller_type.startswith('javax.')
            is_ignored_lib = any(inv.caller_type.startswith(ns) for ns in self.ignore_namespaces)
            is_builder_or_dto = caller_lower.endswith('builder') or caller_lower.endswith('dto') or caller_lower.endswith('factory')
            is_getter_setter = method_lower.startswith('get') or method_lower.startswith('set')

            if not (is_java_native or is_ignored_lib or is_builder_or_dto or is_getter_setter or inv.caller_type == 'UNKNOWN'):
                domain_types_called.add(inv.caller_type)

        has_mocks = len(ast_context.mocked_types) > 0
        has_domain_coupling = len(domain_types_called) > 1
        is_component = has_mocks and has_domain_coupling

        # 2. VARREDURA DA CLASSE (Testes Guiados por Framework)
        integration_markers = self.integration_markers
        found_markers = [
        m for m in integration_markers
            if m in ast_context.class_annotations or self._matches_parent(m, ast_context.parent_class)
        ]
        
        # 3. ÁRVORE DE DECISÃO (Guard Clauses / Retorno Antecipado)
        
        # Cenário A: O framework domina o teste
        if found_markers:
            return TestCaseAnalysis(
                ast_context.method_name, ast_context.file_path, TestGroup.INTEGRATION,
                has_assertions, False, f"Marcador de integração detectado na classe ({found_markers[0]})."
            )

        # Cenário B: Integração manual raiz (bateu na rede/disco sem mockar)
        if has_real_io and not has_mocks:
            return TestCaseAnalysis(
                ast_context.method_name, ast_context.file_path, TestGroup.INTEGRATION,
                has_assertions, False, "Acesso direto a I/O sem a presença de objetos simuladores."
            )

        # Cenário C: Unidade (com verificação se vazou para Componente)
        justification = f"Unitário com características de COMPONENTE (acoplou os domínios: {domain_types_called})." if is_component else "Unitário estrito: Isolamento atômico clássico."
        
        return TestCaseAnalysis(
            ast_context.method_name, ast_context.file_path, TestGroup.UNIT,
            has_assertions, is_component, justification
        )