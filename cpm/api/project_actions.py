from cpm.domain.project.project_loader import ProjectLoader
from cpm.domain.project.project_descriptor_parser import NotACpmProject


def discover_project_actions():
    project_loader = ProjectLoader()

    try:
        project = project_loader.load('.')
        return project.actions
    except NotACpmProject:
        return []
