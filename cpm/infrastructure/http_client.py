from dataclasses import dataclass
import requests


@dataclass
class HttpResponse:
    status_code: int
    body: str


def post(url, data=None, headers=None, files=None):
    requests.post(url, files=files, data=data, headers=headers)


def put(url, data=None, headers=None, files=None):
    requests.put(url, files=files, data=data, headers=headers)


def get(url, data=None, headers=None, files=None):
    response = requests.get(url, files=files, data=data, headers=headers)
    return HttpResponse(response.status_code, response.text)
