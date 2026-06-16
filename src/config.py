import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else ""
}

# String base padronizada para todas as linguagens
BASE_SEARCH_QUERY = "stars:>1000 pushed:>2024-01-01"

# Lista de linguagens que o nosso coletor vai rodar
TARGET_LANGUAGES = ["java", "python"]

# Palavras-chave de exclusão
EXCLUSION_KEYWORDS = [
    "tutorial", "example", "learning", "study", "course", 
    "roadmap", "interview", "awesome", "bootcamp", "exercises",
    "exemplo", "estudo", "curso", "didático",
    "sandbox", "demo", "practice", "prática"
]

# "aprendizado" - tirei essa palavra para evitar tirar projetos de aprendizado de máquina

ALLOWED_LANGUAGES = ['en', 'pt']