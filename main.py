from src.Analyzer.parsers.python_ast import PythonASTParser
from src.Analyzer.classifier.deterministic import DeterministicClassifier
from src.Analyzer.orchestrator import ASTOrchestrator
from src.Analyzer.parsers.java_ast import JavaASTParser
from src.Analyzer.parsers.python_ast import PythonASTParser
from src.Analyzer.reporter import JSONReporter
from src.Collector.colletor import ProjectCollector
from src.Donwloader.donwloader import ProjectDownloader 
from src.logger import registrar_log

def main():    
    registrar_log("PIPELINE", "INICIADO", "Execução do main.py acionada")

    # FASE 1: Coleta de Metadados (Filtro e Database)
    # coletor = ProjectCollector()
    # coletor.run()

    # FASE 2: Download dos .ZIPs
    # downloader = ProjectDownloader()
    # downloader.run()

    # # ==========================================
    # # FASE 3: Análise AST (Mocks e Asserts)
    # # ==========================================

    # # 1. Configura os caminhos
    DATA_DIR = ".\\data\\zips" #Onde ficam os ZIPs (separados nas pastas /python e /java)
    OUTPUT_DIR = ".\\reports" #Onde os JSONs vão cair

    # 1. Configura os caminhos
    # DATA_DIR = ".\\data_test" #Onde ficam os ZIPs (separados nas pastas /python e /java)
    # OUTPUT_DIR = ".\\reports_elastic" #Onde os JSONs vão cair
    
    # 2. Instancia as dependências
    parsers = {
        'python': PythonASTParser(),
        'java': JavaASTParser()
    }
    classifier = DeterministicClassifier()
    reporter = JSONReporter(output_dir=OUTPUT_DIR)
    
    # 3. Inicializa e roda o Orquestrador
    orchestrator = ASTOrchestrator(
        data_dir=DATA_DIR,
        classifier=classifier,
        parsers=parsers,
        reporter=reporter,
        max_workers=4
    )
    
    orchestrator.run()

if __name__ == "__main__":
    main()