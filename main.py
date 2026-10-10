import sys
import os
from src.Analyzer.parsers.python_ast import PythonASTParser
from src.Analyzer.parsers.java_ast import JavaASTParser
from src.Analyzer.classifier.deterministic import DeterministicClassifier
from src.Analyzer.orchestrator import ASTOrchestrator
from src.Analyzer.reporter import JSONReporter
from src.Collector.colletor import ProjectCollector
from src.Donwloader.donwloader import ProjectDownloader 
from src.logger import registrar_log

# Configuração de caminhos usando os.path para compatibilidade Windows/Linux/Docker
DATA_DIR = os.path.join(".", "data", "zips")
OUTPUT_DIR = os.path.join(".", "reports")

def run_phase_1():
    registrar_log("PIPELINE", "FASE 1", "Iniciando coleta de metadados")
    print("\n[+] Iniciando Fase 1: Coleta de Metadados (Filtro e Database)...")
    coletor = ProjectCollector()
    coletor.run()
    print("[✓] Fase 1 concluída!")

def run_phase_2():
    registrar_log("PIPELINE", "FASE 2", "Iniciando download dos ZIPs")
    print("\n[+] Iniciando Fase 2: Download dos .ZIPs...")
    downloader = ProjectDownloader()
    downloader.run()
    print("[✓] Fase 2 concluída!")

def run_phase_3():
    registrar_log("PIPELINE", "FASE 3", "Iniciando análise AST")
    print("\n[+] Iniciando Fase 3: Análise AST (Mocks e Asserts)")
    print(f"    - Diretório de entrada: {DATA_DIR}")
    print(f"    - Diretório de saída: {OUTPUT_DIR}")
    
    parsers = {
        'python': PythonASTParser(),
        'java': JavaASTParser()
    }
    classifier = DeterministicClassifier()
    reporter = JSONReporter(output_dir=OUTPUT_DIR)
    
    orchestrator = ASTOrchestrator(
        data_dir=DATA_DIR,
        classifier=classifier,
        parsers=parsers,
        reporter=reporter,
        max_workers=4
    )
    
    orchestrator.run()
    print("[✓] Fase 3 concluída!")

def run_full_pipeline():
    print("\n[!] Iniciando Pipeline Completo...")
    run_phase_1()
    run_phase_2()
    run_phase_3()
    print("\n[✓] Pipeline Completo finalizado com sucesso!")

def mostrar_menu():
    while True:
        print("\n" + "="*55)
        print("    DETERMINISTIC TEST CLASSIFIER - MENU PRINCIPAL")
        print("="*55)
        print("Selecione uma etapa para executar:")
        print("  1. Executar Fase 1: Coleta de Metadados (Collector)")
        print("  2. Executar Fase 2: Download dos Projetos (Downloader)")
        print("  3. Executar Fase 3: Análise AST (Mocks e Asserts)")
        print("  4. Executar Pipeline Completo (1 -> 2 -> 3)")
        print("  0. Sair")
        print("="*55)
        
        escolha = input("Digite a opção desejada: ").strip()
        
        if escolha == '1':
            run_phase_1()
        elif escolha == '2':
            run_phase_2()
        elif escolha == '3':
            run_phase_3()
        elif escolha == '4':
            run_full_pipeline()
        elif escolha == '0':
            print("\nEncerrando o programa. Até logo!\n")
            sys.exit(0)
        else:
            print("\n[-] Opção inválida. Por favor, escolha um número de 0 a 4.")

def main():    
    registrar_log("PIPELINE", "INICIADO", "Menu interativo acionado")
    try:
        mostrar_menu()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário. Saindo...")
        sys.exit(0)

if __name__ == "__main__":
    main()