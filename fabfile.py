
from fabric.api import run, task, sudo, settings, local, lcd, put, get, prompt, reboot
from fabric.context_managers import lcd
import os.path


@task
def saludo(nombre="Mundo"):
    print "Hola {nombre}!".format(nombre=nombre)


@task
def system_info():
    current_remote_directory = run("pwd")
    print "Current remote directory: " + current_remote_directory

    result = run("uname -a")
    if result.succeeded:
        print "Succeeded"
    else:
        print "Error conecting to hosts"

@task
def create_app_dir(appname="my_app"):
    with settings(warn_only=True):
        result = sudo("mkdir /var/www/" + appname)
    
    if result.failed:
        print "mkdir exit code: " + str(result.return_code)
    
    sudo("ls -l /var/www")


@task
def compress_current_local_dir():
    local('ls -al')
    with(lcd("../")):
        local("tar --exclude='.*' -cvf fabric.tar fabric")


@task
def upload_compressed_file():
    with(lcd("../")):
        put('fabric.tar', "/var/www/fabric.tar", use_sudo=True)

    sudo("ls -al /var/www/ | grep fabric.tar" )


@task
def download_apache_logs(logs_folder_name="apache_logs"):
    if not os.path.exists(logs_folder_name):
        os.mkdir(logs_folder_name)
    get(remote_path="/var/log/apache2/access.log", local_path=logs_folder_name, use_sudo=True)
    get(remote_path="/var/log/apache2/error.log", local_path=logs_folder_name, use_sudo=True)


@task
def configure_app():
    port_number = prompt("Insert application port:", default=8080, validate=int)
    
    folder_name = prompt("Insert folder name:", default="arsat")
    create_app_dir(folder_name)
        

YES_ANSWER = "yes"


@task
def reboot_system():
    reboot_answer = prompt("You have to reboot your system. Do you want to reboot now?", default=YES_ANSWER)
    if reboot_answer.lower() == YES_ANSWER:
        reboot(wait=30)
    else:
        print "Remember to reboot manually"
