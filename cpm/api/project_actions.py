from cpm.domain.project_loader_v1 import ProjectLoader
from cpm.domain.project_loader_v1 import NotACpmProject
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def discover_project_actions():
    filesystem = Filesystem()
    project_loader = ProjectLoader(YamlHandler(filesystem), filesystem)

    try:
        project = project_loader.load()
        return project.actions
    except NotACpmProject:
        return []
