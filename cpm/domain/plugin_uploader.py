from cpm.infrastructure import http_client


class PluginUploader(object):
    def __init__(self, auth_token=''):
        self.auth_token = auth_token

    def upload(self, file_name):
        data = {
            'token': self.auth_token,
        }
        files = {
            'file': open(file_name, 'rb')
        }

        http_client.post('https://www.cpm-hub.com/plugins', files=files, data=data)


class AuthenticationFailure(RuntimeError):
    pass
