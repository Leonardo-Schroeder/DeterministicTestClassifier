from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Repository:
    name: str
    full_name: str
    html_url: str
    description: str
    language: str
    stars: int
    default_branch: str
    
    # Campos pós análise inicial
    accepted: bool = False
    rejection_reason: Optional[str] = None
    rejection_evidence: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)