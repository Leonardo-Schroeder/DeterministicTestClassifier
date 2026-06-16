import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

from src.logger import registrar_log
from src.Analyzer.models.reports import ProjectReport
from src.Analyzer.models.enums import TestGroup

class ASTOrchestrator:
    def __init__(self, data_dir: str, classifier, parsers: dict, reporter, max_workers: int = 4):
        self.data_dir = data_dir
        self.classifier = classifier
        self.parsers = parsers  # Ex: {'python': PythonASTParser(), 'java': JavaASTParser()}
        self.reporter = reporter
        self.max_workers = max_workers

    def run(self):
        registrar_log("ORQUESTRADOR", "INICIADO", f"Iniciando com {self.max_workers} threads.")
        
        for lang, parser in self.parsers.items():
            self._analyze_language(lang, parser)
            
        registrar_log("ORQUESTRADOR", "FINALIZADO", "Varredura concluída.")

    def _analyze_language(self, language: str, parser):
        lang_dir = os.path.join(self.data_dir, language)
        if not os.path.exists(lang_dir):
            registrar_log("ORQUESTRADOR", "AVISO", f"Diretório vazio/inexistente: {lang_dir}")
            return

        zip_files = [f for f in os.listdir(lang_dir) if f.endswith('.zip')]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futuros = {
                executor.submit(self._process_project, zip_file, lang_dir, language, parser): zip_file
                for zip_file in zip_files
            }

            for futuro in as_completed(futuros):
                zip_name = futuros[futuro]
                try:
                    futuro.result()
                except Exception as e:
                    registrar_log("ORQUESTRADOR", "ERRO FATAL", f"Projeto {zip_name} quebrou: {str(e)}")

    def _process_project(self, zip_file: str, lang_dir: str, language: str, parser):
        project_name = zip_file.replace('.zip', '')
        zip_path = os.path.join(lang_dir, zip_file)
        
        registrar_log("ORQUESTRADOR", "PROCESSANDO", f"Analisando: {project_name} ({language})")
        
        # 1. Extrai a AST (Operários trabalhando)
        ast_contexts = parser.extract(zip_path)
        
        # 2. Classifica de forma determinística
        analyzed_cases = []
        counter = Counter()
        
        for context in ast_contexts:
            analysis = self.classifier.classify(context)
            analyzed_cases.append(analysis)
            counter[analysis.group.value] += 1
            
        # 3. Consolida Estatísticas e Gera Relatório
        total = len(analyzed_cases)
        percentages = {g.value: 0.0 for g in TestGroup}
        
        for group_name, count in counter.items():
            percentages[group_name] = round((count / total) * 100, 2) if total > 0 else 0.0
            
        report = ProjectReport(
            project_name=project_name, 
            language=language, 
            total_tests=total, 
            group_percentages=percentages, 
            analyzed_cases=analyzed_cases
        )
        
        # 4. Salva no disco
        self.reporter.save(report)