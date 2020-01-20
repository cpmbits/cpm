from cpm.domain.compilation_recipes import CompilationRecipe
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

CMAKE_RECIPE = (
    'set(PROJECT_NAME {project_name})\n'
    'project(${{NAME}})\n'
    'add_executable(${{NAME}} {sources_list})\n'
    'add_custom_command(\n'
    '    TARGET ${{NAME}}\n'
    '    POST_BUILD\n'
    '    COMMAND COMMAND ${{CMAKE_COMMAND}} - E copy $ <TARGET_FILE:${{NAME}}> ${{PROJECT_SOURCE_DIR}}/${{NAME}}\n'
    ')\n'
)


class BuildRecipe(CompilationRecipe):
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def generate(self, project):
        self.filesystem.create_directory(f'{RECIPES_DIRECTORY}/build')
        self.filesystem.create_file(
            f'{RECIPES_DIRECTORY}/build/CMakeLists.txt',
            CMAKE_RECIPE.format(
                project_name=project.name,
                sources_list=' '.join(project.sources)
            )
        )

    def compile(self, project):
        pass

