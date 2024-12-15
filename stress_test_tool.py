#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import re
import signal
import sys
import threading
import time

import paramiko
import requests


class StressTestTool:
    command_cpu_test = 'stress-ng -c {} --verify -v --timeout {}s'
    command_memory_test = 'stress-ng --vm 2 --vm-bytes {}G --verify -v --timeout {}s'
    command_network_test = 'stress-ng --class network --all 1 --timeout {}s'
    for_test_command = 'echo hello'

    def __init__(self, timeout, test_mode):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.timeout = timeout
        self.server_info = json.load(open("servers.json"))
        self.servers = self.server_info.get("servers")
        self.test_mode = test_mode

    @staticmethod
    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        return type('Enum', (), enums)

    def command_list(self):
        commands = ["cpu_test", "memory_test", "network_test"]
        print("\n")
        print("==============================================")
        for i, command in enumerate(commands):
            print(str(i) + " : ", command)
        print("==============================================")
        return commands

    def server_list(self):
        print("\n")
        print("==============================================")
        for i, server in enumerate(self.servers):
            print("%s : %s (%s)" % (str(i), server["ip"], server["host"]))
        print("==============================================")
        choice_numbers = self.input_text("테스트할 서버를 지정해 주세요. (콤마구분)")

        choice_servers = []
        for index in choice_numbers.split(","):
            server = self.servers[int(index)]
            choice_servers.append(server)
        self.servers = choice_servers

    def cpu_test(self):
        self.server_list()
        command = self.choose_command(self.command_cpu_test)
        self.execute_test(command, Action.CPU)

    def memory_test(self):
        self.server_list()
        command = self.choose_command(self.command_memory_test)
        self.execute_test(command, Action.MEMORY)

    def network_test(self):
        self.server_list()
        command = self.choose_command(self.command_network_test)
        self.execute_test(command, Action.NETWORK)

    def choose_command(self, command):
        if self.test_mode == 'Y':
            return self.for_test_command
        return command

    def execute_test(self, cmd, enum_action):
        # 검증
        threading.Thread(target=lambda: self.request_server()).start()

        for server in self.servers:
            ip = server["ip"]
            user = server["user"]
            password = server["password"]
            load_test_cpu = server["load_test_cpu"]
            load_test_memory = server["load_test_memory"]
            n_cmd = None

            if enum_action == Action.CPU:
                n_cmd = cmd.format(load_test_cpu, self.timeout)
            elif enum_action == Action.MEMORY:
                n_cmd = cmd.format(load_test_memory, self.timeout)
            elif enum_action == Action.NETWORK:
                n_cmd = cmd.format(self.timeout)

            print(n_cmd)
            threading.Thread(target=lambda: self.connect_ssh(ip, user, password, n_cmd)).start()

    def connect_ssh(self, ip, user, password, cmd):
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        cli.connect(ip, port=22, username=user, password=password)
        stdin, stdout, stderr = cli.exec_command(cmd)
        lines = stdout.readlines()
        print(''.join(lines))
        cli.close()

    def request_server(self):
        while True:
            janus_server_url = self.server_info.get("janus_manager_server_url")
            response = requests.get(janus_server_url)
            response = response.json()

            data = response["data"]
            host_name = data["janusHostName"]
            server_name = data["janusServerName"]
            public_ip = data["janusServerPublicIp"]
            request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("%s => host : %s, server : %s, publicIp : %s" % (request_time, host_name, server_name, public_ip))
            time.sleep(5)

    def only_number(self, str):
        return re.match("[0-9]", str)

    def input_text(self, text):
        show_text = text + " : "
        return input(show_text)

    def signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def reflection(self, instance, func_name):
        func = getattr(instance, func_name)
        func()

    def execute(self):
        command_list = self.command_list()
        number = self.input_text("부하 테스트 명령어를 선택해 주세요.")
        if self.only_number(number):
            command = command_list[int(number)]
            self.reflection(self, command)


# ======================================
# main
# ======================================
if __name__ == "__main__":
    argument_len = len(sys.argv)
    if argument_len < 3:
        print("necessary parameters!!")
        sys.exit()

    arg_timeout = sys.argv[1]
    arg_test_mode = sys.argv[2]

    Action = StressTestTool.enum('CPU', 'MEMORY', 'NETWORK')
    stress = StressTestTool(arg_timeout, arg_test_mode)
    stress.execute()
