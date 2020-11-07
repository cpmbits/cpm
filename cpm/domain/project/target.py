from dataclasses import dataclass

from cpm.domain.project.compilation_plan import CompilationPlan


@dataclass
class Target:
    name: str
    build: CompilationPlan
    test: CompilationPlan
