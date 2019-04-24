'''
Created on Apr 10, 2013

@author: Steven
'''


from django import template
import hmf

register = template.Library()


def current_version():
    return hmf.__version__


register.simple_tag(current_version)