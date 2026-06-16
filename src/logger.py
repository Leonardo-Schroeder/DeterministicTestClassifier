import os
from datetime import datetime

def registrar_log(etapa: str, status: str, detalhes: str = ""):
    """Salva um registro de execução no arquivo data/pipeline.log"""
    pasta_logs = "data"
    os.makedirs(pasta_logs, exist_ok=True)
    caminho_log = os.path.join(pasta_logs, "pipeline.log")
    
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensagem = f"[{agora}] {etapa.upper()} | Status: {status} | {detalhes}\n"
    
    with open(caminho_log, "a", encoding="utf-8") as arquivo:
        arquivo.write(mensagem)