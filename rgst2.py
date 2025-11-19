#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgst2.py -- CGI program that handles user registration
Ported from the original Perl rgst2 script.
"""

import os
import sys
import cgi
import cgitb
import html
import shutil
import time
import random

cgitb.enable()

# Config (tweak if needed)
BASE_FILE = "base.txt"
PSWD_FILE = "pswd2.cgi"
PSWD_BAK_DIR = "pswd2.cgi.bak"
PSWD_FLAG = "pswd2.flg"
QUIZ_FILE = "pswd2.cgi.quz"

MIN_NAME_LEN = 2
MAX_NAME_LEN = 20
MIN_PASS_LEN = 4
MAX_PASS_LEN = 20

# Try to use crypt if available, otherwise fallback to a simple salted SHA256 (not identical to Unix crypt).
try:
    import crypt as _crypt_mod

    def make_crypt(password, salt):
        return _crypt_mod.crypt(password, salt)

    def check_crypt(stored_hash, password, salt):
        return stored_hash == _crypt_mod.crypt(password, salt)
except Exception:
    import hashlib

    def make_crypt(password, salt):
        # fallback: SHA256(salt + password) hex
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def check_crypt(stored_hash, password, salt):
        return stored_hash == make_crypt(password, salt)


def read_base():
    basedir = None
    info = None
    try:
        with open(BASE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split("|", 1)
                if len(parts) == 2:
                    basedir, info = parts
                else:
                    basedir = parts[0]
    except FileNotFoundError:
        # allow missing base.txt (Perl original would error)
        pass
    return basedir, info


def read_pswd_file():
    """
    Read pswd2.cgi contents, return dicts.
    Format expected per-line: username:passwdhash:usertype:email:path:
    """
    usr_pw = {}
    usr_type = {}
    usr_email = {}
    usr_path = {}

    try:
        with open(PSWD_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split(":")
                # ensure at least 5 fields (Perl used split(/:/) and took all)
                if len(parts) >= 5:
                    uname = parts[0]
                    pwdhash = parts[1]
                    utype = parts[2]
                    uemail = parts[3]
                    upath = parts[4]
                    usr_pw[uname] = pwdhash
                    usr_type[uname] = utype
                    usr_email[uname] = uemail
                    usr_path[uname] = upath
    except FileNotFoundError:
        # no existing users
        pass

    return usr_pw, usr_type, usr_email, usr_path


def read_quiz():
    """
    Read quiz questions from pswd2.cgi.quz
    Format: qno:qtxt:qans
    Returns dict qno->qtxt and qno->qans (answers as strings)
    """
    quiz_txt = {}
    quiz_ans = {}
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    qno = parts[0]
                    qtxt = parts[1]
                    qans = parts[2]
                    quiz_txt[qno] = qtxt
                    quiz_ans[qno] = qans
    except FileNotFoundError:
        pass
    return quiz_txt, quiz_ans


def cookie_get(name):
    cookie = os.environ.get("HTTP_COOKIE", "")
    if not cookie:
        return ""
    # parse simple cookie string name=value; other=...
    parts = cookie.split(";")
    for p in parts:
        p = p.strip()
        if "=" in p:
            k, v = p.split("=", 1)
            if k == name:
                return v
    return ""


def html_header():
    print("Content-type: text/html; charset=iso-8859-1")
    print()


def render_base_html_start():
    # This mirrors the Perl-generated HTML header + styles
    print("<html><head><title>BatchSubmit.com (Beta)</title>")
    print(
        '<STYLE type=text/css>H2 {FONT-SIZE: 16px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}\n'
        "TH {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}\n"
        "TD {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}\n"
        "LI {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}\n"
        "INPUT {FONT-SIZE: 14px}\n"
        "</STYLE></head>\n"
    )
    print('<body bgColor=#eaf9ff><center>')
    print('<table width=100% border=0 background="image/cloud.jpg">')
    print("<tr><td>")
    print('<table width=600 align=center align=center border=0 bgcolor=white>')
    print('<tr><td rowspan="2" align=right><br><img src="image/cat_sm.png" width=100 height=100></td>')
    print('<td width=80% valign=bottom><h1><center>BatchSubmit.com (Beta)</center></h1></td></tr>')
    print('<tr><td width=25% valign=top><h3><center>Cloud Computing for SAS, R and Python Scripts</center></h3></td></tr>')
    print("</table></td></tr></table><br>")
    print('<Table cellSpacing=0 cellPadding=0 width=100% border=0>')
    print('<tr><td valign=top width=200 bgcolor=#dbe6e0>')
    print('<FORM method=POST ACTION="main2.pl">')
    print('<TABLE cellSpacing=0 cellPadding=4 width=200 border=0>')
    print('<TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>USER</b></font></TD></TR>')
    print('<TR><TD colspan=2 align=left><img src="image/user.png" border=0> User sign up</TD></TR>')
    print('<tr><td colspan=2 height=8 bgcolor=EAF9FF></td></tr>')
    print('<TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>MENU</b></font></TD></TR>')
    print('<TR><TD align=left><a href="main2.pl?curdir="><img src="image/landmark.png" border=0> Main</a></TD>')
    # home uses the user id variable that we'll get below
    usrid = cookie_get("usrid") or ""
    print(f'<TD align=left><a href="main2.pl?curdir=/Users/{html.escape(usrid)}"><img src="image/home.png" border=0> Home</a></TD></TR>')
    print('<TR><TD align=left><a href="task2.pl"><img src="image/task.png" border=0> Task</a></TD>')
    print('<TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl?board=rfp"><img src="image/auction.png" border=0> RFP</a></TD></TR>')
    print('<TR><TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl"><img src="image/bulletin_board.png" border=0> Board</a></TD>')
    print('<TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl?action=search"><img src="image/Find.png" border=0> Search</a></TD></TR>')
    print('<TR><TD align=left><a href="m.main2.pl?curdir="><img src="image/iphone.png" border=0> Mobile</a></TD>')
    print('<TD align=left>

