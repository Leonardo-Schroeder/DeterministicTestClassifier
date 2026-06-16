from ast import List
from dataclasses import dataclass, field
from typing import Set

@dataclass(frozen=True)
class MethodInvocation:
    """Representa uma chamada real na AST, amarrada ao seu tipo/pacote."""
    caller_type: str  # Ex: 'java.sql.Connection', 'org.elasticsearch.cluster.Node' ou 'UNKNOWN'
    method_name: str  # Ex: 'commit', 'start'

@dataclass
class ASTContext:
    method_name: str
    file_path: str
    invocations: Set[MethodInvocation] = field(default_factory=set) # Agora rastreamos a invocação tipada
    mocked_types: Set[str] = field(default_factory=set) # Mocks também ganham rastreio (ex: mockamos uma interface de domínio ou de I/O?)
    imported_libs: Set[str] = field(default_factory=set)
    class_annotations: List[str] = field(default_factory=list)
    parent_class: str = ""