#!/usr/bin/env python3
# exec2.py -- Python CGI port of exec2.cgi
# Notes: assumes a UNIX-like environment (fcntl, crypt). Adjust paths/permissions as needed.

import cgi
import os
import sys
import html
import fcntl
import crypt as pycrypt   # may not exist on non-unix; if not available, code will fall back
import traceback

# Helper to safe-print (CGI)
def print_http_headers():
    print("Content-type: text/html; charset=iso-8859-1")
    print()

# Read base.txt -> basedir, info (uses last non-empty line in original)
def read_base():
    basedir, info = "", ""
    try:
        with open("base.txt", "r") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split("|", 1)
                if len(parts) == 2:
                    basedir, info = parts
    except Exception:
        pass
    return basedir, info

# Read pswd2.cgi into dicts
def read_users():
    usrpwdf = {}
    usrtypef = {}
    usremailf = {}
    usrpathf = {}
    try:
        with open("pswd2.cgi", "r") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                parts = line.split(":")
                # Expect: username:password:type:email:path
                if len(parts) >= 5:
                    usrnamef, pwd, utype, uemail, upath = parts[:5]
                else:
                    # Fallback - fill missing
                    parts += [""] * (5 - len(parts))
                    usrnamef, pwd, utype, uemail, upath = parts
                usrpwdf[usrnamef] = pwd
                usrtypef[usrnamef] = utype
                usremailf[usrnamef] = uemail
                usrpathf[usrnamef] = upath
    except Exception:
        pass
    return usrpwdf, usrtypef, usremailf, usrpathf

