from cpm.api.result import Result
from cpm.api.result import FAIL
from cpm.domain.install_service import PluginNotFound
from cpm.domain.project_loader import NotAChromosProject


def install_plugin(install_service, plugin):
    try:
        install_service.install(plugin)
    except NotAChromosProject:
        return Result(FAIL, 'not a Chromos project')
    except PluginNotFound:
        return Result(FAIL, f'plugin {plugin} not found in CPM Hub')
