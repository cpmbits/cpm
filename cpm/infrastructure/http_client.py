from dataclasses import dataclass
from urllib3.exceptions import InsecureRequestWarning
import requests


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

@dataclass
class HttpResponse:
    status_code: int
    body: str


def post(url, data=None, headers=None, files=None):
    try:
        response = requests.post(url, files=files, data=data, headers=headers, verify=False)
        return HttpResponse(response.status_code, response.text)
    except requests.exceptions.ConnectionError as e:
        raise HttpConnectionError()


def put(url, data=None, headers=None, files=None):
    requests.put(url, files=files, data=data, headers=headers, verify=False)


def get(url, data=None, headers=None, files=None):
    try:
        response = requests.get(url, files=files, data=data, headers=headers, verify=False)
        return HttpResponse(response.status_code, response.text)
    except requests.exceptions.ConnectionError:
        raise HttpConnectionError(url)


class HttpConnectionError(RuntimeError):
    pass
