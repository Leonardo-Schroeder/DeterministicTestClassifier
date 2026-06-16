import re
from langdetect import detect, LangDetectException
from src.config import ALLOWED_LANGUAGES, EXCLUSION_KEYWORDS

# 1. Regex para Caracteres Proibidos
FORBIDDEN_CHARS_REGEX = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7a3\u0400-\u04FF]')

# 2. NOVA OTIMIZAÇÃO: Junta todas as palavras com "OU" (|) em uma única varredura veloz
# Ficará algo como: \b(tutorial|example|learning|...)\b
COMBINED_KEYWORDS = '|'.join(EXCLUSION_KEYWORDS)
EXCLUSION_REGEX = re.compile(rf'\b({COMBINED_KEYWORDS})\b', re.IGNORECASE)

def analyze_repository(repo_data: dict) -> tuple[bool, str, str]:
    desc = repo_data.get("description") or ""
    name = repo_data.get("name") or ""
    full_text = f"{name} {desc}".lower()

    # Passa 1: Varredura de caracteres proibidos (O(N))
    forbidden_match = FORBIDDEN_CHARS_REGEX.search(full_text)
    if forbidden_match:
        return False, "Idioma não suportado (Caracteres Asiáticos/Cirílicos)", f"Caractere: '{forbidden_match.group()}'"

    # Passa 2: Varredura OTIMIZADA de palavras-chave (O(N) - Varre o texto 1 vez só!)
    keyword_match = EXCLUSION_REGEX.search(full_text)
    if keyword_match:
        return False, "Projeto com fins didáticos", f"Palavra-chave: '{keyword_match.group(1)}'"

    # Passa 3: Detecção de Idioma Estatística
    # Aumentamos para 40 caracteres. Textos menores que isso contendo jargões técnicos
    # (ex: "Spring Framework") confundem a biblioteca estatística.
    # Obs: Como o Passa 1 já bloqueia Russo e Chinês via Regex, é seguro deixar descrições curtas passarem.
    if len(desc.strip()) > 40: 
        try:
            lang = detect(desc)
            if lang not in ALLOWED_LANGUAGES:
                return False, "Idioma da descrição não permitido", f"Idioma detectado: '{lang}'"
        except LangDetectException:
            pass # Se a biblioteca falhar totalmente, deixamos passar por garantia.

    # Se chegou aqui, é um projeto válido!
    return True, "Aprovado", "Passou em todos os critérios"