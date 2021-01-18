# NPO Resource Manager

## Installation instructions
For local deployment you can run it in 2 ways: 
* in Docker on your pc
* local on your pc

The preferred way is to deploy it in Docker, since all dependencies (python, 
libraries and postgres database) are included in the Docker images. 
Only debugging and accessing the database is harder. 

This README shows how to install the Docker version.

### Installation in Docker on your desktop
Global steps (to be refined later)

#### Install Docker
See [docker.com](https://www.docker.com/products/docker-desktop)

1. Check Docker is installed correctly

    ```bash
    docker -D run hello-world
    ```
   
1. Check Docker permissions
   
   Docker needs access to the folder where the Resource Manager will be installed. This is easiest done by opening
   the Docker desktop application and accept permission request for the (parent) folder where the Resource Manager 
   application will be installed.
1. Create Docker group and add your (computer) user to this group
    
    With adding your computer user to the docker group you don't have to run Docker as root.
    
    On Linux:
    ```bash
    sudo groupadd docker
    sudo gpasswd -a ${USER} docker
    ```
    For Mac, see here how to set up users and groups: 
    [support.apple.com](https://support.apple.com/guide/mac-help/set-up-other-users-on-your-mac-mtusr001/mac)

1. (re)start Docker

#### Install Git
See [git-scm.com](https://git-scm.com/downloads)
   
#### Get the code from GitHub
On the command line, go to the location where the project directory has to be
placed, e.g. /python/django. Clone the repository which will create a subdirectory
'npo-rm' in there.

```
git clone https://github.com/aesset/npo-rm
```

Go into the newly created directory:
```
cd npo-rm
```

#### Choose  the right branch
Available branches:
* master: will be th PROD version, but currently there is no prod, so this is outdated at the moment
* acc: at the moment the latest version, directly deployed to http://npo-rm-acc-npo-resource-manager-acc.apps.cluster.chp4.io/
* dev: development 
    
   Default you're in ```master```. Change branch is done with this command:
   ```
   git checkout <branch>
   ```
#### Start app
```
docker-compose up --build 
```

This first time it will take a while since the base images for Python and 
Postgres have to be downloaded. If all goes well it should end with something 
like:

```
web_1  | [30/Nov/2020 16:46:36] "GET /admin/jsi18n/ HTTP/1.1" 200 3187
web_1  | Watching for file changes with StatReloader
web_1  | Performing system checks...
web_1  | 
web_1  | System check identified no issues (0 silenced).
web_1  | December 01, 2020 - 08:49:29
web_1  | Django version 3.1.3, using settings 'config.settings'
web_1  | Starting development server at http://0.0.0.0:8100/
web_1  | Quit the server with CONTROL-C.
```

#### Create the database tables
Open a new Terminal window for the next steps:
```
docker-compose exec web python manage.py migrate
```

#### Create the admin user
```
docker-compose exec web python manage.py createsuperuser
```

Fill in (these are examples you can change this to something you like)

```
user:            npo-rm-admin
e-mail address:  your@name.com  
password:        secretsSecrets
```

#### Start the app
```
* http://localhost:8100
* http://localhost:8100/admin   -> log in with the user you created 
```

#### Stop the Docker images with the application and database
```    
By pressing CTRL+C in the window where you started the images.
```

## Start and stop the application
From now on you can start and stop the application with the following 
commands executed in the npo-rm/ directory: 

```
docker-compose up         # starts the application with log in foreground
docker-compose up -d      # starts the application in the background
docker-compose up --build # rebuilds and starts the application
docker-compose down       # shuts down the application
docker-compose logs -f    # follow the logging
```
 
## Database location
The database is placed local on your pc. The location depends on the
installation of Docker, but it is something like:

```bash
var/lib/docker/volumes/npo-rm_postgres_data
```

## Upgrade the application
Update the sources: go to the npo-rm directory on the command line and type:
```bash
git pull
```

Start the application, with the build option, maybe not needed, but sometimes it is:
```bash
docker-compose up --build
```

Go to a new commandline window in the npo-rm directory and type:
```bash
docker-compose exec web python manage.py migrate
```
This updates the database with the latest structure changes

## Reinitialize the database
Want to start with a new empty database? Easy! The database is a 'volume' defined in the 
docker-compose. By removing that volume and restart the containers the
database is recreated. After that you run the migrates and create the 
superuser again:

Check the volumes: 
```bash
docker volume ls
DRIVER    VOLUME NAME
local     npo-rm_postgres_data      <-- this is the one
```
If you want to get more info about the volumes:
```bash
docker volume inspect npo<tab> <-- press tab for auto completion
```
Then to remove:
```bash
docker volume rm npo<tab>
```

Start the containers, create the tables and create superuser:
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
Fill in: your admin user credentials npo-rm-admin with password secretSecrets, or something else ;-)

And you're back in business!

## Run tests
```bash
python mangage.py test
```

to see the coverage:

```bash
coverage run --source='.' manage.py test
coverate html
```
And open htmlcov/index.html

## Jira
Also on [aesset.atlassian.net](https://aesset.atlassian.net).

#### Author
- Eelco Aartsen
- [eelco@aesset.nl](mailto:eelco@aesset.nl)
- AESSET IT - The Netherlands
- [www.aesset.nl](https://www.aesset.nl)


