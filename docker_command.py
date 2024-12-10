#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import signal
import subprocess
import sys

from common.common_service import CommonService


class DockerCommand(CommonService):
    DOCKER_PS = 'docker ps -a --format "{{.ID}}\t{{.Names}}"'

    def __init__(self):
        print("This is very easy to use the docker command.")
        signal.signal(signal.SIGINT, self.__signal_handler)

    def command_list(self):
        commands = []
        commands.append("docker_ps")
        commands.append("version")
        commands.append("create_container")
        commands.append("start_container")
        commands.append("execute_command_in_container")
        commands.append("logs_container")
        commands.append("stop_container")
        commands.append("restart_container")
        commands.append("remove_container")
        commands.append("remove_all_container")
        commands.append("build_image")
        commands.append("remove_image")
        commands.append("remove_all_dangling_image")
        commands.append("network_inspect")
        commands.append("show_all_container_info")
        commands.append("docker_compose_up")
        commands.append("docker_compose_start")
        commands.append("docker_compose_stop")
        commands.append("docker_history")
        commands.append("docker_inspect")
        commands.append("make_image")

        self._print_table(["num", "command"], commands)
        return commands

    def get_docker_ps(self, **kwargs):
        ps_arr = []
        ps_arr.append('docker ps -a')
        ps_arr.append(' --format "{{.ID}}\t{{.Names}}"')

        filters = kwargs.get("filters")
        if filters is not None:
            ps_arr.append(" ")
            ps_arr.append(filters)

        return "".join(ps_arr)

    # ==============================================
    # 정보 확인
    # ==============================================
    def info(self):
        output = self.__process("docker info")
        print(output)

    # ==============================================
    # 버전
    # ==============================================
    def version(self):
        output = self.__process("docker version")
        print(output)

    # ==============================================
    # 컨테이너 생성
    # ==============================================
    def create_container(self):
        base_image = self.__print_command_result('docker images --format "{{.Repository}}:{{.Tag}}"')
        container_name = self.__input_text("container name")

        execute_command = []
        execute_command.append("docker run -dit")
        execute_command.append("--name %s" % container_name)

        answer = self.__input_text("Would you like to use the host network mode for a container? (y or n)")
        if answer == 'y':
            execute_command.append("--network host")
        else:
            answer = self.__input_text("Would you like to publish a container's port to the host? (y or n)")
            if answer == 'y':
                port_list = []
                while True:
                    container_port = self.__input_text("container's port")
                    host_port = self.__input_text("host port")
                    port_list.append("-p %s:%s" % (host_port, container_port))
                    answer = self.__input_text("Add more port? (y or n)")
                    if answer == 'n':
                        break
                execute_command.append(" ".join(port_list))

        answer = self.__input_text("Would you like to attach a volume? (y or n)")
        if answer == 'y':
            host_path = self.__input_text("host path")
            container_path = self.__input_text("container path")
            volume_info = host_path + ":" + container_path
            execute_command.append("-v %s" % volume_info)

        answer = self.__input_text("Would you like to add a link? (y or n)")
        if answer == 'y':
            container_name = self.__input_text("container name")
            execute_command.append("--link %s" % container_name)

        answer = self.__input_text("Would you like to add a environment? (y or n)")
        if answer == 'y':
            env = self.__input_text("please type environment (key=value) like PROFILES=DEV")
            execute_command.append("-e %s" % env)

        execute_command.append("%s" % base_image)
        create_command = " ".join(execute_command)
        print(create_command)
        subprocess.call(create_command, shell=True)

    # ==============================================
    # 컨테이너에 command 실행
    # ==============================================
    def execute_command_in_container(self):
        container_id = self.__print_command_result(self.get_docker_ps(), skip_head=False, split_separator="\t", index_data=0)
        command = self.__input_text("command")

        answer = self.__input_text("Would you like to connect the container with root account? (y or n)")
        if answer == 'y':
            execute_command = "docker exec -it --user root %s %s" % (container_id, command)
            subprocess.call(execute_command, shell=True)
        else:
            execute_command = "docker exec -it %s %s" % (container_id, command)
            subprocess.call(execute_command, shell=True)

    # ==============================================
    # 컨테이너 로그
    # ==============================================
    def logs_container(self):
        container_id = self.__print_command_result(self.get_docker_ps(), skip_head=False, split_separator="\t", index_data=0)
        answer = self.__input_text("Would you like to follow log output? (y or n)")
        if answer == 'y':
            execute_command = "docker logs -f %s" % container_id
            subprocess.call(execute_command, shell=True)
        else:
            execute_command = "docker logs %s" % container_id
            subprocess.call(execute_command, shell=True)

    # ==============================================
    # 컨테이너 중지
    # ==============================================
    def stop_container(self):
        command = self.get_docker_ps(filters='--filter "status=running"')
        container_id = self.__print_command_result(command, skip_head=False, split_separator="\t", index_data=0)
        execute_command = "docker stop %s" % container_id
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 컨테이너 시작
    # ==============================================
    def start_container(self):
        container_id = self.__print_command_result('docker ps -a --filter "status=exited" --format "{{.ID}}\t{{.Names}}"', skip_head=False, split_separator="\t", index_data=0)
        execute_command = "docker start %s" % container_id
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 컨테이너 재시작
    # ==============================================
    def restart_container(self):
        command = self.get_docker_ps()
        container_id = self.__print_command_result(command, skip_head=False, split_separator="\t", index_data=0)
        execute_command = "docker restart %s" % container_id
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 컨테이너 삭제
    # ==============================================
    def remove_container(self):
        container_id = self.__print_command_result(self.get_docker_ps(), skip_head=False, split_separator="\t", index_data=0)
        print("container_id : %s" % container_id)
        subprocess.call("docker rm -f %s" % container_id, shell=True)

    # ==============================================
    # 컨테이너 모두 삭제
    # ==============================================
    def remove_all_container(self):
        answer = self.__input_text("Are you sure to remove all containers in docker? (y or n)")
        if answer == 'y':
            output = self.__process("docker ps -a -q")
            ps_list = output.splitlines()
            for container_id in ps_list:
                subprocess.call("docker rm -f %s" % container_id, shell=True)

    # ==============================================
    # 도커 이미지 빌드
    # ==============================================
    def build_image(self):
        image_name = self.__input_text("image name")
        tag_name = self.__input_text("tag name")
        execute_command = "docker build --no-cache -t %s:%s ." % (image_name, tag_name)
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 이미지 삭제
    # ==============================================
    def remove_image(self):
        base_image = self.__print_command_result('docker images --format "{{.Repository}}:{{.Tag}}"')
        execute_command = "docker rmi -f %s" % base_image
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # docker history
    # ==============================================
    def docker_history(self):
        base_image = self.__print_command_result('docker images --format "{{.Repository}}:{{.Tag}}"')
        csv_file_name = "docker_history.csv"
        execute_command = 'docker history %s --format "table{{.ID}}, {{.CreatedSince}}, {{.Size}}, {{.CreatedBy}}" --no-trunc > %s' % (base_image, csv_file_name)
        subprocess.call(execute_command, shell=True)
        print("made a CSV file : %s" % csv_file_name)

    # ==============================================
    # <none> 이미지 모두 삭제
    # ==============================================
    def remove_all_dangling_image(self):
        output = self.__process('docker images -f "dangling=true" -q')
        img_list = output.splitlines()
        for img_id in img_list:
            subprocess.call("docker rmi %s" % img_id, shell=True)

    # ==============================================
    # docker_compose up
    # ==============================================
    def docker_compose_up(self):
        answer = self.__input_text("docker-compose.yml 파일이 존재하는 디렉토리에서 위치해 있습니까? (y or n)")
        if answer == 'y':
            self.__process('docker-compose.exe up -d')

    # ==============================================
    # docker ps
    # ==============================================
    def docker_ps(self):
        output = self.__process(self.get_docker_ps())
        print(output)

    # ==============================================
    # docker inspect
    # ==============================================
    def docker_inspect(self):
        container_id = self.__print_command_result(self.get_docker_ps(), skip_head=False, split_separator="\t", index_data=0)
        execute_command = "docker inspect %s" % container_id
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 이미지 생성
    # ==============================================
    def make_image(self):
        container_id = self.__print_command_result(self.get_docker_ps(), skip_head=False, split_separator="\t", index_data=0)
        image_name = self.__input_text("image name")
        tag_name = self.__input_text("tag name")
        execute_command = "docker commit %s %s:%s" % (container_id, image_name, tag_name)
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # 네트워크 상세
    # ==============================================
    def network_inspect(self):
        network_id = self.__print_command_result("docker network ls", skip_head=True, split_separator=" ", index_data=0)
        execute_command = "docker inspect %s" % network_id
        subprocess.call(execute_command, shell=True)

    # ==============================================
    # all 컨테이너 정보
    # ==============================================
    def show_all_container_info(self):
        output = self.__process('docker ps --format="{{.Names}}"')
        container_list = output.splitlines()
        for container_name in container_list:
            print("\n")
            option_format_arr = []
            option_format_arr.append('--format="')
            option_format_arr.append('ID : {{.ID}}')
            option_format_arr.append('\\nImage : {{.Image}}')
            option_format_arr.append('\\nCommand : {{.Command}}')
            option_format_arr.append('\\nCreatedAt : {{.CreatedAt}}')
            option_format_arr.append('\\nStatus : {{.Status}}')
            option_format_arr.append('\\nPorts : {{.Ports}}')
            option_format_arr.append('\\nNames : {{.Names}}')
            option_format_arr.append('\\nMounts : {{.Mounts}}')
            option_format_arr.append('\\nNetworks : {{.Networks}}"')
            option_format_str = "".join(option_format_arr)

            command = "docker ps " + option_format_str + ' --filter="name=%s"' % container_name
            print(Color.YELLOW + "======================================================" + Color.ENDC)
            print(Color.YELLOW + container_name + Color.ENDC)
            print(Color.YELLOW + "======================================================" + Color.ENDC)
            subprocess.call(command, shell=True)

            inspect_command_arr = []
            inspect_command_arr.append('--format="')
            inspect_command_arr.append('IPAddress : {{.NetworkSettings.IPAddress}}')
            inspect_command_arr.append('\nHostsPath : {{.HostsPath}}')
            inspect_command_arr.append('\nHostname : {{.Config.Hostname}}')
            inspect_command_arr.append('\nGateway : {{.NetworkSettings.Gateway}}')
            inspect_command_arr.append('"')
            inspect_command_str = "".join(inspect_command_arr)

            inspect_command = "docker inspect " + inspect_command_str + " " + container_name
            subprocess.call(inspect_command)

    # ==============================================
    # common
    # ==============================================
    def __print_command_result(self, command, **kwargs):
        output = self.__process(command)
        output_list = output.splitlines()

        skip_head = kwargs.get("skip_head")
        split_separator = kwargs.get("split_separator")
        index_data = kwargs.get("index_data")

        if skip_head is True:
            del output_list[0]

        for i, row in enumerate(output_list):
            print(Color.READ + str(i) + Color.ENDC, row)

        number = self.__input_text("number")
        data = output_list.pop(int(number))
        if split_separator is not None:
            data = data.split(split_separator)[index_data]

        return data

    def __input_text(self, text):
        show_text = text + " : "
        return input(Color.YELLOW + show_text + Color.ENDC)

    def __process(self, cmd):
        output = subprocess.check_output(cmd, shell=True)
        return output.decode("utf-8")

    def __signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def __only_number(self, str):
        return re.match("[0-9]", str)

    def __reflection(self, instance, func_name):
        func = getattr(instance, func_name)
        func()

    def execute(self):
        command_list = self.command_list()
        number = self.__input_text("please choose a command")
        if self.__only_number(number):
            command = command_list[int(number)]
            self.__reflection(self, command)


class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    READ = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ==============================================
# main
# ==============================================
if __name__ == "__main__":
    d = DockerCommand()
    d.execute()