# Read cookies from environment
def parse_cookies():
    cookies = {}
    cookie_hdr = os.environ.get("HTTP_COOKIE", "")
    for pair in cookie_hdr.split(";"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies

# Utility to safe-escape text for HTML
def esc(s):
    return html.escape(str(s)) if s is not None else ""

# Main CGI logic
def main():
    try:
        form = cgi.FieldStorage()
        basedir, info = read_base()
        usrpwdf, usrtypef, usremailf, usrpathf = read_users()
        cookies = parse_cookies()

        print_http_headers()

        usrid = cookies.get("usrid", "")
        usremail = cookies.get("usremail", "")
        usrkey = cookies.get("usrkey", "")

        # Validate user: original used crypt(usrkey, substr(usrid,0,2)) compare to stored password
        valid_user = False
        if usrid and usrid in usrpwdf:
            stored = usrpwdf.get(usrid, "")
            try:
                # try using crypt module
                check = pycrypt.crypt(usrkey, (usrid[:2] if len(usrid) >= 2 else usrid))
            except Exception:
                # fallback: compare plaintext (mimic original uncrypted storage fallback)
                check = usrkey
            if stored == check:
                valid_user = True

        if not valid_user:
            # redirect to main2.pl
            print('<meta http-equiv="refresh" content="0; URL=main2.pl">')
            print('<a href="main2.pl">You must logon from BatchSubmit(Beta) main page</a>')
            return

        # If reached here, user is authenticated
        # Start printing main HTML (kept structure close to original)
        print("""<html><head><title>BatchSubmit.com (Beta)</title>
<style type="text/css">
H2 {FONT-SIZE: 16px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
TH {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
TD {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
LI {FONT-SIZE: 12px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif}
INPUT {FONT-SIZE: 14px}
</style>
</head>
<body bgColor=#eaf9ff><center>
<table width=100% border=0 background="image/cloud.jpg">
<tr><td>
<table width=600 align=center border=0 bgcolor=white>
<tr>
<td rowspan="2" align=right><br><img src="image/cat_sm.png" width=100 height=100></td>
<td width=80% valign=bottom><h1><center>BatchSubmit.com (Beta)</center></h1></td>
</tr>
<tr><td width=25% valign=top><h3><center>Cloud Computing for SAS, R and Python Scripts</center></h3></td></tr>
</table>
</td></tr></table><br>

<Table cellSpacing=0 cellPadding=0 width=100% border=0>
  <tr>
     <td valign=top width=200 bgcolor=#dbe6e0>
       <FORM method=POST ACTION="main2.pl">
       <TABLE cellSpacing=0 cellPadding=4 width=200 border=0>
           <TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>USER</b></font></TD></TR>
           <TR><TD colspan=2 align=left><img src="image/user.png" border=0> User: {usr}</TD></TR>
           <TR><TD colspan=2 align=center><INPUT TYPE="submit" name="action" value="Logout"></TD></TR>
           <tr><td colspan=2 height=8 bgcolor=EAF9FF></td></tr>

           <TR bgColor=#99bcd8><TD colspan=2 align=left><font color="white"><b>MENU</b></font></TD></TR>
           <TR><TD align=left><a href="main2.pl?curdir="><img src="image/landmark.png" border=0> Main</a></TD>
           <TD align=left><a href="main2.pl?curdir=/Users/{usr}"><img src="image/home.png" border=0> Home</a></TD></TR>
           <TR><TD align=left><a href="task2.pl"><img src="image/task.png" border=0> Task</a></TD>
           <TD align=left><a href="YaBB_2.5.2/pl-bin/yabb2/YaBB.pl?board=rfp"><img src="image/auction.png" border=0> RFP</a></TD></TR>
           <TR><TD align=left><a href="YaBB_2.5.2/pl-bin/yabb2/YaBB.pl"><img src="image/bulletin_board.png" border=0> Board</a></TD>
           <TD align=left><a href="YaBB_2.5.2/pl-bin/yabb2/YaBB.pl?action=search"><img src="image/Find.png" border=0> Search</a></TD></TR>
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
""".format(usr=esc(usrid)))

        # Form fields of interest
        curdir = form.getfirst("curdir", "")
        task = form.getfirst("task", "")
        saveas = form.getfirst("saveas", "")
        action = form.getfirst("action", "")
        cron = form.getfirst("cron", "")
        cronwk = form.getfirst("cronwk", "")

        taskdir = "Main" + curdir

        # Helper: sanitize filename for save
        def contains_slash(s):
            return "/" in s or "\\" in s

        # If action == save, handle saving
        if action == "save":
            if contains_slash(saveas):
                print('<tr bgColor=#99bcd8><td width=100%><font color="white"><b>File can only be saved in the same directory, please try again.</b></font></td></tr>')
                print('<tr><td>Choose one of the following:</td></tr>')
                print('<td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td>')
            elif saveas.lower().endswith(('.sas', '.r', '.py')):
                safe_saveas = saveas.replace(" ", "_")
                source = form.getfirst("source", "")
                source = source.replace("\r", "")
                os.makedirs(taskdir, exist_ok=True)
                try:
                    with open(os.path.join(taskdir, safe_saveas), "w", newline="\n") as out:
                        out.write(source)
                    print('<tr bgColor=#99bcd8><td width=100%><font color="white"><b>The program has been saved</b></font></td></tr>')
                    print('<tr><td>Choose one of the following:</td></tr>')
                    print('<tr><td><h3><a href="main2.pl?curdir={0}">return to previous directory</a></h3></td></tr>'.format(esc(curdir)))
                except Exception as e:
                    print('<tr><td><b>Error saving file: {0}</b></td></tr>'.format(esc(e)))
            elif saveas.lower().endswith('.par'):
                try:
                    # read task template file
                    with open(os.path.join(taskdir, task), "r") as TAS:
                        tas_lines = TAS.readlines()
                except Exception as e:
                    tas_lines = []
                try:
                    with open(os.path.join(taskdir, saveas), "w") as SAV:
                        for line in tas_lines:
                            line = line.rstrip("\n")
                            parts = line.split("|")
                            # Expect 7 fields: id|label|type|name|value|size|break|
                            if len(parts) < 7:
                                SAV.write(line + "\n")
                                continue
                            wwwid, wwwlabel, wwwtype, wwwname, wwwvalue, wwwsize, wwwbreak = parts[:7]
                            if wwwtype == "select" or wwwtype == "radio":
                                options = wwwvalue.split(":")
                                newoptions = []
                                for opt in options:
                                    opt_clean = opt.replace("#", "")
                                    if form.getfirst(wwwname, "") == opt_clean:
                                        newoptions.append("#" + opt_clean)
                                    else:
                                        newoptions.append(opt_clean)
                                SAV.write("|".join([wwwid, wwwlabel, wwwtype, wwwname, ":".join(newoptions), wwwsize, wwwbreak, ""]) + "\n")
                            elif wwwtype == "checkbox":
                                v = wwwvalue.replace("#", "")
                                if form.getfirst(wwwname, "") != "":
                                    SAV.write("|".join([wwwid, wwwlabel, wwwtype, wwwname, "#" + v, wwwsize, wwwbreak, ""]) + "\n")
                                else:
                                    SAV.write("|".join([wwwid, wwwlabel, wwwtype, wwwname, v, wwwsize, wwwbreak, ""]) + "\n")
                            else:
                                if wwwname == "saveas":
                                    VAL = saveas
                                elif wwwname == "task":
                                    VAL = saveas
                                elif wwwname == "cron":
                                    VAL = cron
                                elif wwwname == "cronwk":
                                    VAL = cronwk
                                elif wwwname.lower().startswith("parm"):
                                    VAL = form.getfirst(wwwname, "")
                                else:
                                    SAV.write(line + "\n")
                                    continue
                                SAV.write("|".join([wwwid, wwwlabel, wwwtype, wwwname, VAL, wwwsize, wwwbreak, ""]) + "\n")
                    print('<tr bgColor=#99bcd8><td width=100%><font color="white"><b>The program has been saved</b></font></td></tr>')
                    print('<tr><td>Choose one of the following:</td></tr>')
                    print('<tr><td><h3><a href="main2.pl?curdir={0}">return to previous directory</a></h3></td></tr>'.format(esc(curdir)))
                except Exception as e:
                    print('<tr><td><b>Error saving .par file: {0}</b></td></tr>'.format(esc(e)))
            else:
                print('<tr bgColor=#99bcd8><td width=100%><font color="white"><b>Invalid file name, please try again</b></font></td></tr>')
                print('<tr><td>Choose one of the following:</td></tr>')
                print('<td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td>')
        else:
            # Submission (default) behavior
            if task.lower().endswith(('.par', '.sas', '.r', '.py')):
                print('<tr bgColor=#99bcd8><td width=100%><font color="white"><b>The program has been submitted for execution</b></font></td></tr>')
                print('<tr><td>Choose one of the following:</td></tr>')
                print('<tr><td><h3><a href="task2.pl">monitor task progress</a></h3></td></tr>')
                print('<tr><td><h3><a href="javascript:history.go(-1)">return to previous task</a></h3></td></tr>')
                print('<tr><td><h3><a href="main2.pl?curdir={0}">return to previous directory</a></h3></td></tr>'.format(esc(curdir)))

                # If code file, save a hidden dot-file with source
                program = form.getfirst("program", "")
                if task.lower().endswith(('.sas', '.r', '.py')):
                    source = form.getfirst("source", "")
                    source = source.replace("\r", "")
                    os.makedirs(taskdir, exist_ok=True)
                    try:
                        with open(os.path.join(taskdir, "." + task), "w", newline="\n") as tmpf:
                            tmpf.write(source)
                    except Exception as e:
                        pass

                # Determine log/out filenames (mimic perl logic)
                tasklog = tasktxt = taskout = taskerr = None
                if program.lower().endswith('.sas'):
                    tasklog = task.replace('.par', '.log').replace('.sas', '.log')
                    tasktxt = task.replace('.par', '.lst').replace('.sas', '.lst')
                elif program.lower().endswith('.r'):
                    taskout = task.replace('.par', '.out').replace('.r', '.out')
                elif program.lower().endswith('.py'):
                    taskout = task.replace('.par', '.out').replace('.py', '.out')
                    taskerr = task.replace('.par', '.err').replace('.py', '.err')

                # Acquire lock and update task.xml
                try:
                    lock_fp = open("lock.xml", "w")
                    lockcount = 0
                    while True:
                        try:
                            fcntl.flock(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            break
                        except BlockingIOError:
                            import time
                            time.sleep(0.1)
                            lockcount += 1
                            if lockcount > 50:
                                raise RuntimeError("Unable to acquire lock")
                    # Read existing tasks
                    alltasks = []
                    try:
                        with open("task.xml", "r") as tr:
                            alltasks = tr.readlines()
                    except FileNotFoundError:
                        alltasks = []

                    TASKCOUNT = 0
                    for line in alltasks:
                        line = line.rstrip("\n")
                        if not line:
                            continue
                        parts = line.split(":")
                        if parts:
                            try:
                                TASKCOUNT = int(parts[0])
                            except Exception:
                                pass
                    TASKCOUNT += 1

                    # Append new task line
                    with open("task.xml", "a") as TASK:
                        if task.lower().endswith('.par'):
                            if program.lower().endswith('.sas'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:PAR:{taskdir}:sas.exe -noterminal -sysin {program} -log {tasklog} -print {tasktxt}\n")
                            elif program.lower().endswith('.r'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:PAR:{taskdir}:R.exe CMD BATCH --no-save --no-restore {program} {taskout}\n")
                            elif program.lower().endswith('.py'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:PAR:{taskdir}:python.exe {program} {taskout} {taskerr}\n")
                        else:
                            if program.lower().endswith('.sas'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:SAS:{taskdir}:sas.exe -noterminal -sysin {program} -log {tasklog} -print {tasktxt}\n")
                            elif program.lower().endswith('.r'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:RRR:{taskdir}:R.exe CMD BATCH --no-save --no-restore {program} {taskout}\n")
                            elif program.lower().endswith('.py'):
                                TASK.write(f"{TASKCOUNT}:{usrid}:PYN:{taskdir}:python.exe {program} {taskout} {taskerr}\n")

                    # chmod 0666 on task.xml (best-effort)
                    try:
                        os.chmod("task.xml", 0o666)
                    except Exception:
                        pass

                    # write parm file
                    parm_name = f"parm{TASKCOUNT}.xml"
                    with open(parm_name, "w") as PARM:
                        if program.lower().endswith('.sas'):
                            PARM.write(f"%let usrid={usrid};\n")
                            PARM.write(f"%let usremail={usremail};\n")
                            basedir1 = basedir[:-1] if basedir.endswith("/") else basedir
                            PARM.write(f"%let basedir={basedir1};\n")
                            for key in form.keys():
                                if key.lower().startswith("parm"):
                                    PARM.write(f"%let {key}={form.getfirst(key)};\n")
                        elif program.lower().endswith('.r'):
                            PARM.write(f"setwd(\"../{taskdir}\");\n")
                            PARM.write(f"usrid <- \"{usrid}\";\n")
                            PARM.write(f"usremail <-\"{usremail}\";\n")
                            for key in form.keys():
                                if key.lower().startswith("parm"):
                                    PARM.write(f"{key} <- \"{form.getfirst(key)}\";\n")
                        elif program.lower().endswith('.py'):
                            PARM.write(f"usrid = \"{usrid}\"\n")
                            PARM.write(f"usremail = \"{usremail}\"\n")
                            for key in form.keys():
                                if key.lower().startswith("parm"):
                                    PARM.write(f"{key} = \"{form.getfirst(key)}\"\n")

                    try:
                        os.chmod(parm_name, 0o666)
                    except Exception:
                        pass

                    # unlock
                    fcntl.flock(lock_fp, fcntl.LOCK_UN)
                    lock_fp.close()
                except Exception as e:
                    print('<tr><td><b>Error submitting task: {0}</b></td></tr>'.format(esc(str(e))))
                    # if lockfile opened, attempt to release
        # finish page
        print("</table>\n</table><br>\n")
        print('<table cellspacing=0 cellpadding=0 width=100% border=0>')
        print('    <tr><td bgcolor=#dbe6e0 align=center><br>All Rights Reserved</td></tr>')
        print('    <tr><td bgcolor=#dbe6e0 align=center><br></td></tr>')
        print('</table>\n</center>\n</body></html>')
    except Exception:
        # If anything goes horribly wrong, show simple traceback for debugging
        print_http_headers()
        print("<pre>")
        traceback.print_exc()
        print("</pre>")

if __name__ == "__main__":
    main()




