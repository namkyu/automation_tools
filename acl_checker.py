import signal
import socket
import sys
import threading

class ACL:

    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def command_list(self):
        commands = []
        commands.append("tcp_start_server")
        commands.append("tcp_start_multiple_server")
        commands.append("tcp_send_message")
        commands.append("udp_start_server")
        commands.append("udp_start_multiple_server")
        commands.append("udp_send_message")
        print("==============================================")
        for i, command in enumerate(commands):
            print(str(i), command)
        print("==============================================")
        return commands

    def signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def reflection(self, instance, func_name):
        func = getattr(instance, func_name)
        func()

    def execute(self):
        command_list = self.command_list()
        number = input("please choose command : ")
        command = command_list[int(number)]
        self.reflection(self, command)

    # ================================================
    # TCP
    # ================================================
    def tcp_start_multiple_server(self):
        def start(p):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', int(p)))
            server_socket.listen(0)
            print("tcp server is running!! (port : %s)" % p)
            while True:
                client_socket, addr = server_socket.accept()
                data = client_socket.recv(1024)
                self.print_msg(data.decode(), addr[0], addr[1])

        ports = input("please type ports (comma-separated) : ")
        port_list = ports.split(",")
        for port in port_list:
            threading.Thread(target=start, args=(port.strip(), )).start()

    def tcp_start_server(self):
        port = input("please type port : ")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', int(port)))
        server_socket.listen(0)
        print("tcp server is running!!")
        while True:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            self.print_msg(data.decode(), addr[0], addr[1])

    def tcp_send_message(self):
        ip = input("please type ip : ")
        port = input("please type port : ")
        message = input("please type message : ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, int(port)))
        sock.send(message.encode())

    # ================================================
    # UDP
    # ================================================
    def udp_start_multiple_server(self):
        def start(p):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('0.0.0.0', int(p)))
            print("udp server is running!! (port : %s)" % p)
            while True:
                data, addr = server_socket.recvfrom(1024)
                self.print_msg(data.decode(), addr[0], addr[1])

        ports = input("please type ports (comma-separated) : ")
        port_list = ports.split(",")
        for port in port_list:
            threading.Thread(target=start, args=(port.strip(), )).start()

    def udp_start_server(self):
        port = input("please type port : ")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', int(port)))
        print("udp server is running!!")
        while True:
            data, addr = server_socket.recvfrom(1024)
            self.print_msg(data.decode(), addr[0], addr[1])

    def udp_send_message(self):
        ip = input("please type ip : ")
        port = input("please type port : ")
        message = input("please type message : ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((ip, int(port)))
        sock.send(message.encode())

    # ================================================
    # Common
    # ================================================
    def print_msg(self, msg, ip, port):
        print("---------------------------------------")
        print("client ip :", ip)
        print("client port :", port)
        print("received data :", msg)
        print("---------------------------------------")


# ===========================================
# main
# ===========================================
if __name__ == "__main__":
    acl = ACL()
    acl.execute()
