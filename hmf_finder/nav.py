'''
Created on May 1, 2013

@author: Steven
'''

from django_nav import nav_groups, Nav, NavOption


class Params(NavOption):
    name = u'Parameter Defaults'
    view = 'parameters'

class Resources(NavOption):
    name = u'Extra Resources'
    view = 'resources'

class Acknowledgments(NavOption):
    name = u'Acknowledgments'
    view = 'acknowledgments'

class CalculateNew(NavOption):
    name = u'Begin New Calculation'
    view = 'calculate'

    kwargs = {'add':'create'}



# class AddExtra(NavOption):
#    name =u'Add Extra Functions'
#    view = 'calculate'
#
#    kwargs = {'add':'add'}
#    conditional = {'function'}

class Home(Nav):
    name = u'Home'
    view = 'home'

class Info(Nav):
    name = u'Parameter Info'
    view = 'param-discuss'

    options = [Params, Resources, Acknowledgments]

class Calculate(Nav):
    name = u'Calculate'
    view = 'calculate'

    kwargs = {'add':'create'}

    options = [CalculateNew]

nav_groups.register(Calculate)

nav_groups.register(Home)

nav_groups.register(Info)
