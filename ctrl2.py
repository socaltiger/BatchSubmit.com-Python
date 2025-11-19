#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ctrl2.py - Python CGI version of your Perl ctrl2.cgi
#

import cgi
import cgitb
cgitb.enable()

import os
import html
import urllib.parse
import crypt

# -----------------------------
# parse_form (Perl → Python)
# -----------------------------
def parse_form():
    form = cgi.FieldStorage()
    FORM = {}

    for key in form.keys():
        value = form.getvalue(key)
        if isinstance(value, list):
            value = value[0]
        if value is None:
            value = ""
        # 去掉 HTML 标签（模拟 Perl 版）
        if "<" in value:
            # 参考 Perl: $value =~ s/<([^>]|\n)*>//g;
            value = html.escape(value)
        FORM[key] = value
    return FORM


# -----------------------------
# error()
# -----------------------------
def error():
    print("error...")
    exit()


# -----------------------------
# main_page()
# -----------------------------
def main_page(FORM):

    # ----- read base.txt -----
    try:
        with open("base.txt") as f:
            line = f.readline().strip()
            basedir, info = line.split("|")
    except:
        error()

    # ----- read pswd2.cgi -----
    usrpwdf = {}
    usrtypef = {}
    usremailf = {}
    usrpathf = {}

    try:
        with open("pswd2.cgi") as f:
            for ln in f:
                ln = ln.strip()
                usrnamef, usrpwdf_v, usrtypef_v, usremailf_v, usrpathf_v = ln.split(":")
                usrpwdf[usrnamef] = usrpwdf_v
                usrtypef[usrnamef] = int(usrtypef_v)
                usremailf[usrnamef] = usremailf_v
                usrpathf[usrnamef] = usrpathf_v
    except:
        error()

    # ----- print header -----
    print("Content-type: text/html; charset=iso-8859-1\n")

    # ----- cookie -----
    cookie = os.environ.get("HTTP_COOKIE", "")

    def get_cookie(name):
        for x in cookie.split(";"):
            x = x.strip()
            if x.startswith(name + "="):
                return x.split("=",1)[1]
