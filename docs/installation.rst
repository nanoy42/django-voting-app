Installation
============

Database
########

You will need a working database for this project. We recommend the use of PostgreSQL but any database working with django (see `here <https://docs.djangoproject.com/en/3.0/ref/databases/>`_) will do the trick.

However, please note that this software should be linked to mail server softwares like postfix and dovecot and that any database might not work with those. Please see the documentations of those before choosing any database.

You will need to create, before installation, a database (e.g. ``django-voting-app``) and a user (e.g. ``django-voting-app``) with some password that we will denote ``secret`` for the rest of this page.

Clone the repo
##############

You can clone the repo with the command 

.. code-block:: sh

    git clone https://github.com/nanoy42/django-voting-app



Install dependencies
####################

You can install the dependencies with pipenv

.. code-block:: sh

    pipenv install

or with pip

.. code-block:: sh

    pip install -r requirements.txt

Apply migration
###############

Apply the migrations with the command

.. code-block:: sh

    python src/manage.py migrate

(you will need to have setup the database before this step)

You can create a superuser with the command

.. code-block:: sh

    python src/manage.py createsuperuser

Copy statics
############

You can copy the statics, after setting the STATIC_ROOT setting, with the command

.. code-block:: sh

    python src/manage.py collectstatics

Translations
############

You can compile the translations files with

.. code-block:: sh

    python src/manage.py compilemessages

Configuration of apache
#######################

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

