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


def make_ready(modeladmin, request, queryset):
    """Custom action to make every vote of the queryset ready"""
    queryset.update(ready=True)


make_ready.short_description = "Mark selected votes as ready"


class VoteAdmin(TranslationAdmin):
    """Admin class for Vote model."""

    fields = ("name", "description", "begin_date", "end_date", "groups")
    list_display = (
        "name",
        "ready",
        "begin_date",
        "end_date",
        "nb_questions",
        "nb_documents",
    )
    list_filter = ("ready",)
    ordering = ("-begin_date",)
    actions = (make_ready,)


class QuestionAdmin(TranslationAdmin):
    """Admin class for Question model."""

    list_display = ("text", "vote", "nb_answers")
    list_filter = ("vote",)

    pass


class AnswerAdmin(TranslationAdmin):
    """Admin class for Answer model."""

    fields = (
        "question",
        "answer",
    )

    list_display = ("answer", "question")
    list_filter = ("question", "question__vote")


class DocumentAdmin(TranslationAdmin):
    """Admin class for Document model."""

    list_display = ("name", "vote")
    list_filter = ("vote",)


admin.site.register(Vote, VoteAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Ballot)
admin.site.register(Document, DocumentAdmin)
