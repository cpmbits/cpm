import os
import sys
import docker


class CompilationService(object):
    def __init__(self, project_loader, cmakelists_builder, project_builder):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_builder = project_builder

    def build(self, target='default'):
        project = self.project_loader.load('.')
        self.cmakelists_builder.build(project, target)
        self.project_builder.build(project, target)
    #
    # def build_target(self, target):
    #     project = self.project_loader.load()
    #     image_name = self.image_for_target(project, target)
    #     client = docker.from_env()
    #     try:
    #         client.images.pull(image_name)
    #     except docker.errors.ImageNotFound:
    #         raise DockerImageNotFound(image_name)
    #     except docker.errors.NotFound:
    #         raise DockerImageNotFound(image_name)
    #     container = client.containers.run(
    #         image_name,
    #         'cpm build',
    #         working_dir=f'/{project.name}',
    #         volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
    #         user=f'{os.getuid()}:{os.getgid()}',
    #         detach=True
    #     )
    #     for log in container.logs(stream=True):
    #         sys.stdout.write(log.decode())
    #
    # def image_for_target(self, project, target):
    #     if target in project.targets:
    #         return project.targets[target].properties['image']
    #     else:
    #         return f'cpmbits/{target}'

    def update(self, target='default'):
        project = self.project_loader.load('.')
        self.cmakelists_builder.build(project, target)

    def clean(self):
        project = self.project_loader.load('.')
        self.project_builder.clean(project)


class DockerImageNotFound(RuntimeError):
    def __init__(self, image_name):
        super(DockerImageNotFound, self).__init__()
        self.image_name = image_name
