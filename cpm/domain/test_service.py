class TestService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def run_tests(self, recipe, patterns=[]):
        project = self.project_loader.load()
        if not project.tests:
            raise NoTestsFound()
        recipe.generate(project)
        if not patterns:
            recipe.build_tests()
            recipe.run_all_tests()
        else:
            self.build_matching_tests(recipe, patterns)
            self.run_matching_tests(recipe, patterns)

    def build_matching_tests(self, recipe, patterns):
        tests = list(filter(
            lambda exe: any(pattern in exe for pattern in patterns),
            recipe.test_executables
        ))
        for test in tests:
            recipe.build_test(test)

    def run_matching_tests(self, recipe, patterns):
        tests = list(filter(
            lambda exe: any(pattern in exe for pattern in patterns),
            recipe.test_executables
        ))
        recipe.run_tests(tests)


class NoTestsFound(RuntimeError):
    pass
