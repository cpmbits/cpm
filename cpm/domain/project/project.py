from dataclasses import dataclass, field

from cpm.domain.project.compilation_plan import CompilationPlan


@dataclass
class ProjectInformation:
    name: str = ''
    version: str = ''
    description: str = ''


@dataclass
class Target:
    name: str
    image: str = ''
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)


@dataclass
class Project:
    name: str = ''
    version: str = ''
    description: str = ''
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)
    targets: dict = field(default_factory=dict)
