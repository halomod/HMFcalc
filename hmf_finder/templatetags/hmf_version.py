'''
Created on Apr 10, 2013

@author: Steven
'''

from django import template

register = template.Library()

def current_version():
    from hmf.Perturbations import version
    
    return version

register.simple_tag(current_version)