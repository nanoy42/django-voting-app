Prerequisites
=============

Requirements
############

There are currently two ways of installing django-voting-app :

* by source
* with docker

.. warning:: Installation with docker is considered experimental for now.

If you want to install using the source, you need :

* python
* pip
* a web server (apache or nginx for instance)
* a database

If you want to use docker you only need a working docker installation.  


Database
########

You will need a working database for this project. We recommend the use of PostgreSQL but any database working with django (see `here <https://docs.djangoproject.com/en/3.1/ref/databases/>`_) will do the trick.

You will need to create, before installation, a database (e.g. django-voting-app) and a user (e.g. django-voting-app) with some password that we will denote ``secret`` for the rest of this guide.

This is an example with PostgreSQL syntax :

.. code-block:: sql

    CREATE DATABASE django-voting-app;
    CREATE USER django-voting-app WITH PASSWORD 'secret';
    GRANT ALL PRIVILEGES ON DATABASE django-voting-app TO django-voting-app;