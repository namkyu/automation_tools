import datetime
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
import xml.dom.minidom
import xml.etree.ElementTree

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate


class CommonService(object):
    PRIVATE_INFO_PATH = "config/private_info.xml"
    BACKUP_INFO_PATH = "config/backup_info.xml"
    CHROME_DRIVER_PATH = "chromedriver.exe"

    def __init__(self):
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        print("signal number : %s", sig)
        print("You pressed Ctrl+C!")
        sys.exit(0)

    def _get_project_root_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_name = current_dir.split(os.sep)[-1]
        return current_dir.replace(package_name, '')

    def _get_private_info_config_data(self):
        return self.__get_config_data(self.PRIVATE_INFO_PATH)

    def _get_backup_info_config_data(self):
        return self.__get_config_data(self.BACKUP_INFO_PATH)

    def _get_browser(self):
        return self._get_browser_with_size(1300, 1000)

    def _get_browser_with_size(self, width, height, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36")

        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        project_root_path = self._get_project_root_path()
        chrome_driver_file_path = os.path.join(project_root_path, self.CHROME_DRIVER_PATH)
        browser = webdriver.Chrome(chrome_driver_file_path, options=options, desired_capabilities=capabilities)
        browser.set_window_position(0, 0)
        browser.set_window_size(width, height)

        # 웹페이지가 로딩될때까지 기다리고 10초가 넘어가면 웹페이지가 로딩이 됐던 안됐던 다음 명령어를 실행
        # 만약 웹페이지 로딩이 1초만에 끝났다면 다음 명령어를 실행
        browser.implicitly_wait(15)
        return browser

    def _reflection(self, instance, func_name):
        func = getattr(instance, func_name)
        func()

    def _write_text(self, browser, element_id, input_text, press_enter):
        try:
            browser.find_element_by_id(element_id).send_keys(Keys.DELETE)
            browser.find_element_by_id(element_id).send_keys(str(input_text))
            if press_enter:
                time.sleep(0.5)
                browser.find_element_by_id(element_id).send_keys(Keys.ENTER)
            else:
                time.sleep(0.5)
        except Exception as ex:
            pass

    def _only_number(self, text):
        return re.match("[0-9]", text)

    def _show_command(self, commands):
        print("\n")
        print("==============================================")
        for i, command in enumerate(commands):
            print(i, command)
        print("==============================================")

    def _common_subprocess(self, cmd):
        output = subprocess.check_output(cmd, shell=True)
        return output.decode("utf-8")

    def _new_tab(self, browser, url):
        browser.execute_script("window.open('" + url + "', '_blank')")
        print(browser.window_handles)

    def _exit(self):
        sys.exit(0)

    def _select_value(self, key):
        connection = self.__db_connection()
        cur = connection.cursor()
        cur.execute("SELECT id, title, key, value FROM info WHERE key = ?", [key])
        result = cur.fetchone()
        return result[3]

    def _is_working_time(self):
        weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday()

        if weekday in range(0, 5):
            if 6 <= hour <= 20:
                print("working day : %s, working time : %s" % (weekday_kr[weekday], hour))
                return True

        return False

    def _print_table(self, headers, data_list):
        rows = []
        for i, data in enumerate(data_list):
            rows.append([i, data])

        print(tabulate(rows, headers=headers, tablefmt="psql"))

    def _read_xml_file(self, xml_file):
        tree = xml.etree.ElementTree.parse(xml_file).getroot()
        return tree

    def explicitly_wait(self, browser, locator):
        WebDriverWait(browser, 5).until(EC.presence_of_element_located(locator))

    def explicitly_alert_wait(self, browser):
        WebDriverWait(browser, 10).until(EC.alert_is_present())

    def explicitly_clickable(self, browser, locator):
        time.sleep(2)  # 해당 코드가 없으면 stale element reference: element is not attached to the page document 오류가 자주 발생한다.
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable(locator))

    # ===========================================
    # private method
    # ===========================================
    def __db_connection(self):
        project_root_path = self._get_project_root_path()
        db_file = os.path.join(project_root_path, "config/info.db")
        return sqlite3.connect(db_file)

    def __get_config_data(self, path):
        project_root_path = self._get_project_root_path()
        private_info_file_path = os.path.join(project_root_path, path)
        root_xml = self._read_xml_file(private_info_file_path)
        return root_xml
