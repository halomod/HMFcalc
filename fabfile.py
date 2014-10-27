'''
Created on Jun 14, 2013

@author: Steven
'''

from fabric.api import env, settings, local, run, abort, cd, put, sudo
from fabric.contrib.console import confirm
from os.path import join

username = "hmf"
home_dir = join('/home', username)
env.hosts = [username + '@icrar-nix-023.icrar.org']
app_name = 'HMFcalc'
proj_name = "HMF"  # where the settings file is
code_dir = join(home_dir, app_name)
projdir = join(code_dir, proj_name)  # where the settings file is
def collect():
    local("python manage.py collectstatic --noinput")
def test():
    with settings(warn_only=True):
        result = local('./manage.py test {0}'.format(app_name), capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -A && git commit")

def push():
    local("git push")

def prepare_deploy():
    collect()
    test()
    commit()
    push()

def deploy():
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone https://github.com/steven-murray/HMFcalc.git %s" % code_dir)

    put(join(proj_name, "secret_settings.py"), projdir)

    with cd(code_dir):
        run("git fetch --all")
        run("git reset --hard origin/master")
        run("python change_prod_settings.py")
        run("touch {0}".format(join(projdir, "wsgi.py")))

    # Update hmf from git repo
    with cd(join(home_dir, "hmf")):
        run("git fetch --all")
        run("git reset --hard origin/master")
        run("python setup.py install")

    # Update default model
    with cd(join(code_dir, "static/initialdata")):
        run("python make_initial.py")

    sudo("chmod 777 {0} -R".format(home_dir))

def pd():
    prepare_deploy()
    deploy()

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
    sudo("yum install --assumeyes glibc-devel")
    sudo("yum install --assumeyes gcc-c++")

def python_install():
    with cd(home_dir):
        run("wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz")
        run("tar xf Python-2.7.8.tgz")
        run("rm Python-2.7.8.tgz")

    with cd(join(home_dir, "Python-2.7.8")):
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

    with cd(home_dir):
        sudo("/opt/python2.7/bin/easy_install pip")
        sudo("/opt/python2.7/bin/pip install virtualenv")
        run("/opt/python2.7/bin/virtualenv --distribute hmfenv")
        run("source hmfenv/bin/activate")
        run("echo 'source $HOME/hmfenv/bin/activate'>>$HOME/.bashrc")

def python_packages():
    with cd(home_dir):
        hmfenvpip = join(home_dir, 'hmfenv/bin/pip')
        run(hmfenvpip + " install numpy==1.8.0")
        run(hmfenvpip + " install scipy")
        run(hmfenvpip + " install matplotlib==1.3.1")
        run(hmfenvpip + " install pandas")
        run(hmfenvpip + " install cosmolopy")
        run(hmfenvpip + " install django==1.6")
#         run(hmfenvpip + " install django-tabination")
        run(hmfenvpip + " install django-crispy-forms==1.4.0")
        run(hmfenvpip + " install django-analytical")
#         run(hmfenvpip + " install django-floppyforms")

        try:
            run("git clone https://github.com/steven-murray/pycamb.git")
        except:
            pass

        try:
            run("git clone https://github.com/steven-murray/django-active-menu.git")
        except:
            pass

    with cd(join(home_dir, 'pycamb')):
        run("{0} setup.py install --get=http://camb.info/CAMB_Mar13.tar.gz".format(join(home_dir, "hmfenv/bin/python")))

    with cd(home_dir):
        try:
            run("git clone https://github.com/steven-murray/hmf.git")
        except:
            pass

    with cd(join(home_dir, "django-active-menu")):
        run("{0} setup.py install".format(join(home_dir, "hmfenv/bin/python")))

    with cd(join(home_dir, "hmf")):
        run("{0} setup.py install".format(join(home_dir, "hmfenv/bin/python")))

def mod_wsgi():
    with cd(home_dir):
        run("wget https://github.com/GrahamDumpleton/mod_wsgi/archive/3.5.tar.gz")
        run("tar zxf 3.5.tar.gz")

    with cd(join(home_dir, "/mod_wsgi-3.5")):
        run("./configure")
        run("make")
        sudo("make install")

def configure_apache():

    config_file = \
"""    
NameVirtualHost *:80
WSGISocketPrefix /var/run/wsgi
WSGIPythonPath {0}:{1}

<VirtualHost *:80>
    WSGIScriptAlias / {2}
    
    WSGIDaemonProcess hmf.icrar.org python-path={0}:{1}

    WSGIProcessGroup hmf.icrar.org

    WSGIApplicationGroup %%{GLOBAL}

    Alias /static/ {3}
    <Directory {4}>

        Order deny,allow

        Allow from all

    </Directory>
</VirtualHost>
""".format(code_dir, join(home_dir, "hmfenv/lib/python2.7/site-packages"),
           join(projdir, "wsgi.py"), join(code_dir, "static/"), projdir)

    sudo('echo "{0}" > /etc/httpd/conf.d/hmf.conf'.format(config_file))

    # Now need to add "LoadModule wsgi_module modules/mod_wsgi.so" to httpd.conf
    sudo('echo "LoadModule wsgi_module modules/mod_wsgi.so">/etc/httpd/conf.d/wsgi.conf')

    # Then restart the server
    sudo("service httpd restart")

def configure_mpl():
    with cd(home_dir):
        try:
            run("mkdir .config")
            run("mkdir .config/matplotlib")
            run("touch .config/matplotlib/matplotlibrc")
        except:
            pass
    run("echo 'ps.useafm : True'>>$HOME/.config/matplotlib/matplotlibrc")
    run('echo "pdf.use14corefonts : True" >> $HOME/.config/matplotlib/matplotlibrc')
    run('echo "text.usetex: True" >> $HOME/.config/matplotlib/matplotlibrc')

def setup_cron():

    sudo('''echo "# This is to do a heartbeat check of the webapp
0-59/5 * * * * {0} {1}">/var/spool/cron/{2}'''.format(join(home_dir, "hmfenv/bin/python"),
                                                     join(code_dir, "check_alive.py"), username))
    sudo('''echo "# This is to clear the session every day
0 0 * * * {0} {1} clearsessions">/var/spool/cron/{2}''' .format(join(home_dir, "hmfenv/bin/python"),
                                                                join(code_dir, "manage.py"), username))

def change_bashrc():
    run('echo "export MY_DJANGO_ENV=production">>$HOME/.bashrc')
    run("source ~/.bashrc")

def hack_selinux():
    sudo("echo 0 > /selinux/enforce")

def setup_server():
    # First do all the yum installs
    yum_installs()

    # Now install python 2.7.4
    python_install()

    # Install the python virtualenv and setup tools
    python_dist_tools()

    # Install python packages required
    python_packages()

    # Install mod_wsgi
    mod_wsgi()

    # Configure apache
    configure_apache()

    # Configure matplotlib
    configure_mpl()

    # Configure the environment as a production env
    change_bashrc()

    # Setup cron
    setup_cron()

    # Make SElinux be nice to us
    hack_selinux()

    # Run the deploy
    deploy()

