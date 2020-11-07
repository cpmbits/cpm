from dataclasses import dataclass, field

from cpm.domain.project.compilation_plan import CompilationPlan


@dataclass
class Project:
    build: CompilationPlan
    test: CompilationPlan
    targets: list = field(default_factory=list)
