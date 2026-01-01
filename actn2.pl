#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import cgi
import html
from urllib.parse import unquote_plus

SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"

def error(msg):
    print("Content-Type: text/html\n")
    print(f"<html><body>Error: {html.escape(msg)}</body></html>")
    sys.exit(1)

def is_safe_name(name):
    return all(c in SAFE_FILENAME_CHARS for c in name)

def read_base():
    with open("base.txt") as f:
        line = f.readline().strip()
        basedir, _ = line.split("|", 1)
        return basedir

def main():
    print("Content-Type: text/html\n")

    form = cgi.FieldStorage()

    action = form.getvalue("action", "")
    curdir = form.getvalue("curdir", "")
    task = form.getvalue("task", "")

    basedir = read_base()
    taskdir = os.path.join(basedir, "Main" + curdir)

    print("<html><body>")

    # ========== delete file ==========
    if action == "delfile":
        target = os.path.join(taskdir, task)

        if ".." in target:
            print("Invalid path")
        elif os.path.exists(target):
            os.remove(target)
            attr = os.path.join(taskdir, ".attr." + task)
            if os.path.exists(attr):
                os.remove(attr)
            print("File deleted")
        else:
            print("File does not exist")

    # ========== delete folder ==========
    elif action == "delfolder":
        if ".." in taskdir:
            print("Invalid directory")
        elif os.path.isdir(taskdir) and not os.listdir(taskdir):
            shutil.rmtree(taskdir)
            print("Folder deleted")
        else:
            print("Folder not empty or not exists")

    # ========== copy file ==========
    elif action == "copyfile":
        copyname = form.getvalue("copyname", "")
        src = os.path.join(taskdir, task)
        dst = os.path.join(taskdir, copyname)

        if not is_safe_name(copyname):
            print("Invalid filename")
        elif os.path.exists(dst):
            print("File already exists")
        else:
            shutil.copy(src, dst)
            print("File copied")

    # ========== rename ==========
    elif action == "renamefile":
        targetname = form.getvalue("targetname", "")
        src = os.path.join(taskdir, task)
        dst = os.path.join(taskdir, targetname)

        if not is_safe_name(targetname):
            print("Invalid filename")
        else:
            shutil.move(src, dst)
            print("File renamed")

    # ========== move ========

