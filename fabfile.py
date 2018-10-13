from fabric.api import env, run
from fabric.operations import sudo
import json
import os

CONF = json.loads(open('configs.json').read())

env.user = CONF["USERNAME"]
env.password = CONF["PASSWORD"]
env.hosts = CONF["IPADDRESS"]
env.port = CONF["PORT"]


def deploy():
    source_folder = CONF["ROOTDIR"]

    run("""cd {} &&
    git fetch &&
    git reset --hard origin/master &&
    git pull""".format(source_folder))
    run("""
        cd {} &&
        pip3 install -r requirements.txt &&
        python3 manage.py collectstatic --noinput &&
        python3 manage.py migrate
        """.format(source_folder))
    sudo("""cd {} &&
    systemctl restart ticket.service &""".format(source_folder))
    sudo('service nginx reload')
