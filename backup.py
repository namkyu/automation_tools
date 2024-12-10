import datetime
import glob
import os
import shutil
import xml.dom.minidom
import zipfile

from common.common_service import CommonService


class Backup(CommonService):

    def __init__(self):
        super().__init__()

    # ======================================
    # zip 생성
    # ======================================
    def make_zip(self, dest_path, backup_file_path):
        file_name = os.path.splitext(os.path.basename(backup_file_path))[0]
        zip_file_name = os.path.join(dest_path, file_name)
        zip_file = zipfile.ZipFile(zip_file_name + ".zip", "w")

        mode = zipfile.ZIP_DEFLATED

        # 디렉토리인 경우
        if os.path.isdir(backup_file_path):
            for path, directory, files in os.walk(backup_file_path):
                for file in files:
                    zip_file.write(os.path.join(path, file), os.path.join(path, file), mode)

        # 파일인 경우
        elif os.path.exists(backup_file_path):
            for name in glob.glob(backup_file_path):
                zip_file.write(name, os.path.basename(name), mode)

        # zip file close
        zip_file.close()

    # ======================================
    # execute backup
    # ======================================
    def execute_backup(self):
        project_root_path = self._get_project_root_path()
        backup_info_file_path = os.path.join(project_root_path, self.BACKUP_INFO_PATH)

        dom_tree = xml.dom.minidom.parse(backup_info_file_path)
        collection = dom_tree.documentElement

        backup_folder = collection.getElementsByTagName('backup_dest_path')[0].firstChild.nodeValue
        if os.path.exists(backup_folder) and os.path.isdir(backup_folder):
            shutil.rmtree(backup_folder)
        else:
            os.makedirs(backup_folder)

        backups = collection.getElementsByTagName("backup")
        for backup_info in backups:
            backup_file_path = backup_info.getElementsByTagName('path')[0].childNodes[0].data
            description = backup_info.getElementsByTagName('description')[0].childNodes[0].data

            print("=================================")
            print("backup info")
            print("=================================")
            print("description : %s" % description)
            print("backup_file_path : %s" % backup_file_path)
            print("backup_folder : %s" % backup_folder)
            print("\n")

            # 현재 날짜 경로 추가
            now = datetime.datetime.now().strftime("%Y%m%d-%H%M")
            dest_path = os.path.join(backup_folder, now)

            # 디렉토리 생성
            if not (os.path.isdir(dest_path)):
                os.makedirs(os.path.join(dest_path))

            # zip 생성
            self.make_zip(dest_path, backup_file_path)


# ======================================
# main
# ======================================
if __name__ == "__main__":
    backup = Backup()
    backup.execute_backup()
