'''
Created on Jun 14, 2013

@author: Steven
'''

from fabric.api import env, settings, local, run, abort, cd, put, sudo
from fabric.contrib.console import confirm


username = "hmf"
home_dir = '/home/' + username + '/'
env.hosts = [username + '@180.149.251.183']
app_name = 'HMFcalc'
code_dir = home_dir + app_name + '/'

def test():
    with settings(warn_only=True):
        result = local('./manage.py test hmf_finder', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -A && git commit")

def push():
    local("git push")

def prepare_deploy():
    test()
    commit()
    push()

def deploy():
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone https://github.com/steven-murray/HMFcalc.git %s" % code_dir)

    put("HMF/secret_settings.py", code_dir + "HMF/")
    with cd(code_dir):
        run("git fetch --all")
        run("git reset --hard origin/master")
        #The following line updates the hmf package to the latest on pip. It may not work,
        #I'll have to look at making it the full url, or perhaps doing it by git with a special branch.
        run("pip install hmf --upgrade")
        run("%shmfenv/bin/python change_prod_settings.py" % (home_dir))
        run("%shmfenv/bin/python manage.py collectstatic --noinput")
        run("touch HMF/wsgi.py")
    sudo("chmod 777 %s -R" % (home_dir))

def yum_installs():
    sudo("yum install --assumeyes git")
    sudo("yum install --assumeyes zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel")
    sudo("yum install --assumeyes blas.x86_64")
    sudo("yum install --assumeyes blas-devel.x86_64")
    sudo("yum install --assumeyes lapack.x86_64")
    sudo("yum install --assumeyes lapack-devel.x86_64")
    sudo("yum install --assumeyes httpd.x86_64")
    sudo("chkconfig --levels 235 httpd on")
    sudo("yum install --assumeyes httpd-devel.x86_64")
    sudo("yum install --assumeyes libpng-devel.x86_64")
    # sudo("yum install --assumeyes python27 python27-devel")

def python_install():
    with cd(home_dir):
        run("wget http://python.org/ftp/python/2.7.4/Python-2.7.4.tar.bz2")
        run("tar xf Python-2.7.4.tar.bz2")
    with cd(home_dir + "/Python-2.7.4"):
        sudo("mkdir -p /opt/python2.7/lib")
        sudo("./configure --prefix=/opt/python2.7 --with-threads --enable-shared LDFLAGS='-Wl,-rpath /opt/python2.7/lib'")

        sudo("make && make altinstall")

    with cd(home_dir):
        sudo("ln -s /opt/python2.7/bin/python /usr/bin/python2.7")
        sudo("echo '/opt/python2.7/lib'>> /etc/ld.so.conf.d/opt-python2.7.conf")
        sudo("ldconfig")

def python_dist_tools():
    with cd(home_dir):
        run("wget http://pypi.python.org/packages/source/d/distribute/distribute-0.6.39.tar.gz")
        run("tar xf distribute-0.6.39.tar.gz")

    with cd(home_dir + "distribute-0.6.39"):
        sudo("/opt/python2.7/bin/python2.7 setup.py install")
        #sudo("python2.7 setup.py install")

    with cd(home_dir):
        sudo("/opt/python2.7/bin/easy_install pip")
        sudo("/opt/python2.7/bin/pip install virtualenv")
        #sudo("easy_install-2.7 pip")
        #run("easy_install-2.7 virtualenv")
        run("/opt/python2.7/bin/virtualenv --distribute hmfenv")
        run("source hmfenv/bin/activate")
        run("echo 'source $HOME/hmfenv/bin/activate'>>$HOME/.bashrc")

def python_packages():
    with cd(home_dir):
        hmfenvpip = home_dir + 'hmfenv/bin/pip'
        run(hmfenvpip + " install numpy")
        run(hmfenvpip + " install scipy")
        run(hmfenvpip + " install matplotlib")
        run(hmfenvpip + " install SciTools")
        run(hmfenvpip + " install pandas")
        run(hmfenvpip + " install cosmolopy")
        run(hmfenvpip + " install django")
        run(hmfenvpip + " install django-tabination")
        run(hmfenvpip + " install django-crispy-forms")
        run(hmfenvpip + " install django-analytical")
        run(hmfenvpip + " install django-floppyforms")


        run("git clone https://github.com/steven-murray/pycamb.git")

    with cd(home_dir + 'pycamb'):
        run(home_dir + "hmfenv/bin/python setup.py install")

    with cd(home_dir):
        run(hmfenvpip + " install hmf")
def mod_wsgi():
    with cd(home_dir):
        run("wget modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz")
        run("tar zxf mod_wsgi-3.4.tar.gz")

    with cd(home_dir + "/mod_wsgi-3.4"):
        run("./configure")
        run("make")
        sudo("make install")

def configure_apache():

    config_file = \
"""    
NameVirtualHost *:80
WSGISocketPrefix /var/run/wsgi
WSGIPythonPath %s:%shmfenv/lib/python2.7/site-packages

<VirtualHost *:80>
    WSGIScriptAlias / %sHMF/wsgi.py
    
    WSGIDaemonProcess hmf-test.icrar.org python-path=%s:%shmfenv/lib/python2.7/site-packages

    WSGIProcessGroup hmf-test.icrar.org

    WSGIApplicationGroup %%{GLOBAL}

    Alias /static/ %sstatic/
    <Directory %sHMF>

        Order deny,allow

        Allow from all

    </Directory>
</VirtualHost>
""" % (code_dir, home_dir, code_dir, code_dir, home_dir, code_dir, code_dir)

    sudo('echo "%s" > /etc/httpd/conf.d/hmf.conf' % (config_file))
    #with open("/etc/httpd/conf.d/hmf.conf") as f:
    #    f.write(config_file)

    #Now need to add "LoadModule wsgi_module modules/mod_wsgi.so" to httpd.conf
    sudo('echo "LoadModule wsgi_module modules/mod_wsgi.so">/etc/httpd/conf.d/wsgi.conf')
    #with open("/etc/httpd/conf.d/wsgi.conf") as f:
    #    f.write("LoadModule wsgi_module modules/mod_wsgi.so")

    #Then restart the server
    sudo("service httpd restart")

def configure_mpl():
    run("echo 'ps.useafm : True'>>$HOME/.matplotlib/matplotlibrc")
    run('echo "pdf.use14corefonts : True" >> $HOME/.matplotlib/matplotlibrc')
    run('echo "text.usetex: True" >> $HOME/.matplotlib/matplotlibrc')

def setup_cron():

    sudo('''echo "# This is to do a heartbeat check of the webapp
0-59/5 * * * * %shmfenv/bin/python %scheck_alive.py">/var/spool/cron/%s''' % (home_dir, code_dir, username))
    sudo('''echo "# This is to clear the session every day
0 0 * * * %shmfenv/bin/python %smanage.py clearsessions">/var/spool/cron/%s''' % (home_dir, code_dir, username))

def change_bashrc():
    run('echo "export MY_DJANGO_ENV=production">>$HOME/.bashrc')
    run("source ~/.bashrc")

def hack_selinux():
    sudo("echo 0 > /selinux/enforce")

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

    #Configure matplotlib
    configure_mpl()

    #Configure the environment as a production env
    change_bashrc()

    #Setup cron
    setup_cron()

    #Make SElinux be nice to us
    hack_selinux()

    #Run the deploy
    deploy()

