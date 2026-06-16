from dataclasses import dataclass
from typing import List, Dict
from src.Analyzer.models.enums import TestGroup

@dataclass
class TestCaseAnalysis:
    method_name: str
    file_path: str
    group: TestGroup
    has_assertions: bool
    is_component_trait: bool
    justification: str

@dataclass
class ProjectReport:
    project_name: str
    language: str
    total_tests: int
    group_percentages: Dict[str, float]
    analyzed_cases: List[TestCaseAnalysis]