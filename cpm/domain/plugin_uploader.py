from cpm.infrastructure import http_client


class PluginUploader(object):
    def __init__(self, auth_token='', repository_url='https://www.cpm-hub.com/plugins'):
        self.repository_url = repository_url
        self.auth_token = auth_token

    def upload(self, file_name):
        data = {
            'token': self.auth_token,
        }
        files = {
            'file': open(file_name, 'rb')
        }

        http_client.post(self.repository_url, files=files, data=data)


class AuthenticationFailure(RuntimeError):
    pass
