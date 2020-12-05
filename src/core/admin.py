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
Admin registration for core app.
"""

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Answer, Ballot, Document, Question, Vote


class VoteAdmin(TranslationAdmin):
    """Admin class for Vote model."""

    fields = ("name", "description", "begin_date", "end_date", "groups")


class QuestionAdmin(TranslationAdmin):
    """Admin class for Question model.

    We need it for translations.
    """

    pass


class AnswerAdmin(TranslationAdmin):
    """Admin class for Answer model."""

    fields = (
        "question",
        "answer",
    )


class DocumentAdmin(TranslationAdmin):
    """Admin class for Document model.

    We need it for translations.
    """

    pass


admin.site.register(Vote, VoteAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Ballot)
admin.site.register(Document, DocumentAdmin)