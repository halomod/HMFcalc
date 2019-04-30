'''
Created on Apr 10, 2013

@author: Steven
'''

import hmf
from django import template

register = template.Library()


def current_version():
    return hmf.__version__


register.simple_tag(current_version)
