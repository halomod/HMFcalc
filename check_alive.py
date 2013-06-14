#! python

'''
Created on Jun 14, 2013

@author: Steven
'''
import urllib2
import StringIO
import sys
from subprocess import call

response = urllib2.urlopen("http://hmf.icrar.org", timeout=5)
#web_page = response.read()

for line in response.readlines():
    if "<a href='hmf_finder/form/create/' class='btn btn-primary btn-large'>Begin!</a>" in line:
        print "found line"
        sys.exit()

print "Web-page down, restarting"
call(["service", "httpd", "restart"])

