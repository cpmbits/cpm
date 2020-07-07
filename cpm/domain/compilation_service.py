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
        image = self.image_for_target(project, target)
        client = docker.from_env()
        container = client.containers.run(
            image,
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )
        for log in container.logs(stream=True):
            sys.stdout.write(log.decode())

    def image_for_target(self, project, target):
        if target in project.targets:
            return project.targets[target].properties['image']
        else:
            return f'cpmbits/{target}'

    def update(self, cmake_recipe):
        project = self.project_loader.load()
        cmake_recipe.generate(project)

    def clean(self, cmake_recipe):
        self.project_loader.load()
        cmake_recipe.clean()
