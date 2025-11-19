#!/usr/bin/env python3
# upld2.py -- upload file to server

import os
import cgi
import cgitb
import html
import re

cgitb.enable()  # helpful for debugging

SAFE_CHARS = re.compile(r'^[a-zA-Z0-9_.-]+$')
BLOCKED_EXT = ('.php', '.cgi', '.pl', '.exe')

def error(msg="error..."):
    print("Content-type: text/plain\n")
    print(msg)
    exit(1)

def get_basename(fullname: str) -> str:
    return os.path.basename(fullname)

def main_page():
    print("Content-type: text/html; charset=iso-8859-1\n")

    form = cgi.FieldStorage()
    curdir = form.getvalue("curdir", "")
    action = form.getvalue("action", "")

    # Read cookies
    cookies = os.environ.get("HTTP_COOKIE", "")
    cookie_dict = {}
    for part in cookies.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookie_dict[k] = v

    usrid = cookie_dict.get("usrid", "")
    usrkey = cookie_dict.get("usrkey", "")

    # TODO: Replace with proper password/session check
    if not usrid or usrkey != "expected_key":
        print('<meta http-equiv="refresh" content="0; URL=main2.py">')
        print('<a href="main2.py">You must logon from main page</a>')
        return

    print("<html><head><title>BatchSubmit.com (Beta)</title></head><body>")
    print("<center>")

    if action == "upfile":
        upfile = form["upfile"] if "upfile" in form else None
        if not upfile or not upfile.file:
            print("There was a problem uploading your file (try a smaller file).")
            return

        basename = get_basename(upfile.filename)
        basename = basename.replace(" ", "_")
        basename = re.sub(r'[^a-zA-Z0-9_.-]', '', basename)

        if basename.lower().endswith(BLOCKED_EXT):
            print("<b>You have no permission to upload this file type.</b>")
            return
        if not SAFE_CHARS.match(basename):
            print("<b>File name contains invalid characters.</b>")
            return

        safe_dir = os.path.join("Main", curdir)
        os.makedirs(safe_dir, exist_ok=True)
        filepath = os.path.join(safe_dir, basename)

        with open(filepath, "wb") as f:
            while True:
                chunk = upfile.file.read(1024)
                if not chunk:
                    break
                f.write(chunk)

        print("<b>File has been uploaded.</b>")
        print(f'<a href="main2.py?curdir={html.escape(curdir)}">return to previous directory</a>')

    print("</center></body></html>")

if __name__ == "__main__":
    main_page()
