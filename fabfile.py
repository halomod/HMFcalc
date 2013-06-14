'''
Created on Jun 14, 2013

@author: Steven
'''

from fabric.api import env, settings, local, run, abort, cd
from fabric.contrib.console import confirm

env.hosts = ['hmf@hmf-test.icrar.org']

def test():
    with settings(warn_only=True):
        result = local('./manage.py test hmf_finder', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -p && git commit")

def push():
    local("git push")

def prepare_deploy():
#    test()
    commit()
    push()

def deploy():
    code_dir = '/home/hmf/HMFcalc/'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone https://github.com/steven-murray/HMFcalc.git %s" % code_dir)
    with cd(code_dir):
        run("git pull")
        run("pip install hmf --upgrade")
        run("touch wsgi.py")


def yum_installs():
    run("yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel")
    run("yum install blas.x86_64")
    run("yum install blas-devel.x86_64")
    run("yum install lapack.x86_64")
    run("yum install lapack-devel.x86_64")
    run("yum install httpd.x86_64")
    run("chkconfig --levels 235 httpd on")
    run("yum install httpd-devel.x86_64")
    run("yum install libpng-devel.x86_64")

def python_install():
    with cd("/home/hmf/"):
        run("wget http://python.org/ftp/python/2.7.4/Python-2.7.4.tar.bz2")
        run("tar xf Python-2.7.4.tar.bz2")
    with cd("/home/hmf/Python-2.7.4"):
        run("mkdir -p /opt/python2.7/lib")
        run("./configure --prefix=/opt/python2.7 --with-threads --enable-shared LDFLAGS='-Wl,-rpath /opt/python2.7/lib'")

        run("make && make altinstall")

    with cd("/home/hmf"):
        run("ln -s /opt/python2.7/bin/python /usr/bin/python2.7")
        run("echo '/opt/python2.7/lib'>> /etc/ld.so.conf.d/opt-python2.7.conf")
        run("ldconfig")

def python_dist_tools():
    with cd("/home/hmf/"):
        run("wget http://pypi.python.org/packages/source/d/distribute/distribute-0.6.39.tar.gz")
        run("tar xf distribute-0.6.39.tar.gz")

    with cd("/home/hmf/distribute-0.6.39"):
        run("/usr/bin/python2.7 setup.py install")

    with cd('/home/hmf/'):
        run("/opt/python2.7/bin/easy_install pip")
        run("/opt/python2.7/bin/pip install virtualenv")
        run("virtualenv --distribute hmfenv")
        run("source hmfenv/bin/activate")
        run("echo 'source $HOME/hmfenv/bin/activate'>>$HOME/.bashrc")

def python_packages():
    with cd("/home/hmf"):
        run("pip install numpy")
        run("pip install scipy")
        run("pip install matplotlib")
        run("pip install SciTools")
        run("pip install pandas")
        run("pip install cosmolopy")
        run("pip install django")
        run("pip install django-tabination")
        run("pip install django-crispy-forms")
        run("pip install django-analytical")
        run("pip install django-floppyforms")
        run("pip install hmf")

        run("git clone https://github.com/steven-murray/pycamb.git")

    with cd('home/hmf/pycamb'):
        run("python setup.py install")

def mod_wsgi():
    with cd("/home/hmf/"):
        run("wget modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz")
        run("tar zxf mod_wsgi-3.4.tar.gz")

    with cd("home/hmf/mod_wsgi-3.4"):
        run("./configure")
        run("make")
        run("make install")

def configure_apache():

    config_file = \
"""    
NameVirtualHost *:80
WSGISocketPrefix /var/run/wsgi
WSGIPythonPath /root/HMFcalc:/root/hmfenv/lib/python2.7/site-packages

<VirtualHost *:80>
    WSGIScriptAlias / /root/HMFcalc/HMF/wsgi.py
    
    WSGIDaemonProcess hmf-test.icrar.org python-path=/home/hmf/HMFcalc:/home/hmf/hmfenv/lib/python2.7/site-packages

    WSGIProcessGroup hmf-test.icrar.org

    WSGIApplicationGroup %{GLOBAL}

    <Directory /root/HMCcalc/HMF>

        Order deny,allow

        Allow from all

    </Directory>
</VirtualHost>
"""
    with open("/etc/httpd/conf.d/hmf.conf") as f:
        f.write(config_file)

    #Now need to add "LoadModule wsgi_module modules/mod_wsgi.so" to httpd.conf

    #Then restart the server
    run("service httpd restart")

def setup_server():
    # First do all the yum installs
    yum_installs()

    #Now install python 2.7.4
    python_install()

    #Install the python virtualenv and setup tools
    python_dist_tools()

    #Install python packages required
    python_packages()

    #Install mod_wsgi
    mod_wsgi()

    #Configure apache
    configure_apache()

    #Run the deploy
    deploy()

