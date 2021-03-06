#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess
from multiprocessing import Pool

# path to the project root
path = os.path.abspath(os.path.dirname(__file__))

def list_submodules():
    gitmodules = open(os.path.join(path, ".gitmodules"), 'r')
    submodules = re.findall("path = ([\w\-_\/]+)", gitmodules.read())
    gitmodules.close()
    return submodules


def check_submodule(name):
    # Get commit id of local branch
    cmd_commit = ["git", "-C", name, "rev-parse", "--verify", "HEAD"]
    commit_id = subprocess.Popen(cmd_commit, shell=False,
                                 stdout=subprocess.PIPE) \
                                .communicate()[0].decode().rstrip('\n')

    # Check if it's also in the remote branch
    cmd_check = ["git", "-C", name, "branch", "--quiet", "-r", "--contains", commit_id]
    print("Checking %s..." % name)
    res = subprocess.Popen(cmd_check, shell=False, stdout=subprocess.PIPE) \
                    .communicate()[0].decode().splitlines()
    print("%s checked" % name)

    if len(res) == 0:
        return name

    return None


if __name__ == '__main__':
    p = Pool()
    submodules_status = p.map(check_submodule, list_submodules())
    failed_submodules = list(filter(None.__ne__, submodules_status))
    if len(failed_submodules) > 0:
        print("Following submodules have not been pushed:\n  - ", end="")
        print(*failed_submodules, sep='\n  - ')
        sys.exit(2)
    sys.exit(0)
