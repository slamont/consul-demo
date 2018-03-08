import json
from time import sleep

import socket
import random
import base64

import requests
from flask import Flask
app = Flask(__name__)
hostname = socket.gethostname()

servers = ['consul1','consul2','consul3']
server = random.choice(servers)
BASE_CONSUL_URL = 'http://{consul}:8500'.format(consul=server)

PORT = 8080

@app.route('/')
def home():
    try:
        d = get_kv()
        value = base64.b64decode(d[0].get('Value')).decode('utf-8')
        msg = 'Hello ' + value
    except:
        msg = 'Hello World!'
    return msg


@app.route('/health')
def hello_world():
    data = {
        'status': 'healthy'
    }
    return json.dumps(data)


def register():
    url = BASE_CONSUL_URL + '/v1/agent/service/register'
    data = {
        'name': 'PythonApp',
        'address': hostname,
        'check': {
            'http': 'http://{host}:{port}/health'.format(host=hostname,port=PORT),
            'interval': '10s'
        }
    }
    res = requests.put(
        url,
        data=json.dumps(data)
    )
    print("CONTENT OF REQUEST: {status} {content}".format(status=res.status_code, content=(url, data)))
    return res.text


def get_kv():
    url = BASE_CONSUL_URL + '/v1/kv/'
    try:
        response = requests.get(url + hostname)
        return response.json()
    except:
        return '{}'

if __name__ == '__main__':
    sleep(8)
    try:
        print(register())
        print("Registered")
    except:
        print("Failed to register with {consul_server}".format(consul_server=server))
        pass
    app.debug = False
    app.run(host="0.0.0.0", port=PORT)
