Configuration file
==================

.. warning:: The following page describe the structure of the configuration file for django-voting-app. However, for now, you can't edit any value in the docker image for the configuration.

The configuration is done in a ``local_settings.py``. You can copy a canvas for this file in the ``src/django_voting_app`` directory : 

.. code-block:: sh

    cp src/django_voting_app/local_settings.example.py src/django_voting_app/local_settings.py

Then you must edit the values in it.

.. note:: The ``local_settings.py`` is included at the end of the configuration file so you can overwrite **any** django settings, but we encourage to edit only the ones listed in the example local settings file.

Django settings
###############

Please see the `django documentation <https://docs.djangoproject.com/fr/3.0/ref/settings>`_ for extended documentation.

.. attribute:: SECRET_KEY

Default: ``""``

A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value. This value should be kept secret.

.. warning::
    Django can't run without a secret key.

.. attribute:: DEBUG

Default: ``False``

A boolean that turns on/off debug mode. You should use ``DEBUG=False`` for production.

.. attribute:: ALLOWED_HOSTS

Default: ``[]``

A list of strings representing the host/domain names that this Django site can serve.

.. warning::
    Django can't run with ``DEBUG=False`` and ``ALLOWED_HOSTS=[]``.

.. attribute:: ADMINS

Default: ``[]``

A list of tuples representing the admins in the format (name, email).

.. attribute:: DATABASES

Default: 

.. code-block:: python 

    {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

If you use a postgresql database, on the same host as where you installed django-voting-app, it should look like this:

.. code-block:: python

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "django-voting-app",
            "USER": "django-voting-app",
            "PASSWORD": "secret",
            "HOST": "localhost",
        }
    }

.. attribute:: TIME_ZONE

Default: ``"UTC"``

Time zone of the server.

.. attribute:: STATIC_ROOT

Default: ``BASE_DIR / "staticfiles"``

Folder in which the static files should be copied. You should make an alias for ``/static`` to this directory. 

.. attribute:: MEDIA_ROOT

Default: ``BASE_DIR / "media"``

Folder in which the media files should be uploaded. You should make an alias for ``/media`` to this directory. 

Model translation settings
##########################

django-voting-app uses `django-modeltranslation <https://github.com/deschler/django-modeltranslation>`_ to translate the instances of the models.

It should work out of the box with the configuration, but if you want to make some modification, there are some parameters worth noting (we, however, redirect you to the full documentation for more parameters and details).

django-voting-languages supports the following languages :

 * English (en)
 * French (fr)

To set the default language for your models your models, you can use

.. attribute:: MODELTRANSLATION_DEFAULT_LANGUAGE

Default: ``"en"``

Also, you may want to use other languages than English qnd French for your models, that can be done by setting he following attribute:

.. attribute:: MODELTRANSLATION_LANGUAGES

Default is ``LANGUAGES``


However note that he would still be possible to change to any language set in ``LANGUAGES``, so you may have to overwrite the ``LANGUAGES`` setting as well.

.. todo:: Get available languages from ``MODELTRANSLATION_LANGUAGES`` and not from ``LANGUAGES``.


django-voting-app settings
##########################

There are 3 parameters fro django-voting-app:

.. attribute:: VOTE_NAME

Default: ``"Django Voting app"``
This text is displayed in the navbar and in the tab name.

.. attribute:: VOTE_SEE_BEFORE_END

Default: ``False``
If set to True, staff can see the results of a vote before its end.

.. attribute:: VOTE_LOCAL_LEGALS

Default: empty string
Text displayed on the legals page. If it is an empty string, the section is not displayed.


Link to LDAP
############

This app was initially developed to plug to LDAP, and make a voting app for an organization.

This is totally independent of django-voting-app but here is an example of how you can do it.\

Install the `django-auth-ldap <https://github.com/django-auth-ldap/django-auth-ldap>`_ package and configure it like so 

.. code-block:: python

    # Add the authentication class
    AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "django_auth_ldap.backend.LDAPBackend",
    )

    # Uri of the ldap server
    AUTH_LDAP_SERVER_URI = "ldap://ldap.example.org"

    # Bind user to LDAP
    AUTH_LDAP_BIND_DN = "cn=user,dc=ldap,dc=example,dc=org"
    AUTH_LDAP_BIND_PASSWORD = "secret"

    # Where to find the users
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        "cn=Users,dc=ldap,dc=example,dc=org", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
    )

    # Here we are making an account active is dialupAccess is True
    AUTH_LDAP_USER_ATTR_MAP = {"email": "mail","is_active": "dialupAccess"}

    # Copy groups from LDAP 
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        "ou=posix,ou=groups,dc=ldap,dc=example,dc=org",
        ldap.SCOPE_SUBTREE,
        "(objectClass=posixGroup)",
    )
    AUTH_LDAP_GROUP_TYPE = PosixGroupType()
    AUTH_LDAP_MIRROR_GROUPS = True

    # Map users of groups to specific roles
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_staff": "cn=staff,ou=posix,ou=groups,dc=ldap,dc=example,dc=org",
        "is_superuser": "cn=root,ou=posix,ou=groups,dc=ldap,dc=example,dc=org",
    }