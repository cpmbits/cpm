from dataclasses import dataclass


@dataclass
class TemplateDownload:
    template_name: str
    version: str
    payload: str
