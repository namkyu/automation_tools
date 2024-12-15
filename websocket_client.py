#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import binascii
import http.client as http_client
import random
import signal
import socket
import string
import sys
import time
from threading import Thread

import requests


class WebSocketClient(Thread):
    transport = "websocket"
    host = "localhost"
    port = 8080
    endpoint = ""

    def __init__(self, endpoint, host="localhost", port=8080):
        self.endpoint = endpoint
        self.host = host
        self.port = port
        Thread.__init__(self)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def random_str(self, length):
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for c in range(length))

    def connect(self):
        self.get_socket_info()
        self.start()

    # ==========================================
    # info 조회
    # ==========================================
    def get_socket_info(self):
        conn = 0
        try:
            conn = http_client.HTTPConnection(self.host, self.port)
            conn.request('GET', self.endpoint + '/info')
            response = conn.getresponse()
            print("INFO", response.status, response.reason, response.read())
        finally:
            if not conn:
                conn.close()

    # ==========================================
    # run thread for connection websocket with sockJS
    # ==========================================
    def run(self):
        conn = http_client.HTTPConnection(self.host, self.port)
        server_id = str(random.randint(0, 1000))
        conn_id = self.random_str(8)
        url = '/'.join([self.endpoint, server_id, conn_id, self.transport])

        raw_key = bytes(random.getrandbits(8) for _ in range(16))
        key = base64.b64encode(raw_key).decode()

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Version': 13,
            'Sec-WebSocket-Key': key
        }

        print("==============================================")
        print("Connecting to URL :", url)
        conn.request('GET', url, headers=headers)
        response = conn.getresponse()
        print("connected :", response.status)
        print("==============================================")

        # 소켓의 파일 번호
        file_no = response.fileno()
        # file descriptor 를 통해 python socket 생성
        # AF_INET : IP4v 사용, SOCK_STREAM : 스트림소켓 사용
        sock = socket.fromfd(file_no, socket.AF_INET, socket.SOCK_STREAM)

        while True:
            data = sock.recv(1)  # received one byte
            b = bytearray(data)
            readable_data = binascii.hexlify(b)

            # print("received byte data : %s, readable data : %s" % (data, readable_data))
            if data == b'o':
                print(">> Socket connected")
            if data == b'c':
                print(">> Socket disconnected")
                return
            if data == b'h':
                pass
            if data in (b'm', b'a'):
                msg = sock.recv(1000)
                print(">> Message: ", msg)

def monitor_websocket_stat(url):
    while True:
        response = requests.get(url)
        print(response.text)
        time.sleep(5)


# ===========================================
# main
# ===========================================
if __name__ == "__main__":

    argument_len = len(sys.argv)
    if argument_len != 6:
        print("invalid argument length !!")
        sys.exit(1)

    param_endpoint = sys.argv[1]
    param_host = sys.argv[2]
    param_port = sys.argv[3]
    param_max_connect_socket = int(sys.argv[4])
    param_url = sys.argv[5]

    print("==============================================")
    print("Arguments")
    print("==============================================")
    print("endpoint :", param_endpoint)
    print("host :", param_host)
    print("port :", param_port)
    print("max_connect_socket :", param_max_connect_socket)
    print("url :", param_url)

    for i in range(0, param_max_connect_socket):
        client = WebSocketClient(param_endpoint, param_host, param_port)
        client.connect()
        time.sleep(0.1)