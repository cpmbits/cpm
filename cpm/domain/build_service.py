class BuildService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def build(self, cmake_recipe):
        project = self.project_loader.load()
        cmake_recipe.generate(project)
        cmake_recipe.build(project)

    def update(self, cmake_recipe):
        project = self.project_loader.load()
        cmake_recipe.generate(project)

    def clean(self, cmake_recipe):
        self.project_loader.load()
        cmake_recipe.clean()

