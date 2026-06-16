import json
import os
from src.config import BASE_SEARCH_QUERY, TARGET_LANGUAGES
from .github_client import GitHubClient
from src.logger import registrar_log 

class ProjectCollector:
    def __init__(self):
        self.client = GitHubClient()

    def save_language_database(self, language: str, data: dict):
        """Salva a lista de projetos em um arquivo JSON específico para a linguagem"""
        os.makedirs("data", exist_ok=True)
        filename = f"data/{language}_projects.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Banco de dados de {language.upper()} salvo em: {filename}")

    def run(self):
        print("=== Iniciando Coleta de Metadados da IC ===\n")
        registrar_log("COLETA", "INICIADA", "Iniciando busca na API do GitHub")
        
        for lang in TARGET_LANGUAGES:
            query = f"language:{lang} {BASE_SEARCH_QUERY}"
            registrar_log("COLETA", "QUERY_EXECUTADA", f"[{lang.upper()}] String: '{query}'") # 👈 LOG
            
            # max_pages=10 traz os top 1000 repositórios.
            repos = self.client.fetch_repositories(language=lang, query=query, max_pages=10)
            
            # Converte para dicionário e evita duplicatas
            repos_dict = {repo.full_name: repo.to_dict() for repo in repos}
            
            # Calcula as estatísticas
            aceitos = sum(1 for r in repos_dict.values() if r["accepted"])
            rejeitados = len(repos_dict) - aceitos
            
            print(f"\ Resumo de {lang.upper()}:")
            print(f"   - Total únicos analisados: {len(repos_dict)}")
            print(f"   - Aceitos: {aceitos}")
            print(f"   - Rejeitados: {rejeitados}")
            
            # Salva no arquivo isolado
            self.save_language_database(language=lang, data=repos_dict)
            
            registrar_log("COLETA", "FUNIL_DADOS", f"[{lang.upper()}] Analisados: {len(repos_dict)} | Aceitos: {aceitos} | Rejeitados: {rejeitados}")
        registrar_log("COLETA", "CONCLUIDA", "Coleta finalizada com sucesso.")