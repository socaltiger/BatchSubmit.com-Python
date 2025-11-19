#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import sys

def parse_form():
    """Parse form input."""
    form = cgi.FieldStorage()
    params = {key: form.getvalue(key) for key in form.keys()}
    return params

def main_page(params):
    """Output the main HTML page."""
    print("Content-Type: text/html\n")

    # Begin HTML
    print("""<!DOCTYPE html>
<html>
<head>
<title>Help</title>
</head>
<body bgcolor="#f8f8f8">
<center>
""")

    # Header Table
    print("""
<table cellspacing="0" cellpadding="4" width="100%" border="1">
  <tr>
    <td bgcolor="#dbe6e0" align="center"><b>Help Information</b></td>
  </tr>
</table>
<br>
""")

    # Main help section (copied from original Perl output)
    print("""
<table cellspacing="0" cellpadding="4" width="100%" border="1">
  <tr>
    <td bgcolor="#FFFFFF">
      <b>General Help</b><br><br>
      This page displays help information for the system.<br><br>
    </td>
  </tr>
</table>
<br>
""")

    # Footer
    print("""
<table cellspacing="0" cellpadding="0" width="100%" border="0">
  <tr><td bgcolor="#dbe6e0" align="center"><br>All Rights Reserved</td></tr>
  <tr><td bgcolor="#dbe6e0" align="center"><br></td></tr>
</table>

</center>
</body>
</html>
""")

def main():
    params = parse_form()
    main_page(params)

if __name__ == "__main__":
    main()
