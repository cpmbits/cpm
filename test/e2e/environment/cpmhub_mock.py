import os
from flask import Flask, request


app = Flask(__name__)
BASE_DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}'


@app.route('/')
def hello():
    return 'hello'


@app.route('/bits/<name>/<version>', methods=['POST', 'GET'])
def get_bit(name, version):
    if request.method == 'GET':
        with open(f'{BASE_DIRECTORY}/samples/{name}_{version}.json') as payload_file:
            payload = payload_file.read()
        return payload
    if request.method == 'POST':
        with open(f'{name}_{version}.json') as payload_file:
            payload_file.write(request.data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
