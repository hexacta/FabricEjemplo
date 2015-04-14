
Fabric
======

Fabric_ es una librería y aplicación de línea de comando implementada en Python, que permite automatizar tareas de administración de sistemas y deployment de aplicaciones. Además de poder ejecutar estas tareas localmente, Fabric permite la ejecución de las mismas en forma remota a través de SSH.

.. _Fabric: http://www.fabfile.org/

Fabric permite realizar una gran variedad de tareas, pero resumidamente podemos simplificarlo en estas tres:

1. Ejecutar comandos remotos a través de ssh
2. Descargar y subir archivos desde y hacia las máquinas remotas
3. Solicitar datos al usuario
  
Casos de uso:

- Sistematizar el proceso de deploymente de una aplicación (puede no ser una aplicación Python)
- Automatizar tareas comunes de administración de sistemas:
  
  - instalación de aplicaciones
  - cambios de configuración
  - creación de usuarios
  - etc, etc, etc
  
Instalación
-----------

Si tenemos instalado ``pip`` en nuestro sistema, podemos instalar Fabric ejecutando

.. code-block:: console

    $ pip install fabric

Otra opción es usar el Administrador de paquetes correspondiente a nuestro sistema. Por ejemplo en ubuntu, 

.. code-block:: console

    $ sudo apt-get install fabric

.. warning:: En algunos sistemas el paquete fabric puede aparecer con el nombre python-fabric


Componentes
-----------

Los dos componentes principales de Fabric son el archivo **fabfile.py** y la utilidad de línea de comando **fab**.

El archivo **fabfile.py** es un módulo de Python que contiene la definición de las tareas que vamos a ejecutar. El comando **fab** se utilizará para ejecutar estas tareas.

Por ejemplo, un simple hola mundo

.. code-block:: python

    def saludo(nombre="Mundo"):
        print "Hola {nombre}!".format(nombre=nombre)

Podemos ejecutarlo de la siguiente forma

.. code-block:: console

    $ fab saludo:nombre=Santiago
    Hola Santiago!

    Done.


En este caso estamos ejecutando la tarea ``saludo`` pasándole como parémetro ``nombre`` el valor ``Santiago``.

Ejecución de comandos remotos
-----------------------------
Lo que hace a Fabric tan poderoso es su excelente integración con SSH, la cual nos permite ejecutar comandos remotos de una forma simple y clara.

Para eso, Fabric nos provee de un conjunto de `operaciones básicas <http://docs.fabfile.org/en/1.10/api/core/operations.html>`_  que describiremos a continuación. Para testear estas operaciones iniciamos un servidor utilizando la configuración de Vagrant que adjuntamos. 

run : 
    Se utiliza para ejecutar un comando remoto. En el siguiente ejemplo podemos ver como obtener información de un sistema 

    .. code-block:: python
    
        from fabric.api import run, task

        @task
        def system_info():
            current_remote_directory = run("pwd")
            print "Current remote directory: " + current_remote_directory

            result = run("uname -a")
            if result.succeeded:
                print "Succeeded"
            else:
                print "Error conecting to hosts"

    Podemos ejecutar esta tarea en un servidor remoto, especificando su ip y el usuario que ejecutará los comandos
        
    .. code-block:: console
      
        $ fab system_info -H 192.168.0.2 -u vagrant  

    .. note:: al ejecutar el comando anterior se nos pedirá que ingresemos el password del usuario `vagrant`. Como se ve, la ejecución de comando permite la interacción entre el usuario que lo lanzó y el servidor remoto.    
    

sudo : 
    Similar a `run` pero permite ejecutar el comando con permisos de superusuario

    .. code-block:: python
    
        @task
        def create_app_dir(appname="my_app"):
            with settings(warn_only=True):
                result = sudo("mkdir /var/www/" + appname)
            
            if result.failed:
                print "mkdir exit code: " + str(result.return_code)
            
            sudo("ls -l /var/www")

    El comando anterior crear el directorio con el nombre que le especifiquemos en el path ``/var/www/`` (arrojando un warning si el mismo ya existe) y luego lista los archivos. Como en el caso anterior podemos ejecutarlo con:

    .. code-block:: console
        
        $ fab create_app_dir:appname="arsat" -H 192.168.0.2 -u vagrant

    .. note:: si en el script anterior utilizábamos ``run`` en lugar de ``sudo`` el comando fallaría en crear el directorio ya que no tenemos permisos para escribir en ``/var/www``.


