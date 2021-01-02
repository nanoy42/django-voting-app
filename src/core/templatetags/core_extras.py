# django-voting-app - Simple django app to organise votes
# Copyright (C) 2020 The authors
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

"""
Templatetags for core app.
"""

from django import template
from django.conf import settings
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

register = template.Library()


class GetModelTranslationAvailableLanguagesNode(template.Node):
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        context[self.variable] = [k for k in settings.MODELTRANSLATION_LANGUAGES]
        return ""


@register.simple_tag
def has_voted(vote, user):
    """Return different strings wether the user has voted or not

    Args:
        vote (Vote): the vote
        user (User): user to test

    Returns:
        string: depends on wether the user voted or not.
    """
    if vote.has_voted(user):
        return _("You voted")
    return _("You have not yet voted")


@register.tag("get_modeltranslation_available_languages")
def do_get_modeltransaltion_available_languages(parser, token):
    """
    Store a list of available languages in the context.
    Usage::
        {% get_modeltranslation_available_languages as languages %}
        {% for language in languages %}
        ...
        {% endfor %}
    This puts settings.MODELTRANSLATIONLANGUAGES into the named variable.
    """
    # token.split_contents() isn't useful here because this tag doesn't accept variable as arguments
    args = token.contents.split()
    if len(args) != 3 or args[1] != "as":
        raise template.TemplateSyntaxError(
            "'get_modeltranslation_available_languages' requires 'as variable' (got %r)"
            % args
        )
    return GetModelTranslationAvailableLanguagesNode(args[2])
