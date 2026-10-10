from dataclasses import dataclass, field

@dataclass(frozen=True)
class MethodInvocation:
    """Representa uma chamada real na AST, amarrada ao seu tipo/pacote."""
    caller_type: str  # Ex: 'java.sql.Connection', 'org.elasticsearch.cluster.Node' ou 'UNKNOWN'
    method_name: str  # Ex: 'commit', 'start'

@dataclass
class ASTContext:
    method_name: str
    file_path: str
    invocations: set[MethodInvocation] = field(default_factory=set)
    mocked_types: set[str] = field(default_factory=set)
    imported_libs: set[str] = field(default_factory=set)
    class_annotations: list[str] = field(default_factory=list)
    parent_class: str = ""