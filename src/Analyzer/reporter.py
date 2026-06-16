import os
import json
from enum import Enum
from dataclasses import asdict
from src.Analyzer.models.reports import ProjectReport
from src.logger import registrar_log

class JSONReporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def save(self, report: ProjectReport):
        lang_dir = os.path.join(self.output_dir, report.language)
        os.makedirs(lang_dir, exist_ok=True)
        
        json_path = os.path.join(lang_dir, f"{report.project_name}.json")
        
        # Função interna para lidar com Enums e Sets durante o dump do JSON
        def custom_serializer(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(
                    asdict(report), 
                    f, 
                    indent=4, 
                    default=custom_serializer, 
                    ensure_ascii=False
                )
            registrar_log("REPORTER", "SUCESSO", f"Relatório salvo: {json_path}")
        except Exception as e:
            registrar_log("REPORTER", "ERRO", f"Falha ao salvar {json_path}: {str(e)}")