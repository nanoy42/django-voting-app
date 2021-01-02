Post-installation and update procedures
=======================================

After the installation or after an update, you may have to perform additional operations.

Migrations
##########

Migrations are all the structural operations on the database. They should be run after an installation.

They should also be run whenever new migrations appears. Migrations can come from :

* migrations from django
* migrations from other dependencies (django-modeltranslations for instance)
* internal migrations.

Migrations should be run when migrating to

* 1.0.0
* 0.1.0

The command to apply migrations is 

.. code-block:: sh

    python src/manage.py migrate

.. note:: Migrations are applied automatically when using docker.

Superuser
#########

Once the installation is finished, you may want to create a super user. You can do it using the command 

.. code-block:: sh

    python src/manage.py createsuperuser

and fill in the requested information.

Statics
#######

In production statics are **NOT** served by django. You should 

1. Create a directory for static files
2. Set ``STATIC_ROOT`` to the directory's path in the configuration file
3. Create an alias for '/static/' to the directory you created in the web server (see apache example configuration file) 
4. Run the django command to copy static files to the directory

The command to be run is 

.. code-block:: sh

    python src/manage.py collectstatic

Translations
############

You can compile the translations files with 

.. code-block:: sh

    python src/manage.py compilemessages

Example of apache configuration
###############################


When configuring apache, make sure to make alias for the media root and static root. An example of configuration can be found below:

.. code-block:: apache

    <IfModule mod_ssl.c>
        <VirtualHost *:80>
            ServerName example.org
            Redirect / https://example.org
            LogLevel warn
            CustomLog /var/log/apache2/example.access.log combined
            ErrorLog /var/log/apache2/example.error.log
        </VirtualHost>
        <VirtualHost *:443>
            ServerName example.org
            CustomLog /var/log/apache2/example.access.log combined
            ErrorLog /var/log/apache2/example.error.log
            SSLEngine on
            SSLCertificateFile /etc/letsencrypt/live/example.org/fullchain.pem
            SSLCertificateKeyFile /etc/letsencrypt/live/example.org/privkey.pem
            #Include /etc/letsencrypt/options-ssl-apache.conf
            <Directory /var/www/django-voting-app/src>
                Order allow,deny
                Allow from all
            </Directory>

            Alias /static/ /var/www/django-voting-app/src/staticfiles/
            Alias /media/ /var/www/django-voting-app/src/media/

            WSGIScriptAlias / /var/www/django-voting-app/src/django_voting_app/wsgi.py
            WSGIProcessGroup www-data
            WSGIDaemonProcess www-data processes=2 threads=16 maximum-requests=1000 display-name=example
            WSGIPassAuthorization On
        </VirtualHost>
    </IfModule>

Modification of wsgi file to use in virtual env
###############################################

If you are using a virtualenv, a slight modification if the ``wsgi.py`` file is required. This file is located in ``src/django_voting_app``.

We suppose that the virtualenv directory is located at ``/var/www/django-voting-app/.venv``.

.. code-block:: python

    import os
    import sys

    VIRTUALENV_LOC = '/var/www/django-voting-app/.venv'

    activate_env=os.path.join(VIRTUALENV_LOC, 'bin/activate_this.py')
    exec(compile(open(activate_env, "rb").read(), activate_env, 'exec'), {'__file__':activate_env})

    sys.path.append('/var/www/django-voting-app/src')
    sys.path.append('/var/www/django-voting-app/src/django_voting_app')

    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_voting_app.settings")
    application = get_wsgi_application()

