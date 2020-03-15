from dataclasses import dataclass


@dataclass
class PluginDownload:
    plugin_name: str
    version: str
    payload: str
