import os
import sys


def search_file(search_root_dir, search_file_name):
    files = os.listdir(search_root_dir)
    for file in files:
        fullname_file = os.path.join(search_root_dir, file)
        if os.path.isdir(fullname_file):
            search_file(fullname_file, search_file_name)
        else:
            if search_file_name == file:
                print("------------------------------------------------------")
                print("found file path =>", fullname_file)
                print("------------------------------------------------------")
                sys.exit(0)
            if logging == "Y":
                print(fullname_file)


argument_len = len(sys.argv)
if argument_len != 4:
    print("invalid argument length !!")
    sys.exit(1)

logging = sys.argv[3]
search_file(sys.argv[1], sys.argv[2])
