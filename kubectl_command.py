#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import signal
import subprocess
import sys


class KubectlCommand:
    command_pods_list = 'kubectl get pods -o wide'
    command_ingress_list = 'kubectl get ing'
    command_config_list = 'kubectl get configmap'
    command_cronjob = 'kubectl get cronjob'
    command_delete_cronjob = 'kubectl delete cronjob {}'

    command_monitor_pod = 'kubectl top pod'
    command_monitor_nodes = 'kubectl top nodes'

    command_get_container = 'kubectl get pods {} -o jsonpath="{{.spec.containers[*].name}}"'
    command_get_pods = 'kubectl get pods'
    command_deployment_list = 'kubectl get deployment'
    command_svc_list = 'kubectl get svc'
    command_hpa_list = 'kubectl get hpa'
    command_connect_container = 'kubectl exec -ti {} -c {} {}'
    command_delete_resource = 'kubectl delete {} {}'

    command_logs = 'kubectl logs -f --tail=100 {} -c {}'
    command_watch = 'kubectl get pods {} -w'
    command_apply_directory = 'kubectl apply -f {}'

    def __init__(self):
        print("This is very easy to use the kubectl command.")
        signal.signal(signal.SIGINT, self.signal_handler)

    def command_list(self):
        commands = []
        commands.append("get_pods")
        commands.append("get_ingress")
        commands.append("get_configmap")
        commands.append("get_cronjob")
        commands.append("monitor")
        commands.append("logs")
        commands.append("connect_container")
        commands.append("watch_pod")
        commands.append("remove_all_app_config")
        commands.append("delete_cronjob")
        commands.append("apply_directory")
        print("==============================================")
        for i, command in enumerate(commands):
            print(bcolors.READ + str(i) + bcolors.ENDC, command)
        print("==============================================")
        return commands

    # ==============================================
    # features
    # ==============================================
    def process(self, cmd):
        output = subprocess.check_output(cmd, shell=True)
        return output.decode("utf-8")

    def get_pods(self):
        output = self.process(self.command_pods_list)
        print(output)

    def get_ingress(self):
        output = self.process(self.command_ingress_list)
        print(output)

    def get_configmap(self):
        output = self.process(self.command_config_list)
        print(output)

    def get_cronjob(self):
        output = self.process(self.command_cronjob)
        print(output)

    def delete_cronjob(self):
        cronjob_name = self.input_text("cronjob name")
        output = self.process(self.command_delete_cronjob.format(cronjob_name))
        print(output)

    def monitor(self):
        output_nodes = self.process(self.command_monitor_nodes)
        print(output_nodes)
        output_pods = self.process(self.command_monitor_pod)
        print(output_pods)

    def logs(self):
        pod_name = self.print_command_result(self.command_get_pods, skip_head=True, split_separator=" ", index_data=0)
        container_name = self.show_containers(pod_name)
        execute_command = self.command_logs.format(pod_name, container_name)
        subprocess.call(execute_command, shell=True)

    def connect_container(self):
        search_pod_name = self.input_text("search pod name")
        pod_name = self.print_command_result(self.command_get_pods, skip_head=True, split_separator=" ", index_data=0, search_pod_name=search_pod_name)
        if pod_name is not None:
            container_name = self.show_containers(pod_name)
            command = self.input_text("please type what you want to execute a command")
            execute_command = self.command_connect_container.format(pod_name, container_name, command)
            subprocess.call(execute_command, shell=True)

    def watch_pod(self):
        pod_name = self.print_command_result(self.command_get_pods, skip_head=True, split_separator=" ", index_data=0)
        execute_command = self.command_watch.format(pod_name)
        subprocess.call(execute_command, shell=True)

    def remove_all_app_config(self):
        answer = self.input_text("Would you like to remove all of resource in the application? (y or n)")
        if answer == 'y':
            print(bcolors.BLUE + ">> show deployment" + bcolors.ENDC)
            deployment_name = self.print_command_result(self.command_deployment_list, skip_head=True, split_separator=" ", index_data=0)
            if deployment_name is not None:
                delete_deploy_command = self.command_delete_resource.format("deployment", deployment_name)
                subprocess.call(delete_deploy_command, shell=True)

            print(bcolors.BLUE + ">> show svc" + bcolors.ENDC)
            svc_name = self.print_command_result(self.command_svc_list, skip_head=True, split_separator=" ", index_data=0)
            if svc_name is not None:
                delete_svc_command = self.command_delete_resource.format("svc", svc_name)
                subprocess.call(delete_svc_command, shell=True)

            print(bcolors.BLUE + ">> show hpa" + bcolors.ENDC)
            hpa_name = self.print_command_result(self.command_hpa_list, skip_head=True, split_separator=" ", index_data=0)
            if hpa_name is not None:
                delete_hpa_command = self.command_delete_resource.format("hpa", hpa_name)
                subprocess.call(delete_hpa_command, shell=True)

    def apply_directory(self):
        path = self.input_text("directory")
        apply_command = self.command_apply_directory.format(path)
        print(apply_command)
        subprocess.call(apply_command, shell=True)

    # ==============================================
    # common
    # ==============================================
    def print_command_result(self, command, **kwargs):
        output_list = self.process(command).splitlines()
        if len(output_list) == 0:
            return None

        skip_head = kwargs.get("skip_head")
        split_separator = kwargs.get("split_separator")
        index_data = kwargs.get("index_data")
        search_pod_name = kwargs.get("search_pod_name")

        if skip_head is True:
            del output_list[0]

        if search_pod_name is not None:
            for idx, pod in enumerate(output_list):
                matched = re.match(search_pod_name, pod)
                if not matched:
                    del output_list[idx]

        if len(output_list) == 0:
            return None

        for i, deployment in enumerate(output_list):
            print(bcolors.READ + str(i) + bcolors.ENDC, deployment)

        number = self.input_text("number")
        data = output_list.pop(int(number))
        if split_separator is not None:
            data = data.split(split_separator)[index_data]

        return data

    def input_text(self, text):
        show_text = text + " : "
        return input(bcolors.YELLOW + show_text + bcolors.ENDC)

    def show_containers(self, pod_name):
        get_containers_command = self.command_get_container.format(pod_name)
        output_containers = self.process(get_containers_command)
        container_list = output_containers.split()
        for i, name in enumerate(container_list):
            print(i, name)

        number = self.input_text("number")
        container_name = container_list.pop(int(number))
        return container_name

    def signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def only_number(self, str):
        return re.match("[0-9]", str)

    def reflection(self, instance, func_name):
        func = getattr(instance, func_name)
        func()

    def execute(self):
        command_list = self.command_list()
        number = self.input_text("please choose command")
        if self.only_number(number):
            command = command_list[int(number)]
            self.reflection(self, command)


class bcolors:
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
    k = KubectlCommand()
    k.execute()
