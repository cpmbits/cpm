import os
import sys
import docker


class CompilationService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def build(self, cmake_recipe):
        project = self.project_loader.load()
        cmake_recipe.generate(project)
        cmake_recipe.build(project)

    def build_target(self, target):
        project = self.project_loader.load()
        client = docker.from_env()
        container = client.containers.run(
            f'cpmbits/{target}',
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )
        for log in container.logs(stream=True):
            sys.stdout.write(log.decode())

    def update(self, cmake_recipe):
        project = self.project_loader.load()
        cmake_recipe.generate(project)

    def clean(self, cmake_recipe):
        self.project_loader.load()
        cmake_recipe.clean()
