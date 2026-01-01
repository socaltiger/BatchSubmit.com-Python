#!/usr/bin/env python3
# exec2.py — Python translation of exec2.cgi

import os
import sys
import shutil
import cgi
import cgitb
import urllib.parse
import crypt

cgitb.enable()

SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def error(msg="error..."):
    print("Content-Type: text/plain\n")
    print(msg)
    sys.exit(1)


def valid_filename(name):
    return all(c in SAFE_FILENAME_CHARS for c in name)


def html(msg):
    print(msg)


# --------------------------------------------------
# Parse CGI input
# --------------------------------------------------

form = cgi.FieldStorage()

curdir = form.getfirst("curdir", "")
task = form.getfirst("task", "")
action = form.getfirst("action", "")

# --------------------------------------------------
# Load base directory
# --------------------------------------------------

try:
    with open("base.txt") as f:
        line = f.readline().strip()
        basedir, _ = line.split("|", 1)
except Exception:
    error("Cannot read base.txt")

# --------------------------------------------------
# Load users
# --------------------------------------------------

usrpwdf = {}

try:
    with open("pswd2.cgi") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            u, pw, *_ = line.split(":")
            usrpwdf[u] = pw
except Exception:
    error("Cannot read pswd2.cgi")

# --------------------------------------------------
# Cookies
# --------------------------------------------------

cookie = os.environ.get("HTTP_COOKIE", "")
cookies = dict(item.split("=", 1) for item in cookie.split("; ") if "=" in item)

usrid = cookies.get("usrid", "")
usrkey = cookies.get("usrkey", "")

# --------------------------------------------------
# Auth check
# --------------------------------------------------

if not usrid or usrpwdf.get(usrid) != crypt.crypt(usrkey, usrid[:2]):
    print("Content-Type: text/html\n")
    html('<meta http-equiv="refresh" content="0; URL=main2.cgi">')
    html('<a href="main2.cgi">You must logon from BatchSubmit main page</a>')
    sys.exit(0)

# --------------------------------------------------
# Paths
# --------------------------------------------------

taskdir = os.path.join(basedir, "Main" + curdir.replace("/", os.sep))

print("Content-Type: text/html\n")

# --------------------------------------------------
# Actions
# --------------------------------------------------

if action == "renamefile":
    target = form.getfirst("targetname", "")
    src = os.path.join(taskdir, task)
    dst = os.path.join(taskdir, target)

    ext = os.path.splitext(task)[1]

    if "/" in target or "\\" in target:
        html("File must stay in same directory")
    elif " " in target:
        html("Filename cannot contain spaces")
    elif not valid_filename(target):
        html("Invalid filename")
    elif not target.lower().endswith(ext.lower()):
        html("File type must remain the same")
    else:
        try:
            shutil.move(src, dst)
            html("File renamed")
        except Exception as e:
            error(str(e))

elif action == "copyfile":
    copyname = form.getfirst("copyname", "")
    src = os.path.join(taskdir, task)
    dst = os.path.join(taskdir, copyname)

    ext = os.path.splitext(task)[1]

    if "/" in copyname or "\\" in copyname:
        html("Copy must stay in same directory")
    elif " " in copyname:
        html("Filename cannot contain spaces")
    elif not valid_filename(copyname):
        html("Invalid filename")
    elif copyname == task:
        html("Same filename")
    elif not copyname.lower().endswith(ext.lower()):
        html("File type mismatch")
    else:
        shutil.copy(src, dst)
        html("File copied")

elif action == "delfile":
    path = os.path.join(taskdir, task)

    if ".." in path:
        html("Invalid path")
    elif os.path.exists(path):
        os.unlink(path)
        html("File deleted")
    else:
        html("File does not exist")

elif action == "newfile":
    name = form.getfirst("newfilename", "")
    path = os.path.join(taskdir, name)

    if "/" in name or "\\" in name:
        html("Invalid filename")
    elif " " in name:
        html("Filename cannot contain spaces")
    elif not valid_filename(name):
        html("Invalid filename")
    elif name.lower().endswith((".cgi", ".pl", ".exe", ".php")):
        html("Permission denied")
    elif os.path.exists(path):
        html("File already exists")
    else:
        open(path, "w").close()
        html("File created")

elif action == "newfolder":
    name = form.getfirst("newfoldername", "")
    path = os.path.join(taskdir, name)

    if "/" in name or "\\" in name:
        html("Invalid folder name")
    elif " " in name:
        html("Folder name cannot contain spaces")
    elif not valid_filename(name):
        html("Invalid folder name")
    elif os.path.exists(path):
        html("Folder already exists")
    else:
        os.mkdir(path)
        html("Folder created")

elif action == "delfolder":
    if ".." in taskdir:
        html("Invalid folder")
    elif os.path.exists(taskdir):
        if not os.listdir(taskdir):
            shutil.rmtree(taskdir)
            html("Folder deleted")
        else:
            html("Folder not empty")
    else:
        html("Folder does not exist")

elif action == "movefile":
    targetfolder = form.getfirst("targetfolder", "")
    dest = os.path.abspath(os.path.join(taskdir, targetfolder))
    userroot = os.path.abspath(os.path.join(basedir, "Main", "Users", usrid))

    if not os.path.isdir(dest):
        html("Target folder does not exist")
    elif not dest.lower().startswith(userroot.lower()):
        html("Out of bounds")
    else:
        shutil.move(os.path.join(taskdir, task), dest)
        html("File moved")

else:
    html("No action")
