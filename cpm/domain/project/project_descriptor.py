from dataclasses import dataclass, field


@dataclass
class DeclaredBit:
    name: str
    version: str
    target: str = ''
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)


@dataclass
class PackageDescription:
    path: str
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    sources: list = field(default_factory=list)


@dataclass
class CompilationPlan:
    declared_bits: list = field(default_factory=list)
    bits: dict = field(default_factory=dict)
    packages: list = field(default_factory=list)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)
    includes: set = field(default_factory=set)


@dataclass
class ProjectInformation:
    name: str = ''
    version: str = ''
    description: str = ''


@dataclass
class TargetDescription:
    name: str
    main: str = 'main.cpp'
    format: str = 'binary'
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)
    post_build: list = field(default_factory=list)
    dockerfile: str = ''
    image: str = ''
    test_image: str = ''
    test_dockerfile: str = ''
    toolchain_prefix: str = ''


@dataclass
class ProjectDescriptor:
    name: str = ''
    version: str = ''
    description: str = ''
    schema: str = '1.0'
    yaml_document: object = None
    build: CompilationPlan = field(default_factory=CompilationPlan)
    test: CompilationPlan = field(default_factory=CompilationPlan)
    declared_bit: DeclaredBit = None
    targets: dict = field(default_factory=dict)

    def build_packages(self):
        return self.build.packages + [package for target, description in self.targets.items() for package in description.build.packages]
