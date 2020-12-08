# DEPLOYMENT CHECKLIST

## ALLOWED HOSTS
In settings.py, change the following to reflect the desired hosts:

```
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] 
```


## SETTINGS
The settings for RM are set in the environment. 
The settings.py picks them up by using 
```
X = os.environ.get('X', default='Y')
```
For development see:
- local_settings.sh 
- docker-compose.yml

#### SECRET_KEY
Generate a new one for every env

##### DEBUG
Set to False for production env
This is NOT a logging setting, but a Django internal 
setting helping developers see what's going on.

#### ENVIRONMENT
This is a switch for several settings, see
config/settings.py. It defaults to prod to be sure that the
most secure setting is used when de property 
can not be found.

Examples used:
- dev-local
- dev-docker
- acc
- prod
   
#### Database
RM uses PostgreSQL database (12.5, but lower will probably do 
as well). The user must have create access rights.

*Database settings:*

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_HOST

?? OpenShift settings ??

#### Compile static files using Whitenoise
see: http://whitenoise.evans.io/en/stable/django.html

WhiteNoise allows your web app to serve its own static files, 
making it a self-contained unit that can be deployed anywhere 
without relying on nginx, Amazon S3 or any other external 
service. (Especially useful on Heroku, OpenShift and other PaaS 
providers.)


#### Server
Default Django comes with RunServer for development. For production
this can be changed into Gunicorn, giving a performance improvement.
But may we need another, asynchronous-friendly webserver.
See https://docs.djangoproject.com/en/3.1/howto/deployment/

For the moment we let it run with runserver.


#### Post check
See Django's recommendations, should be empty:
```
python manage.py check --deploy
```