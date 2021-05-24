from dataclasses import dataclass


@dataclass
class ProjectTemplate:
    name: str
    version: str
    payload: str
