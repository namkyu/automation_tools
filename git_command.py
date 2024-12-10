# -*- coding: utf-8 -*-

import datetime
import json
import random
import re
import string
import subprocess
import sys

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

from common.common_service import CommonService


class GitCommand(CommonService):

    limit_row_num = 10

    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    }

    def __init__(self):
        super().__init__()

    def command_list(self):
        commands = []
        commands.append("help")
        commands.append("auto_merge")
        commands.append("commit")
        commands.append("merge")
        commands.append("auto_pull")
        commands.append("list_stash")
        commands.append("save_stash")
        commands.append("pop_stash")
        commands.append("apply_stash")
        commands.append("drop_stash")
        commands.append("reset")
        commands.append("rebase")
        commands.append("rebase_interactive")
        commands.append("rebase_change_commit_date")
        commands.append("rebase_continue")
        commands.append("print_commit_history")
        commands.append("make_commit_history_for_test")

        self._print_table(["num", "command"], commands)
        return commands

    # ==============================================
    # valid 체크
    # ==============================================
    def check_current_branch(self):
        current_branch = self.current_branch()
        if current_branch in ("develop", "master"):
            print("does not support to do anything in this branch ==> %s" % current_branch)
            sys.exit()

    # ==============================================
    # common
    # ==============================================
    def help(self):
        print("save_stash : stash 에 저장하기")
        print("apply_stash : stash 에서 꺼내오기 (stash 삭제 하지 않음)")
        print("pop_stash : stash 에서 꺼내오기 (stash 삭제 함)")
        print("=============== rebase 관련 ==================")
        print("pick : 해당 커밋을 수정하지 않고, 그냥 사용")
        print("reword : 커밋 메시지만 수정")
        print("edit : 커밋 정보 수정 가능 (메시지, author, date)")
        print("squash : 해당 커밋을 이전 커밋과 합치기")
        print("위의 옵션을 적용한 후 저장하면 이후 edit 모드 화면이 출력되고 그곳에서 commit message를 수정해야 한다.")
        print("==============================================")

    def process(self, cmd):
        print("# %s" % cmd)
        output = subprocess.check_output(cmd, shell=True)
        return output.decode("utf-8")
    
    def call(self, cmd):
        print("# %s" % cmd)
        subprocess.call(cmd, shell=True)

    def current_branch(self):
        output = self.process("git rev-parse --abbrev-ref HEAD")
        return output.rstrip()

    def last_commit(self):
        return self.process("git rev-list -1 HEAD")

    def list_branch(self):
        branch_list = self.process("git branch").splitlines()
        new_branch_list = []
        for i, branch in enumerate(branch_list):
            b = re.sub("(\\s|\\*)", "", branch)
            new_branch_list.append(b)

        self._print_table(["num", "branch"], new_branch_list)
        return new_branch_list

    def git_commit_log(self, max_count):
        commit_logs = self.process("git log --oneline --max-count=%d" % max_count).splitlines()
        commit_log_list = []
        for i, log in enumerate(commit_logs):
            commit_log = log.split(" ", 1)[1]
            commit_log_list.append(commit_log)

        self._print_table(["num", "log"], commit_log_list)
        return commit_log_list

    # ==============================================
    # features
    # ==============================================
    def auto_merge(self):
        git.check_current_branch()
        c_branch = self.current_branch()
        if c_branch.find("feature") > -1:
            self.call("git checkout develop")
            self.call("git pull origin develop")
            self.call("git merge %s --no-edit" % c_branch)
            self.call("git push origin develop")
            self.call("git checkout %s" % c_branch)
        elif c_branch.find("hotfix") > -1:
            self.call("git checkout develop")
            self.call("git pull origin develop")
            self.call("git merge %s" % c_branch)
            self.call("git push origin develop")
            self.call("git checkout master")
            self.call("git pull origin master")
            self.call("git merge %s" % c_branch)
            self.call("git push origin master")
            self.call("git checkout %s" % c_branch)

    def commit(self):
        commit_msg = input("please type commit message : ")
        self.call("git add *")
        self.call("git commit -m \"%s\"" % commit_msg)

    def merge(self):
        new_branch_list = self.list_branch()
        from_branch_number = input("please choose a branch to merge (가져올브랜치) : ")
        if self._only_number(from_branch_number):
            from_branch = new_branch_list[int(from_branch_number)]
            new_branch_list = self.list_branch()
            to_branch_number = input("please choose a branch to be merged (머지되는브랜치) : ")
            if self._only_number(to_branch_number):
                to_branch = new_branch_list[int(to_branch_number)]
                self.call("git checkout %s" % to_branch)
                self.call("git pull origin %s" % to_branch)
                self.call("git merge %s" % from_branch)

                answer = input("Would you like to push this branch? (y or n) : ")
                if answer == 'y':
                    self.call("git push origin %s" % to_branch)
                self.call("git checkout %s" % from_branch)

    def rebase(self):
        self.help()
        branch_list = self.list_branch()
        from_branch_number = input("어떤 브랜치의 commit을 이동시킬 것 입니까? (from branch) : ")
        from_branch = branch_list[int(from_branch_number)]
        to_branch_number = input("%s의 commit들을 어느 브랜치의 끝으로 이동시킬 것입니까? : " % from_branch)
        to_branch = branch_list[int(to_branch_number)]
        # 대상이 되는 브랜치로 이동하여 pull 받는다. (최신 소스 반영)
        self.call("git checkout %s" % to_branch)
        self.call("git pull origin %s" % to_branch)
        # rebase 진행
        self.call("git checkout %s" % from_branch)
        self.call("git rebase %s" % to_branch)
        answer = input("병합하시겠습니까? (y or n)")
        if answer == 'y':
            self.call("git checkout %s" % to_branch)
            self.call("git merge %s" % from_branch)

    def rebase_interactive(self):
        self.help()
        self.git_commit_log(20)
        commit_log_num = input("어느 commit 까지 수정하실 건가요? : ")
        self.call("git rebase -i HEAD~%d" % (int(commit_log_num) + 1))

    def rebase_change_commit_date(self):
        now = datetime.datetime.now().strftime("%b %d %H:%M:%S %Y")
        self.call('git commit --amend --no-edit --date "%s +0900"' % now)

    def rebase_continue(self):
        self.call("git rebase --continue")

    def auto_pull(self):
        self.call("git checkout develop")
        self.call("git pull origin develop")
        self.call("git checkout master")
        self.call("git pull origin master")

    def list_stash(self):
        stash_list = self.process("git stash list").splitlines()
        for i, stash in enumerate(stash_list):
            print(i, stash)
        return stash_list

    def save_stash(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stash_name = input("please type stash name : ")
        self.call("git stash save -u %s %s" % (now, stash_name))

    def apply_stash(self):
        self.list_stash()
        number = input("please choose number : ")
        if self._only_number(number):
            self.call("git stash apply %s" % number)

    def pop_stash(self):
        self.list_stash()
        number = input("please choose number : ")
        if self._only_number(number):
            self.call("git stash pop %s" % number)

    def drop_stash(self):
        self.list_stash()
        number = input("please choose number : ")
        if self._only_number(number):
            self.call("git stash drop %s" % number)

    def reset(self):
        # git reset --hard  a3bbb3c
        line_number = input("how many lines? : ")
        commit_list = self.process("git log -%s --pretty=oneline" % line_number).splitlines()
        for i, commit in enumerate(commit_list):
            print(i, commit)

    def make_commit_history_for_test(self):
        current_branch = self.current_branch()
        print("current branch : %s" % current_branch)
        file_name = input("test file : ")
        for _ in range(10):
            with open(file_name, "a") as file:
                msg = ''.join(random.choice(string.ascii_lowercase) for c in range(5))
                file.write(msg)
            file.close()
            self.call("git add *")
            self.call("git commit -m '%s_%s_%s_%d'" % (current_branch, msg, file_name, _))

    def print_commit_history(self):
        config = json.loads(self._select_value("commit_history_env"))
        url = config.get("url")
        services = config.get("services")

        self._print_table(["project", "repository"], services)
        print("if you want to see whole projects, please press enter keyboard.")
        number = input("please choose a project : ")

        # 모두
        if not number:
            for service in services:
                self.project_history(service, url)
        # 단 건
        else:
            service = services[int(number)]
            self.project_history(service, url)

    def project_history(self, service, url):
        project = service.get("project")
        repository = service.get("repository")

        git_url = url.get("git_url")
        git_login_url = url.get("git_login_url")
        git_project_url = url.get("git_project_url") % (project, repository)
        session = self.login(git_login_url)

        res = session.get(git_project_url, headers=self.common_headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        elements = soup.select("#commits-table > tbody > tr")

        data_list = []
        for i, element in enumerate(elements):
            if i == self.limit_row_num:
                break
            try:
                author = element.select_one(".author > div").attrs['title']
                commit_link = element.select_one(".commitid").attrs['href']
                commit_msg = element.select_one(".message-subject").text
                date_text = element.select_one("time").text

                author = author[0:3]
                commit_msg = commit_msg.split("\n")[0]
                commit_link = git_url + commit_link

                data_list.append([author, commit_link, date_text, commit_msg])
            except Exception as ex:
                continue

        print(tabulate(data_list, headers=["name", "link", "date", "message"], tablefmt="rst"))
        print("\n\n")

    def execute(self):
        command_list = self.command_list()
        number = input("please choose command : ")
        if self._only_number(number):
            command = command_list[int(number)]
            git_command = GitCommand()
            self._reflection(git_command, command)


# ==============================================
# main
# ==============================================
if __name__ == "__main__":
    git = GitCommand()
    git.execute()
