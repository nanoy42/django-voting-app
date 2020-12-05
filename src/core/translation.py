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
Translation for models.
"""

from modeltranslation.translator import TranslationOptions, translator

from core.models import Answer, Document, Question, Vote


class VoteTranslationOptions(TranslationOptions):
    """Translation class for Vote."""

    fields = ("name", "description")


class QuestionTranslationOptions(TranslationOptions):
    """Translation class for Question."""

    fields = ("text",)


class AnswerTranslationOptions(TranslationOptions):
    """Translation class for Answer"""

    fields = ("answer",)


class DocumentTranslationOptions(TranslationOptions):
    """Translation class for Document."""

    fields = ("name", "document")


translator.register(Vote, VoteTranslationOptions)
translator.register(Question, QuestionTranslationOptions)
translator.register(Answer, AnswerTranslationOptions)
translator.register(Document, DocumentTranslationOptions)