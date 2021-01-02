import threading
import pytest

from test.e2e.environment import cpmhub_mock
from cpm.infrastructure import http_client
from werkzeug.serving import make_server


server = None


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 8000, cpmhub_mock.app)
        self.ctx = cpmhub_mock.app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def start_server():
    global server
    server = ServerThread()
    server.start()


def stop_server():
    global server
    server.shutdown()


@pytest.fixture(scope="module", autouse=True)
def start_core_mock():
    start_server()
    __wait_for_server()
    yield
    stop_server()


def __wait_for_server():
    alive = False
    while not alive:
        try:
            http_client.get('http://localhost:8000/')
            alive = True
        except Exception as e:
            pass
