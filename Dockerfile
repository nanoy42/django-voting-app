FROM python:3
ENV LDAP_USER_FILTER="(uid=%(user)s)"
ENV LDAP_GROUP_FILTER="(objectClass=groupOfUniqueNames)"
RUN useradd --create-home appuser
WORKDIR /home/appuser
RUN apt-get update && apt-get install -y --no-install-recommends gettext-base libldap2-dev libsasl2-dev gcc
COPY docker/ .
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install django-auth-ldap && pip install gunicorn
USER appuser
COPY --chown=appuser src .
CMD ./docker-entrypoint.sh

