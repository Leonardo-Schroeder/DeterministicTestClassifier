from src.Analyzer.models.enums import TestGroup
from src.Analyzer.models.ast_data import ASTContext
from src.Analyzer.models.reports import TestCaseAnalysis

class DeterministicClassifier:
    def __init__(self):
        self.io_namespaces = (
            'java.sql', 'java.net', 'java.io', 'java.nio', 'javax.net',
            'org.apache.http', 'okhttp3', 'requests', 'urllib', 'aiohttp', 'socket',
            'feign', 'retrofit2',
            'org.hibernate', 'javax.persistence', 'org.springframework.data',
            'com.mongodb', 'org.postgresql', 'redis.clients', 'com.datastax',
            'org.testcontainers', 'com.github.dockerjava', 'org.apache.kafka', 
            'software.amazon.awssdk', 'com.amazonaws', 'org.neo4j', 'org.couchbase', 'org.elasticsearch', 'org.opensearch',
            'org.h2', 'com.h2database', 'org.sqlite', 'com.microsoft.sqlserver',
            'oracle.jdbc', 'com.mysql', 'com.mysql.cj.jdbc', 'org.springframework.web.client', 'org.springframework.http',
            'com.squareup.okhttp', 'org.apache.hc.client5.http',
            'java.net.http', 'javax.ws.rs.client', 'jersey.client',
            'com.google.api.client.http', 'com.github.kittinunf.fuel', 'org.springframework.kafka', 'org.apache.pulsar', 'rabbitmq.client',
            'com.rabbitmq.client', 'org.springframework.amqp',
            'org.apache.rocketmq', 'org.eclipse.paho.client.mqttv3', 'com.google.cloud', 'com.azure.storage', 'com.azure.cosmos',
            'io.minio', 'org.jclouds', 'com.oracle.bmc',
            'com.dropbox.core', 'com.box.sdk', 'io.lettuce.core', 'org.redisson', 'redis.clients.jedis',     'org.elasticsearch.client', 'co.elastic.clients', 'org.elasticsearch.action', 
            'io.grpc', 'com.google.protobuf', 'org.apache.thrift', 'javax.mail', 'org.springframework.mail', 'com.sendgrid',     'java.nio.file', 'org.apache.commons.io', 'com.google.common.io',
        )
        self.assert_namespaces = (
            'org.junit.Assert', 'org.junit.jupiter.api.Assertions', 
            'org.mockito.Mockito', 'org.assertj.core.api.Assertions', 
            'org.hamcrest.MatcherAssert',     'com.google.common.truth.Truth',  # Google Truth
            'org.junit.jupiter.api.Assertions',  # JUnit 5 (você já tem, mas manter)
            'org.junit.Assert',
            'org.testng.Assert',
            'org.assertj.core.api.Assertions',
            'org.hamcrest.MatcherAssert', 
            'com.github.npathai.hamcrestopt.OptionalMatchers',
            'io.kotest.assertions',
            'org.mockito.Mockito',
            'org.mockito.BDDMockito', 
            'org.powermock.api.mockito.PowerMockito',
            'org.springframework.test.web.servlet.ResultActions',
            'org.springframework.test.web.servlet.request.MockMvcRequestBuilders',
            'org.springframework.test.web.servlet.result.MockMvcResultMatchers',
            'com.jayway.jsonpath.JsonPath',
            'io.restassured.RestAssured', 'org.web3j.protocol.core.methods.response',
        )
        self.assert_keywords = {'assert', 'verify', 'expect', 'fail', 'should'}  
        self.ignore_namespaces = (
            'org.slf4j', 'org.apache.logging', 'java.util', 'java.lang',
            'org.apache.commons', 'com.google.common', 'org.springframework.util',

             # Logging (completo)
            'org.slf4j', 'org.apache.logging', 'java.util.logging', 'log4j', 
            'org.apache.log4j', 'ch.qos.logback', 'org.tinylog',

            # Utilitários Java padrão
            'java.util', 'java.lang', 'java.math', 'java.text', 'java.time',
            'java.time.format', 'java.util.concurrent', 'java.util.stream',
            'java.util.function', 'java.util.regex', 'java.util.zip',
            'java.security', 'java.nio.charset',

            # Utilitários de terceiros
            'org.apache.commons', 'com.google.common', 'org.springframework.util',
            'org.apache.commons.lang3', 'org.apache.commons.collections4',
            'com.google.common.base', 'com.google.common.collect', 'com.google.common.io',
            'commons-io', 'org.joda.time',

            # Projeto Lombok (geração de código)
            'lombok',

            # Reflexão e proxies
            'java.lang.reflect', 'java.lang.invoke', 'net.sf.cglib', 'org.springframework.cglib',
            'org.mockito.cglib', 'org.objenesis',

            # JSON/XML parsing (não é domínio)
            'com.fasterxml.jackson', 'com.google.gson', 'org.json', 'javax.json',
            'com.fasterxml.jackson.databind', 'com.fasterxml.jackson.core',
            'org.simpleframework.xml', 'javax.xml.bind', 'com.thoughtworks.xstream',

            # Anotações
            'java.lang.annotation', 'javax.annotation', 

            # Streams reativos (infraestrutura)
            'reactor.core.publisher', 'rx.Observable', 'io.reactivex',

            # Configuração e properties
            'org.springframework.core.env', 'org.springframework.boot.context.properties',
            'org.springframework.beans.factory.annotation.Value',

            # AOP e proxies
            'org.aspectj.lang', 'org.springframework.aop',

            # Test utilities que não são assertions
            'org.junit.rules', 'org.junit.jupiter.api.extension', 'org.testng.annotations',
            'org.springframework.boot.test.context.TestConfiguration'
        )
        self.integration_markers = (
            # Spring Boot
            'SpringBootTest', 'DataJpaTest', 'DataMongoTest', 'DataRedisTest',
            'WebMvcTest', 'WebFluxTest', 'RestClientTest', 'JsonTest',
            'JdbcTest', 'DataLdapTest', 'DataCassandraTest', 'DataElasticsearchTest',

            # Elasticsearch específico
            'ESIntegTestCase', 'ESRestTestCase', 'ESTestCase',

            # Testcontainers
            'Testcontainers', 'Container', 'TestcontainersExtension',

            # Quarkus
            'QuarkusIntegrationTest', 'QuarkusTest',

            # Micronaut
            'MicronautTest',

            # WildFly/Arquillian
            'Arquillian', 'RunAsClient',

            # Database testing
            'DbUnitTest', 'SpringBootTest', '@DataJpaTest',

            # Integration test padrão
            'IntegrationTest', 'Integration', 'IT'
        )
    
    def classify(self, ast_context: ASTContext) -> TestCaseAnalysis:
        has_real_io = False
        has_assertions = False
        domain_types_called = set()

        # 1. VARREDURA DE MÉTODOS
        for inv in ast_context.invocations:
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
        found_markers = [m for m in integration_markers if m in ast_context.class_annotations or m in ast_context.parent_class]

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