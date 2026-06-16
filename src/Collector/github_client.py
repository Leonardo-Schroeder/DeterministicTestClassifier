import time
import requests
from src.config import HEADERS
from src.models import Repository
from .filters import analyze_repository

class GitHubClient:
    BASE_URL = "https://api.github.com/search/repositories"

    def fetch_repositories(self, language: str, query: str, max_pages: int = 5) -> list[Repository]:
        all_repos = []
        
        print(f"\nColetando repositórios para: {language.upper()}")
        print(f"Query executada: {query}")
        
        for page in range(1, max_pages + 1):
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": page
            }
            
            # Sistema de Retries
            sucesso_na_pagina = False
            max_retries = 3
            
            for tentativa in range(1, max_retries + 1):
                response = requests.get(self.BASE_URL, headers=HEADERS, params=params)
                
                if response.status_code == 200:
                    sucesso_na_pagina = True
                    items = response.json().get("items", [])
                    if not items:
                        print(f"Fim dos resultados na página {page}.")
                        break # Fim absoluto dos resultados
                    
                    for item in items:
                        is_accepted, reason, evidence = analyze_repository(item)
                        
                        repo = Repository(
                            name=item["name"],
                            full_name=item["full_name"],
                            html_url=item["html_url"],
                            description=item["description"] or "Sem descrição",
                            language=language,
                            stars=item["stargazers_count"],
                            default_branch=item["default_branch"],
                            accepted=is_accepted,
                            rejection_reason=reason,
                            rejection_evidence=evidence
                        )
                        all_repos.append(repo)
                    
                    print(f"Página {page} processada. Analisados {len(all_repos)} projetos até agora...")
                    time.sleep(3) # Pausa amigável padrão de 3s
                    break # Sai do loop de tentativas, pois deu certo!
                    
                elif response.status_code in [500, 502, 503, 504]:
                    print(f"Servidor do GitHub instável (Erro {response.status_code}). Tentativa {tentativa}/{max_retries}...")
                    time.sleep(5 * tentativa) # Espera 5s, depois 10s, depois 15s...
                    
                elif response.status_code == 403:
                    print(f"Rate Limit atingido (Erro 403). Verifique o seu GITHUB_TOKEN.")
                    print(response.json())
                    break # Rate limit não resolve tentando de novo rápido, melhor parar.
                    
                else:
                    print(f"Erro na API (Status {response.status_code}): {response.text}")
                    break
            
            # Se tentou 3 vezes e falhou, ou se a página veio vazia de propósito
            if not sucesso_na_pagina and response.status_code != 200:
                print(f"Desistindo da página {page} após {max_retries} tentativas.")
                break # Interrompe a coleta para esta linguagem
                
        return all_repos