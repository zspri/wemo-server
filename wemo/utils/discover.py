import ipaddress
import time

from os import getenv
from threading import Thread
from . import worker


def get_devices():
    print('Finding WeMo devices...')
    workers = worker.Workers(10, worker.ScanWorker, scan_timeout=2, connect_timeout=30, port=49153)
    workers.start()

    for addr in ipaddress.IPv4Network(getenv('NET_SPACE')):
        workers.put(addr.exploded)

    workers.send_stop()
    devices = workers.wait()
    print(f'Found {len(devices)} device(s)')
    return devices


class DiscoveryWorker:
    def __init__(self):
        self.devices = []
        self.thread = None
        self.last_update = None

    def _loop(self):
        while True:
            self.devices = get_devices()
            self.last_update = time.time()
            time.sleep(20)

    def run(self):
        t = Thread(target=self._loop, daemon=True)
        t.start()
        self.thread = t
