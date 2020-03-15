from dataclasses import dataclass
import requests


@dataclass
class HttpResponse:
    status_code: int
    body: str


def post(url, data=None, headers=None, files=None):
    try:
        requests.post(url, files=files, data=data, headers=headers)
    except requests.exceptions.ConnectionError:
        raise HttpConnectionError()


def put(url, data=None, headers=None, files=None):
    requests.put(url, files=files, data=data, headers=headers)


def get(url, data=None, headers=None, files=None):
    try:
        response = requests.get(url, files=files, data=data, headers=headers)
        return HttpResponse(response.status_code, response.text)
    except requests.exceptions.ConnectionError:
        raise HttpConnectionError()


class HttpConnectionError(RuntimeError):
    pass
