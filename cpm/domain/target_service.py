from cpm.domain import target


class TargetService:
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def add_target(self, target_name):
        project = self.project_loader.load()
        project.add_target(target.Target(target_name))
        self.project_loader.save(project)
