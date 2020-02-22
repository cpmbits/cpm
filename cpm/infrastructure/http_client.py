import requests


def post(url, data=None, headers=None, files=None):
    requests.post(url, files=files, data=data, headers=headers)