local : 
    Se utiliza para correr un comando en la máquina local.

    .. code-block:: python
    
        @task
        def compress_current_local_dir():
            local('ls -al')
            with(lcd("../")):
                local("tar --exclude='.*' -cvf fabric.tar fabric ")

    En el ejemplo estamos listando los archivos del directorio actual y luego estamos comprimiendo el mismo. El comando ``lcd`` nos permite movernos localmente entre directorios.

put :
    Este comando permite copiar un archivo de nuestra máquina local a la máquina remota

    .. code-block:: python
    
        @task
        def upload_compressed_file():
            with(lcd("../")):
                put('fabric.tar', "/var/www/fabric.tar", use_sudo=True)

            sudo("ls -al /var/www/ | grep fabric.tar" )

    En este caso, creamos una tarea que nos permite subir el archivo que comprimimos en el paso anterior a nuestro servidor remoto. 

get : 
    Se utiliza para descargar un archivo de la máquina remota

    .. code-block:: python
    
        @task
        def download_apache_logs(logs_folder_name="apache_logs"):
            if not os.path.exists(logs_folder_name):
                os.mkdir(logs_folder_name)
            get(remote_path="/var/log/apache2/access.log", 
                local_path=logs_folder_name, use_sudo=True)
            get(remote_path="/var/log/apache2/error.log", 
                local_path=logs_folder_name, use_sudo=True)

    Esta tarea nos permite descargar los logs de apache y guardarlos en una carpeta local. 

    .. warning:: si en la carpeta local ya existe un archivo con ese nombre, el archivo será sobreescrito.
    
prompt :
    Consulta al usuario (el que está corriendo el script de Fabric), para que ingrese información requerida por el script

    .. code-block:: python
    
        @task
        def configure_app():
            port_number = prompt("Insert application port", default=8080, validate=int)
            
            folder_name = prompt("Introduce folder name", default="arsat")
            with settings(warn_only=True):
                result = sudo("mkdir /var/www/" + folder_name)
            
            sudo("ls -l /var/www")
        
    La tarea anterior nos permite ingresar el nombre de la carpeta donde instalaremos nuestra aplicación y el puerto en el que se ejecutará la misma.
    

reboot : 
    Se utiliza para reiniciar el sistema remoto

    .. code-block:: python

        YES_ANSWER = "yes"

        @task
        def reboot_system():
            reboot_answer = prompt("You have to reboot your system. Do you want to reboot now?", default=YES_ANSWER)
            if reboot_answer.tolower() == YES_ANSWER:
                reboot(wait=30)
            else:
                print "Remember to reboot manually"


Otras funciones y utilidades
----------------------------
Algunas cosas más que ofrece Fabric:

`Context Managers`_ : 
    Permiten definir ciertos contextos en los que se ejecuta un comando. Por ejemplo, podemos definir variables de entorno, movernos a un directorio, omitir errores de ejecución, etc

`Manejo de archivos`_ : 
    Provee un conjunto de funciones para el manejo de archivos remotos. Entre otras cosas permite:

    - Chequear si un archivo existe
    - Comentar o descomentar parte del mismo
    - Agregar información al final o reemplazar parte del mismo
    - Subir un archivo a partir de un template


.. _`Context Managers` : http://docs.fabfile.org/en/1.10/api/core/context_managers.html
.. _`Manejo de archivos` : http://docs.fabfile.org/en/1.10/api/contrib/files.html


Cómo lo utilizamos:
-------------------

Fabric fue utilizado en el proyecto FOP-ARSAT para crear los scripts de instalación y actualización de nuestra aplicación. Haciendo uso de esta librería, desarrollamos un script que le permitía al cliente tener instalada y configurada la aplicación en sus propios servidores, en cuestión de minutos y con una mínima configuración.

Además, utilizamos Fabric para definir tareas propias y recurrentes dentro del proyecto, por ejemplo:
 
* empaquetado de la aplicación
* deploy en servidores de Integración contínua
* deploy en servidores de Pruebas


Links útiles
------------

- `Documentación oficial`_
- `Tutorial oficial`_
- `Tutorial rápido`_  


.. _`Documentación oficial` : http://docs.fabfile.org/en/1.10/
.. _`Tutorial oficial` : http://docs.fabfile.org/en/1.10/tutorial.html
.. _`Tutorial rápido` : https://www.digitalocean.com/community/tutorials/how-to-use-fabric-to-automate-administration-tasks-and-deployments
