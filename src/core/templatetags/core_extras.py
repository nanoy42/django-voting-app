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
from django.utils.translation import gettext_lazy as _

register = template.Library()


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


@register.simple_tag
def language_flag(language_code):
    """Return the flag for the corresponding language code.

    Args:
        language_code (string): language code

    Returns:
        string: flag
    """
    if language_code == "fr":
        return "🇫🇷"
    else:
        return "🇬🇧"