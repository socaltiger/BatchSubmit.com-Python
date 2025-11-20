#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file2.py -- Python CGI program that performs file management tasks
#
# Converted from original Perl file2 CGI

import os
import sys
import html
import time
from http import cookies
from cgi import FieldStorage, escape
from pathlib import Path

# crypt fallback: attempt to use POSIX crypt, otherwise use identity (matches plain-text behavior)
try:
    from crypt import crypt as _crypt
except Exception:
    def _crypt(pw, salt):
        return pw

def read_base(base_path="base.txt"):
    basedir = ""
    info = ""
    try:
        with open(base_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split("|", 1)
                if len(parts) == 2:
                    basedir, info = parts
                else:
                    basedir = parts[0]
    except Exception:
        pass
    return basedir, info

def read_pswd(pswd_path="pswd2.cgi"):
    # file format: username:password:type:email:path
    users = {}
    types = {}
    emails = {}
    paths = {}
    try:
        with open(pswd_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split(":")
                # at least username and password expected
                if len(parts) >= 2:
                    uname = parts[0]
                    upwd = parts[1]
                    utype = parts[2] if len(parts) > 2 else ""
                    uemail = parts[3] if len(parts) > 3 else ""
                    upath = parts[4] if len(parts) > 4 else ""
                    users[uname] = upwd
                    types[uname] = utype
                    emails[uname] = uemail
                    paths[uname] = upath
    except Exception:
        pass
    return users, types, emails, paths

def sanitize_value(name, value):
    if value is None:
        return ""
    # In original Perl they removed HTML tags for all fields except "source"
    if name != "source":
        # remove tags: naive approach by escaping
        return html.escape(value)
    else:
        # allow HTML in "source" but strip HTML comments (like Perl)
        # remove <!-- ... -->
        import re
        value = re.sub(r"<!--(.|\n)*?-->", "", value)
        return value

def http_print(s):
    sys.stdout.write(s)

def main():
    # parse form
    form = FieldStorage()
    # gather form into dict like Perl's %FORM
    FORM = {}
    for key in form:
        field = form[key]
        # For file uploads, FieldStorage yields a mini-field with file attribute
        if isinstance(field, list):
            # multiple fields with same name
            values = []
            for f in field:
                if f.file:
                    # file upload; read small preview or leave placeholder
                    values.append(f.value.decode('utf-8', errors='ignore') if isinstance(f.value, bytes) else f.value)
                else:
                    values.append(f.value)
            FORM[key] = values[-1]
        else:
            if field.file:
                # file upload contents may be large; keep as bytes or decode
                try:
                    val = field.value
                    if isinstance(val, bytes):
                        val = val.decode('utf-8', errors='ignore')
                except Exception:
                    val = ""
            else:
                val = field.value
            FORM[key] = sanitize_value(key, val)

    # read base and pswd files
    basedir, baseinfo = read_base("base.txt")
    users, types, emails_map, paths_map = read_pswd("pswd2.cgi")

    # Output header
    http_print("Content-type: text/html; charset=iso-8859-1\n\n")

    # parse cookies
    cookie_header = os.environ.get("HTTP_COOKIE", "")
    c = cookies.SimpleCookie()
    c.load(cookie_header)
    usrid = c.get("usrid").value if "usrid" in c else ""
    usremail = c.get("usremail").value if "usremail" in c else ""
    usrkey = c.get("usrkey").value if "usrkey" in c else ""

    # check login: original Perl did
    # if ($usrid eq "" or $usrpwdf{$usrid} ne crypt($usrkey, substr($usrid,0,2)))
    logged_in = False
    if usrid and usrid in users:
        stored = users.get(usrid, "")
        salt = (usrid[:2] if len(usrid) >= 2 else usrid)
        try:
            if stored == _crypt(usrkey, salt):
                logged_in = True
            else:
                # fallback: sometimes stored password may be plaintext and _crypt unavailable/identity
                if stored == usrkey:
                    logged_in = True
        except Exception:
            if stored == usrkey:
                logged_in = True

    if not logged_in:
        # not logged in: redirect to main2.pl like original
        http_print('<meta http-equiv="refresh" content="0; URL=main2.pl">\n')
        http_print('<a href="main2.pl">You must logon from BatchSubmit.com main page</a>\n')
        return

    # logged in: render page
    # prepare date/time in same format as original
    now = time.localtime()
    year = now.tm_year % 100
    month = now.tm_mon
    mday = now.tm_mday
    hour = now.tm_hour
    minute = now.tm_min
    sec = now.tm_sec
    date = f"{hour:02d}:{minute:02d}:{sec:02d} {month}/{mday:02d}/{year:02d}"

    # curdir and task
    curdir = FORM.get("curdir", "")
    task = FORM.get("task", "")
    action = FORM.get("action", "")

    # Print HTML (structure follows original)
    http_print("""<html><head><title>BatchSubmit.com (Beta)</title>
<STYLE type=text/css>H2 {FONT-SIZE: 16px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
TH {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
TD {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
LI {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
INPUT {FONT-SIZE: 14px}
</STYLE>
</head><body bgColor=#eaf9ff><center>
<table width=100% border=0 background="image/cloud.jpg">
<tr><td>
<table width=600 align=center border=0 bgcolor=white>
<tr>
<td rowspan="2" align=right><br><img src="image/cat_sm.png" width=100 height=100></td>
<td width=80% valign=bottom><h1><center>BatchSubmit.com (Beta)</center></h1></td>
</tr>
<tr>
<td width=25% valign=top><h3><center>Cloud Computing for SAS, R and Python Scripts</center></h3></td>
</tr>
</table>
</td></tr>
</table><br>
<Table cellSpacing=0 cellPadding=0 width=100% border=0>
  <tr>
     <td valign=top width=200 bgcolor=#dbe6e0>
       <FORM method=POST ACTION="main2.pl">
       <TABLE cellSpacing=0 cellPadding=4 width=200 border=0>
           <TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>USER</b></font></TD></TR>
           <TR><TD colspan=2 align=left><img src="image/user.png" border=0> User: """)
    http_print(html.escape(usrid))
    http_print("""</TD></TR>
           <TR><TD colspan=2 align=center><INPUT TYPE="submit" name="action" value="Logout"></TD></TR>
           <tr><td colspan=2 height=8 bgcolor=EAF9FF></td></tr>
           <TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>MENU</b></font></TD></TR>
           <TR><TD align=left><a href="main2.pl?curdir="><img src="image/landmark.png" border=0> Main</a></TD>
           <TD align=left><a href="main2.pl?curdir=/Users/""")
    http_print(html.escape(usrid))
    http_print(""""><img src="image/home.png" border=0> Home</a></TD></TR>
           <TR><TD align=left><a href="task2.pl"><img src="image/task.png" border=0> Task</a></TD>
           <TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl?board=rfp"><img src="image/auction.png" border=0> RFP</a></TD></TR>
           <TR><TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl"><img src="image/bulletin_board.png" border=0> Board</a></TD>
           <TD align=left><a href="YaBB_2.5.2/cgi-bin/yabb2/YaBB.pl?action=search"><img src="image/Find.png" border=0> Search</a></TD></TR>
           <TR><TD align=left><a href="m.main2.pl?curdir="><img src="image/iphone.png" border=0> Mobile</a></TD>
           <TD align=left><a href="help2.pl"><img src="image/help_book.png" border=0> Help</a></TD></TR>
           <tr><td colspan=2 height=8 bgcolor=EAF9FF></td></tr>
           <TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>INFO</b></font></TD></TR>
           <TR><TD colspan=2><br></TD></TR>
       </TABLE>
       </FORM>
     </td>
     <td width=8><br></td>
     <TD valign=top bgColor=#dbe6e0>
       <TABLE cellSpacing=0 cellPadding=4 width=100% border=0>
""")
    # header path display similar to Perl (with word breaks)
    display_dir = (curdir or "")
    display_escaped = html.escape(display_dir).replace("/", "/<wbr>/")
    if action in ("newfile", "newnote", "newfolder", "delfolder"):
        http_print(f'       <tr bgColor=#99bcd8><td colspan=2><font color="white">/Main{display_escaped}</font></td></tr>\n')
    else:
        task_display = html.escape(task) if task else ""
        http_print(f'       <tr bgColor=#99bcd8><td colspan=2><font color="white">/Main{display_escaped}/<wbr>{task_display}</font></td></tr>\n')

    # open the appropriate form target (upld2.pl when task == "new" and action == "upfile")
    if task == "new" and action == "upfile":
        http_print(f'<tr><td colspan=2><form method=POST action="upld2.pl" enctype="multipart/form-data">\n')
        http_print(f'<input type="hidden" name="curdir" value="{html.escape(curdir)}">\n')
        http_print(f'<input type="hidden" name="task" value="{html.escape(task)}">\n')
    else:
        http_print(f'<tr><td colspan=2><form method=POST action="actn2.pl">\n')
        http_print(f'<input type="hidden" name="curdir" value="{html.escape(curdir)}">\n')
        http_print(f'<input type="hidden" name="task" value="{html.escape(task)}">\n')
        http_print(f'<input type="hidden" name="action" value="{html.escape(action)}">\n')

    http_print("<br>\n")

    # implement actions that the original Perl actually handled in this CGI
    taskdir = "Main" + (curdir or "")
    # ensure taskdir path exists for file ops (same as original assume)
    try:
        os.makedirs(taskdir, exist_ok=True)
    except Exception:
        pass

    if action == "savepar":
        saveas = FORM.get("saveas", "")
        if saveas.lower().endswith(".par"):
            source = FORM.get("source", "")
            source = source.replace("\r", "")
            try:
                with open(os.path.join(taskdir, saveas), "w", encoding="utf-8", errors="ignore") as fd:
                    fd.write(source)
                http_print("<tr><td><b>The file has been saved</b></font></td></tr>\n")
                http_print("<tr><td>Choose one of the following:</td></tr>\n")
                http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
                http_print(f'<tr><td><h3><a href="main2.pl?curdir={html.escape(curdir)}">return to previous directory</a></h3></td></tr>\n')
            except Exception as e:
                http_print(f"<tr><td><b>Error saving file: {html.escape(str(e))}</b></td></tr>\n")
        else:
            http_print("<tr><td><b>Invalid file name, please try again</b></font></td></tr>\n")
            http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
    elif action == "savefileattr":
        saveas = FORM.get("saveas", "")
        source = FORM.get("source", "")
        source = source.replace("\r", "")
        try:
            with open(os.path.join(taskdir, f".attr.{saveas}"), "w", encoding="utf-8", errors="ignore") as fd:
                fd.write(source)
            http_print("<tr><td><b>The file has been saved</b></font></td></tr>\n")
            http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
            http_print(f'<tr><td><h3><a href="main2.pl?curdir={html.escape(curdir)}">return to previous directory</a></h3></td></tr>\n')
        except Exception as e:
            http_print(f"<tr><td><b>Error saving file attribute: {html.escape(str(e))}</b></td></tr>\n")
    elif action == "savefolderattr":
        source = FORM.get("source", "")
        source = source.replace("\r", "")
        try:
            with open(os.path.join(taskdir, ".sharefolder"), "w", encoding="utf-8", errors="ignore") as fd:
                fd.write(source)
            http_print("<tr><td><b>The file has been saved</b></font></td></tr>\n")
            http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
            http_print(f'<tr><td><h3><a href="main2.pl?curdir={html.escape(curdir)}">return to previous directory</a></h3></td></tr>\n')
        except Exception as e:
            http_print(f"<tr><td><b>Error saving folder attribute: {html.escape(str(e))}</b></td></tr>\n")
    elif action == "savefeedback":
        saveas = FORM.get("saveas", "")
        append = FORM.get("append", "")
        if saveas.lower().endswith(".msg"):
            append = append.replace("\r", "")
            try:
                with open(os.path.join(taskdir, saveas), "a", encoding="utf-8", errors="ignore") as fd:
                    fd.write(f"\nat {date}, {usrid} says:\n\n")
                    fd.write(append)
                    fd.write("\n\n============================================================\n")
                http_print("<tr><td><b>The feedback has been added</b></font></td></tr>\n")
                http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
                http_print(f'<tr><td><h3><a href="main2.pl?curdir={html.escape(curdir)}">return to previous directory</a></h3></td></tr>\n')
            except Exception as e:
                http_print(f"<tr><td><b>Error appending feedback: {html.escape(str(e))}</b></td></tr>\n")
        else:
            http_print("<tr><td><b>Something went wrong, please try again</b></font></td></tr>\n")
            http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
    elif action == "save":
        saveas = FORM.get("saveas", "")
        saveas = saveas.replace(" ", "_")
        # try to get extension of original task
        ext = ""
        if "." in task:
            ext = task[task.rfind("."):]
        if ext and saveas.lower().endswith(ext.lower()):
            source = FORM.get("source", "")
            source = source.replace("\r", "")
            try:
                with open(os.path.join(taskdir, saveas), "w", encoding="utf-8", errors="ignore") as fd:
                    fd.write(source)
                http_print("<tr><td><b>The file has been saved</b></font></td></tr>\n")
                http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
                http_print(f'<tr><td><h3><a href="main2.pl?curdir={html.escape(curdir)}">return to previous directory</a></h3></td></tr>\n')
            except Exception as e:
                http_print(f"<tr><td><b>Error saving file: {html.escape(str(e))}</b></td></tr>\n")
        else:
            http_print("<tr><td><b>File type must be same as original, please try again</b></font></td></tr>\n")
            http_print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>\n')
    elif action == "delfile":
        http_print(f'Do you really want to delete file "<font color=red size=+1><b>{html.escape(task)}</b></font>"?\n')
        http_print('<p><input type="submit" name="action" value="delfile" size=""><BR>\n')
    elif action == "delfolder":
        thisfolder = curdir.split("/")[-1] if curdir else ""
        http_print(f'Do you really want to delete folder "<font color=red size=+1><b>{html.escape(thisfolder)}</b></font>"?\n')
        http_print('<p><input type="submit" name="action" value="delfolder" size=""><BR>\n')
    elif action == "copyfile":
        http_print("Please enter name:\n")
        http_print('<INPUT TYPE="TEXT" NAME="copyname" VALUE="" SIZE=30><BR>\n')
        http_print('<p><input type="submit" name="action" value="copyfile" size=""><BR>\n')
    elif action == "renamefile":
        http_print("Please enter name:\n")
        http_print('<INPUT TYPE="TEXT" NAME="targetname" VALUE="" SIZE=30><BR>\n')
        http_print('<p><input type="submit" name="action" value="renamefile" size=""><BR>\n')
    elif action == "movefile":
        http_print("Please enter target folder:\n")
        http_print('<INPUT TYPE="TEXT" NAME="targetfolder" VALUE="" SIZE=30><BR>\n')
        http_print('<p><input type="submit" name="action" value="movefile" size=""><BR>\n')
    elif task == "new":
        if action == "newfile":
            http_print("Please enter new file name:\n")
            http_print('<INPUT TYPE="TEXT" NAME="newfilename" VALUE="" SIZE=30><BR>\n')
            http_print('<p><input type="submit" name="action" value="newfile" size=""><BR>\n')
        elif action == "newnote":
            http_print("Please enter new note name:\n")
            http_print('<INPUT TYPE="TEXT" NAME="newnotename" VALUE="note.msg" SIZE=30><BR>\n')
            http_print('<p><input type="submit" name="action" value="newnote" size=""><BR>\n')
        elif action == "newfolder":
            http_print("Please enter new folder name:\n")
            http_print('<INPUT TYPE="TEXT" NAME="newfoldername" VALUE="" SIZE=30><BR>\n')
            http_print('<p><input type="submit" name="action" value="newfolder" size=""><BR>\n')
        elif action == "upfile":
            http_print("Please choose file to upload:\n")
            http_print('<INPUT TYPE="FILE" NAME="upfile" VALUE="" SIZE=30><BR>\n')
            http_print('<p><input type="submit" name="action" value="upfile" size=""><BR>\n')

    # close form and rest of page
    http_print("</form>\n")
    http_print("</td></tr></table>\n")
    http_print("</table><br>\n")
    http_print('<table cellspacing=0 cellpadding=0 width=100% border=0>\n')
    http_print('    <tr><td bgcolor=#dbe6e0 align=center><br>All Rights Reserved</td></tr>\n')
    http_print('    <tr><td bgcolor=#dbe6e0 align=center><br></td></tr>\n')
    http_print('</table>\n')
    http_print('</center>\n')
    http_print('</body></html>\n')

if __name__ == "__main__":
    main()
