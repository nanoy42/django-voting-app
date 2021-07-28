Site Administration
===================

Self diagnostic page
####################

The site now includes a basic self diagnostic page to see :

* the version of django-voting-app (and if a new version is available)
* the media folder configuration
* translations configuration
* https
* dependencies

Updater
#######

The update script was introduced in version 1.3.0.

It allows a user to update django-voting-app using a script.

Some remarks:

* By default, it will prevent a user to update when major changes are detected. This behavior can be overwritten with the `-f` (`--force`) option. It is probably better to make a manual update in this case.
* By default, it will prevent a user to update if the current branch is not main. It can be overwritten with the `-f` (`--force`) option if you know what you are doing.

The other option to the script is `-h --help` that will display the help screen.

.. warning:: This feature is tagged as experimental from version 1.3.0 and onwards.