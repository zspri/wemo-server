"""
Copyright (c) 2014, Ian McCracken
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

* Neither the name of ouimeaux nor the names of its contributors may be used to
endorse or promote products derived from this software without specific prior
written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import multiprocessing
import socket

from typing import Type
from .http import get_device


class Worker(multiprocessing.Process):
    _END_OF_STREAM = None

    def __init__(self, request_queue: multiprocessing.Queue, response_queue=multiprocessing.Queue):
        super().__init__()
        self.request_queue = request_queue
        self.response_queue = response_queue

    def send_stop(self):
        self.request_queue.put(self._END_OF_STREAM)

    def process_response(self, resp):
        self.response_queue.put(resp)


class Workers:
    def __init__(self, n_workers: int, worker_type: Type[Worker], *args, **kwargs):
        self.request_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        self._workers = [worker_type(self.request_queue, self.response_queue,
            *args, **kwargs) for _ in range(n_workers)]

    def start(self):
        for wrk in self._workers:
            wrk.start()

    def put(self, msg):
        self.request_queue.put(msg)

    def wait(self) -> list:
        while self._workers:
            for i, wrk in enumerate(self._workers):
                if not self._workers[i].is_alive():
                    self._workers.pop(i)
                    break

        ret = []
        while not self.response_queue.empty():
            ret.append(self.response_queue.get())
        return ret

    def send_stop(self):
        for wrk in self._workers:
            wrk.send_stop()


class ScanWorker(Worker):
    def __init__(self, request_queue: multiprocessing.Queue, response_queue: multiprocessing.Queue,
                 scan_timeout: float, connect_timeout: float, port: int = 49153):
        super().__init__(request_queue, response_queue)
        self.scan_timeout = scan_timeout
        self.connect_timeout = connect_timeout
        self.port = port

    def run(self):
        while True:
            addr = self.request_queue.get()
            if addr == self._END_OF_STREAM:
                break

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.scan_timeout)
                sock.connect((addr, self.port))
                sock.close()
                dev = get_device(f'{addr}:{self.port}')
                print('Found WeMo device: {}'.format(dev))
                self.process_response(dev)
            except OSError:
                pass
