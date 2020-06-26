#! python

"""
Created on Jun 14, 2013

@author: Steven
"""
import urllib.request
from subprocess import call

response = urllib.request.urlopen("http://hmf.icrar.org", timeout=5)

for line in response.readlines():
    if (
        "<a href='hmf_finder/form/create/' class='btn btn-primary btn-large'>Begin!</a>"
        in line
    ):
        print("found line")
        found_line = True
        break

if not found_line:
    print("Web-page down, restarting")
    call(["sudo", "service", "httpd", "restart"])
