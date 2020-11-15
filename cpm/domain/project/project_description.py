from dataclasses import dataclass, field


@dataclass
class DeclaredBit:
    name: str
    version: str


@dataclass
class PackageDescription:
    path: str
    cflags: list = field(default_factory=list)
    sources: list = field(default_factory=list)


@dataclass
class CompilationPlan:
    bits: list = field(default_factory=list)
    packages: list = field(default_factory=list)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)


@dataclass
class ProjectInformation:
    name: str = ''
    version: str = ''
    description: str = ''


@dataclass
class TargetDescription:
    name: str
    image: str = ''
    main: str = 'main.cpp'
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)


@dataclass
class ProjectDescription:
    name: str = ''
    version: str = ''
    description: str = ''
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)
    targets: dict = field(default_factory=dict)
