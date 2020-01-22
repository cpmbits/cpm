from cpm.domain.compilation_recipes import RECIPES_DIRECTORY


class CleanService(object):
    def __init__(self, filesystem, project_loader):
        self.project_loader = project_loader
        self.filesystem = filesystem

    def clean(self):
        self.project_loader.load()
        if not self.filesystem.directory_exists(RECIPES_DIRECTORY):
            return
        self.filesystem.remove_directory(RECIPES_DIRECTORY)
