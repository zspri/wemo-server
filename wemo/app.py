from flask import Flask, jsonify, request
from os import getenv
from .utils import http, discover, misc

app = Flask(__name__)
app.debug = False
app.discovery_worker = None


@app.before_request
def before_request():
    if request.headers.get('Authorization') != getenv('DEFAULT_AUTH_KEY'):
        return jsonify(error='Authentication required'), 401


@app.route('/devices')
def get_devices():
    return jsonify(
        devices=app.discovery_worker.devices,
        _last_update=app.discovery_worker.last_update)


@app.route('/devices/<device_hash>', methods=['GET', 'PATCH'])
def get_device(device_hash):
    host = misc.find_host_by_hash(app.discovery_worker.devices, device_hash)
    if host is None:
        return jsonify(error='Device not found'), 404
    if request.method == 'GET':
        # implements GetFriendlyName, GetBinaryState
        return jsonify(host)
    elif request.method == 'PATCH':
        # implements SetBinaryState
        try:
            stat = int(request.args['state'])
            assert stat in [0, 1]
            ev = http.set_state(host['device'], stat)
            app.discovery_worker.devices = misc.force_update_devices(app.discovery_worker.devices, host['hash'], ev)
            return jsonify(state=ev)
        except KeyError:
            return jsonify(error='State parameter required'), 400
        except ValueError as e:
            return jsonify(error=f'State must be an integer ({e})'), 400
        except AssertionError:
            return jsonify(error='State must either be 0 or 1'), 400


def start():
    app.discovery_worker = discover.DiscoveryWorker()
    app.discovery_worker.run()

    app.run('0.0.0.0', port=80)
