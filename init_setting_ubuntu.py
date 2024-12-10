#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import sys
import time


class InitSettingUbuntu:
    EMPTY = ""

    def execute_command(self, command):
        try:
            print(bcolors.YELLOW + command + bcolors.ENDC)
            answer = input("Continue to execute above command? (y or n) : ")
            if answer != 'y':
                print(self.EMPTY)
                return

            subprocess.check_call(command, shell=True)
            time.sleep(1)
            print(bcolors.BLUE + "SUCCESS!!\n" + bcolors.ENDC)
        except subprocess.CalledProcessError:
            sys.exit(1)

    def start(self):
        answer = input("Would you like to initialize on this computer? (y or n) : ")
        if answer != 'y':
            return

        answer = input("Are you a root account? (y or n) : ")
        if answer != 'y':
            return

        print("============================================")
        print("Create User")
        print("============================================")
        user_id = input("Please type user id : ")
        user_pw = input("Please type user password : ")
        self.execute_command("sudo useradd -m {}".format(user_id))
        self.execute_command("echo '{}:{}' | sudo chpasswd".format(user_id, user_pw))

        print("============================================")
        print("Add Authority Sudo")
        print("============================================")
        self.execute_command("echo '{} ALL=(ALL:ALL) ALL' >> /etc/sudoers".format(user_id))

        print("============================================")
        print("Install Essential Library")
        print("============================================")
        self.execute_command("sudo apt-get update -y".format(user_id))
        self.execute_command("sudo apt-get install build-essential -y".format(user_id))

        print("============================================")
        print("Change Root Password")
        print("============================================")
        self.execute_command("passwd")

        print("============================================")
        print("Change Default Shell Configuration")
        print("============================================")
        self.execute_command("chsh {} -s /bin/bash".format(user_id))

        print("============================================")
        print("Ignore Password Expired")
        print("============================================")
        self.execute_command("sudo chage -E -1 -m 0 {}".format(user_id))
        self.execute_command("sudo chage -E -1 -M 99999 {}".format(user_id))
        self.execute_command("sudo chage -l {}".format(user_id))

        print("============================================")
        print("Shell Timeout Configuration")
        print("============================================")
        self.execute_command("echo 'TMOUT=' >> ~/.profile")

        print("============================================")
        print("File Descriptor")
        print("============================================")
        self.execute_command("echo '* hard nofile 10240' >> /etc/security/limits.conf")
        self.execute_command("echo '* soft nofile 10240' >> /etc/security/limits.conf")


class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    READ = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ======================================
# main
# ======================================
if __name__ == "__main__":
    isu = InitSettingUbuntu()
    isu.start()
