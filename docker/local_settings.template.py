# django-voting-app - Simple django app to organise votes
# Copyright (C) 2020 Yoann Piétri

# django-voting-app is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# django-voting-app is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with django-voting-app. If not, see <https://www.gnu.org/licenses/>.

############################## NOTICE ##############################
####################################################################
# Please copy this file to src/django_voting_app/local_settings.py #
# and fill it with appropriate values.                             #
# Note that this file is included at the end and can overwrite     #
# any django setting.                                              #
####################################################################

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

########################## django settings #########################

# See https://docs.djangoproject.com/en/3.1/ref/settings/

SECRET_KEY = "${DJANGO_SECRET}"

DEBUG = False

ALLOWED_HOSTS = ["${HOST}"]

ADMINS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TIME_ZONE = "UTC"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

################## django-modeltranslation settings ################

# See https://django-modeltranslation.readthedocs.io/en/latest/index.html

MODELTRANSLATION_DEFAULT_LANGUAGE = "en"

##################### django-voting-app settings ###################

# See https://django-voting-app.readthedocs.io/en/latest/

# Text displayed in the navbar and in the tab name.
# Default: Django Voting App
VOTE_NAME = "Django Voting App"

# If set to True, results can be accessed by administrators before the end of the vote.
# Default: False
VOTE_SEE_BEFORE_END = False

# Text displayed on the legals page. If it is an empty string, the section is not displayed.
# Default: empty string
VOTE_LOCAL_LEGALS = """
"""

############################## Optional ############################
##################### django-ldap-auth settings ####################

# See https://django-auth-ldap.readthedocs.io/en/latest/

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType

AUTHENTICATION_BACKENDS = (
   "django.contrib.auth.backends.ModelBackend",
   "django_auth_ldap.backend.LDAPBackend",
)

AUTH_LDAP_SERVER_URI = "${LDAP_URI}"

AUTH_LDAP_BIND_DN = "${LDAP_BIND_DN}"
AUTH_LDAP_BIND_PASSWORD = "${LDAP_BIND_PASSWORD}"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "${LDAP_USER_BASE}", ldap.SCOPE_SUBTREE, "${LDAP_USER_FILTER}"
)

AUTH_LDAP_USER_ATTR_MAP = {"email": "mail"}
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "${LDAP_GROUP_BASE}",
    ldap.SCOPE_SUBTREE,
    "${LDAP_GROUP_FILTER}",
)
AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType()
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "${LDAP_STAFF_GROUP}",
    "is_superuser": "${LDAP_SUPERUSER_GROUP}",
}

AUTH_LDAP_USER_ATTR_MAP = {"is_active": "dialupAccess"}
