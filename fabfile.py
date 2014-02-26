from fabric.api import *
# Default release is 'current'
env.release = 'current'
import os
import cStringIO

fabfile_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir  = os.path.join(fabfile_dir, 'templates/')

def production():
  """Production server settings"""
  env.settings = 'production'
  env.user = 'grupygo'
  env.app = 'grupygo'
  env.path = '/home/%(user)s/sites/%(app)s' % env
  env.hosts = ['grupygo.org']

def setup():
  """
  Setup a fresh virtualenv and install everything we need so it's ready to deploy to
  """
  run('mkdir -p %(path)s; cd %(path)s; /usr/local/bin/virtualenv --no-site-packages .; mkdir releases; mkdir shared; mkdir conf;' % env)
  clone_repo()
  checkout_latest()
  install_requirements()

def deploy():
  """Deploy the latest version of the site to the server and restart nginx"""
  checkout_latest()
  install_requirements()
#  collect_static()
  symlink_current_release()
#  migrate()
  _generate_conf('uwsgi.ini', env, '%(path)s/conf/' % env )
  restart_server()

def _generate_conf(conf_file, variables, output_dir):
  input_file = os.path.join(templates_dir, conf_file)
  output_file = os.path.join(output_dir, conf_file)
  
  conf = ''
  output = cStringIO.StringIO()
  try:
    with open(input_file, 'r') as input:
        for line in input:
          output.write(line % variables)
    conf = output.getvalue()
  finally:
    output.close()
  
  print conf
  with open(output_file, 'w') as output:
    output.write(conf)

  
def collect_static():
  run('cd %(path)s/releases/%(release)s; ../../bin/python manage.py collectstatic --noinput' % env)

def clone_repo():
  """Do initial clone of the git repo"""
  run('cd %(path)s; git clone /home/%(user)s/git/repositories/%(app)s.git repository' % env)

def checkout_latest():
  """Pull the latest code into the git repo and copy to a timestamped release directory"""
  import time
  env.release = time.strftime('%Y%m%d%H%M%S')
  run("cd %(path)s/repository; git pull origin master" % env)
  run('cp -R %(path)s/repository %(path)s/releases/%(release)s; rm -rf %(path)s/releases/%(release)s/.git*' % env)

def install_requirements():
  """Install the required packages using pip"""
  run('cd %(path)s; %(path)s/bin/pip install uwsgi' % env)
  run('cd %(path)s; %(path)s/bin/pip install -r ./releases/%(release)s/requirements.txt' % env)

def symlink_current_release():
  """Symlink our current release, uploads and settings file"""
  with settings(warn_only=True):
    run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' % env)
  run('cd %(path)s; ln -s %(release)s releases/current' % env)
  """ production settings"""
  with settings(warn_only=True):
    run('rm %(path)s/shared/static' % env)
    run('cd %(path)s/releases/current/static/; ln -s %(path)s/releases/%(release)s/static %(path)s/shared/static ' %env)

def migrate():
  """Run our migrations"""
  run('cd %(path)s/releases/current; ../../bin/python manage.py syncdb --noinput --migrate' % env)
  run('cd %(path)s/releases/current; ../../bin/python manage.py migrate' % env)

def rollback():
  """
  Limited rollback capability. Simple loads the previously current
  version of the code. Rolling back again will swap between the two.
  """
  run('cd %(path)s; mv releases/current releases/_previous;' % env)
  run('cd %(path)s; mv releases/previous releases/current;' % env)
  run('cd %(path)s; mv releases/_previous releases/previous;' %env)
  restart_server()

def stop_server():
  """Stop the web server"""
  with settings(warn_only=True):
    sudo('kill -9 `cat /tmp/project-%(user)s_%(app)s_%(settings)s.pid`' % env)
    sudo('rm /tmp/project-%(user)s_%(app)s_%(settings)s.pid /tmp/uwsgi-%(user)s_%(app)s_%(settings)s.sock' % env )

def start_server():
  """Start the web server"""
  run('cd %(path)s/releases/current; %(path)s/bin/uwsgi --ini %(path)s/conf/uwsgi.ini' % env)
  sudo('/etc/init.d/nginx restart')

def restart_server():
  """Restart Server"""
  stop_server()
  start_server()
