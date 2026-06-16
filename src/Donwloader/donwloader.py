import os
import json
import requests
import time
import concurrent.futures
from src.config import TARGET_LANGUAGES
from src.logger import registrar_log

class ProjectDownloader:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        self.zips_dir = os.path.join(base_dir, "zips")
        os.makedirs(self.zips_dir, exist_ok=True)

    def _get_safe_filename(self, full_name: str) -> str:
        return full_name.replace("/", "_") + ".zip"

    def download_repo(self, repo: dict) -> bool:
        """Função isolada para baixar um único repo. Perfeita para rodar em Threads."""
        full_name = repo["full_name"]
        language = repo["language"]
        default_branch = repo["default_branch"]
        
        lang_dir = os.path.join(self.zips_dir, language)
        os.makedirs(lang_dir, exist_ok=True)
        
        safe_name = self._get_safe_filename(full_name)
        filepath = os.path.join(lang_dir, safe_name)

        # Se já existe, ignora super rápido
        if os.path.exists(filepath):
            print(f"Pulando: {full_name}")
            return True

        zip_url = f"https://github.com/{full_name}/archive/refs/heads/{default_branch}.zip"
        
        try:
            response = requests.get(zip_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Sucesso: {full_name}")
                time.sleep(0.5)
                return True
            else:
                print(f"Erro HTTP {response.status_code} em: {full_name}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de Conexão ({full_name}): {e}")
            return False

    def run(self):
        print("\n=== Iniciando Download (Modo TURBO - Multithreading) ===\n")
        
        MAX_WORKERS = 10 
        registrar_log("DOWNLOAD", "INICIADO", f"Multithreading ativado com {MAX_WORKERS} workers") # 👈 LOG
        
        for lang in TARGET_LANGUAGES:
            json_path = os.path.join(self.base_dir, f"{lang}_projects.json")
            
            if not os.path.exists(json_path):
                print(f"Arquivo não encontrado: {json_path}")
                continue

            with open(json_path, 'r', encoding='utf-8') as f:
                repos_dict = json.load(f)

            aceitos = [repo for repo in repos_dict.values() if repo["accepted"]]
            print(f"Processando {len(aceitos)} projetos de {lang.upper()} com {MAX_WORKERS} workers...")
            
            sucessos = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                resultados = executor.map(self.download_repo, aceitos)
                
                for resultado in resultados:
                    if resultado:
                        sucessos += 1
                        
            print(f"\nConcluído para {lang.upper()}: {sucessos}/{len(aceitos)} baixados.\n")
            registrar_log("DOWNLOAD", "RESUMO_EXECUCAO", f"[{lang.upper()}] Processados com sucesso: {sucessos} de {len(aceitos)}")
            registrar_log("DOWNLOAD", "CONCLUIDO", "Rotina de downloads finalizada.")