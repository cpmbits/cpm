from dataclasses import dataclass, field


@dataclass
class DeclaredBit:
    name: str
    version: str


@dataclass
class Package:
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
    include_directories: list = field(default_factory=list)
    targets: list = field(default_factory=list)     # TODO: Targets

# yaml --load--> parsed yaml --parse--> project plan --digest--> project
