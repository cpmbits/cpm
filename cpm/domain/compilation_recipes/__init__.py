RECIPES_DIRECTORY = 'recipes'


class CompilationRecipe(object):
    def generate(self, project):
        raise NotImplementedError()

    def compile(self, project):
        raise NotImplementedError()


class CompilationError(RuntimeError):
    pass
