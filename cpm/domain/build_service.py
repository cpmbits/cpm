class BuildService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def build(self, compilation_recipe):
        project = self.project_loader.load()
        compilation_recipe.generate(project)
        compilation_recipe.compile(project)
