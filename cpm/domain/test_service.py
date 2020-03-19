class TestService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def run_tests(self, recipe, patterns=[]):
        project = self.project_loader.load()
        if not project.tests:
            raise NoTestsFound()
        recipe.generate(project)
        recipe.build_tests()
        if not patterns:
            recipe.run_tests()
        else:
            self.run_matching_tests(recipe, patterns)

    def run_matching_tests(self, recipe, patterns):
        tests = filter(
            lambda exe: any(pattern in exe for pattern in patterns),
            recipe.executables
        )
        for test in tests:
            recipe.run_test(test)


class NoTestsFound(RuntimeError):
    pass
