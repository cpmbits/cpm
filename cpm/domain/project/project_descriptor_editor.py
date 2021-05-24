from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE
from cpm.infrastructure import filesystem


def update(directory, project_descriptor, params):
    stream = StringIO()
    project_descriptor.yaml_document.update(params)
    yaml = YAML()
    yaml.dump(project_descriptor.yaml_document, stream=stream)
    yaml_payload = stream.getvalue()
    filesystem.write_file(f'{directory}/{PROJECT_DESCRIPTOR_FILE}', yaml_payload)
