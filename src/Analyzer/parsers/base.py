import zipfile
from abc import ABC, abstractmethod
from typing import List
from src.Analyzer.models.ast_data import ASTContext

class BaseASTParser(ABC):
    @abstractmethod
    def extract(self, zip_path: str) -> List[ASTContext]:
        """Extrai o contexto da AST de todos os métodos de teste de um ZIP."""
        pass
        
    def _is_valid_zip(self, zip_path: str) -> bool:
        return zipfile.is_zipfile(zip_path)