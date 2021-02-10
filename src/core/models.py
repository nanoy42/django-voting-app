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
Models for core app.
"""

import hashlib
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import IntegrityError, models, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def is_member_or(user, groups):
    """Test if a a user is a member of one or more groups.

    Return True if the user is in one or more groups contained in variable groups
    Return False if the user is not in any of the groups

    Args:
        user (User): user to test
        groups (iterable of Group): groups

    Returns:
        bool: True if the user is in one or more of the groups, False otherwise
    """
    user_groups = user.groups.all()
    for group in groups:
        if group in user_groups:
            return True
    return False


class Vote(models.Model):
    """Vote model

    A vote contains question and is limited in time

    Args:
        name (string): name of the vote
        description (string): description of the vote
        begin_date (datetime): datetime for the beginning of the vote
        end_date (datetime): datetime for the end of the vote
        ready (bool): a vote must be ready to begin
        groups (list of Group): a user must be in one or more the groups to vote

    name, begin_date and end_date are required
    """

    class Meta:
        """Define name and plural name of Vote model"""

        verbose_name = _("vote")
        verbose_name_plural = _("votes")

    name = models.CharField(max_length=255, verbose_name=_("name"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    begin_date = models.DateTimeField(verbose_name=_("begin date"))
    end_date = models.DateTimeField(verbose_name=_("end date"))
    ready = models.BooleanField(default=False, verbose_name=_("ready"))
    groups = models.ManyToManyField(Group, blank=True)
    see_voters = models.BooleanField(default=False, verbose_name=_("see voters"))

    def __str__(self):
        """string representation of a vote (name)

        Returns:
            string: name of the vote
        """
        return self.name

    @property
    def get_total_ballots(self):
        """Return the total number of ballots (ie participations)

        Returns:
            int: total number of ballots
        """
        return Ballot.objects.filter(vote=self).count()

    def can_vote(self, user):
        """Verify if a user can vote.

        Several conditions:
          * the vote must be ready
          * the vote must be ongoing (i.e. not before or after the vote period)
          * if the vote is restricted to some groups, the user must be in one of the groups
          * the user mustn't have already voted

        Args:
            user (User): user

        Returns:
            (bool, string): the boolean is True if the user can vote. If False, the string is the corresponding error message
        """
        msg = ""
        res = True
        if self.before or not self.ready:
            msg = _("This vote is not open")
            res = False
        elif self.after:
            msg = _("This vote is closed")
            res = False
        elif self.groups.all() and not is_member_or(user, self.groups.all()):
            msg = _("You are not allowed to vote in this vote")
            res = False
        elif self.has_voted(user):
            msg = _("You already voted for this vote")
            res = False
        return res, msg

    def has_voted(self, user):
        """Test if a user has voted.

        Args:
            user (User): user to test

        Returns:
            bool: True if the user has already voted for this vote, False otherwise.
        """
        req = Ballot.objects.filter(vote=self, user=user)
        if req.count():
            return True
        return False

    @property
    def before(self):
        """Test if the time is before the beginning of the vote

        Returns:
            bool: True if the time is before the beginning of the vote
        """
        return timezone.now() < self.begin_date

    @property
    def after(self):
        """Test if the time is after the end of the vote

        Returns:
            bool: True if the time is after the end of the vote
        """
        return timezone.now() > self.end_date

    @property
    def active(self):
        """Test if the vote is active

        A vote is active if :
          * the vote is ready
          * the vote has begun
          * the vote is not finished

        Returns:
            bool: True if the is active, False otherwise
        """
        return self.ready and not self.before and not self.after

    def make_ready(self):
        """Set ready to True"""
        self.ready = True
        self.save()

    @property
    def can_see_results(self):
        """Test if the results are available

        This depends on the VOTE_SEE_BEFORE_END

        Returns:
            bool: True if the results can be seen.
        """
        return settings.VOTE_SEE_BEFORE_END or self.after

    @transaction.atomic
    def vote(self, user, answers):
        """Vote for the vote

        Args:
            user (User): the user who is about to vote
            answers (iterable of Answer): list of answers for the ballot. The length must the same as the number fo questions

        Todo:
            verify that each question has one answer

        Raises:
            Exception: when the number of answers is not the same as the numbe rof questions
            Exception: if one element of answers is not an Answer
            Exception: if one the answer is not from the vote
            Exception: if the user cannot vote on this vote
        """
        res, msg = self.can_vote(user)
        if res:
            if len(answers) != self.question_set.count():
                raise Exception("Incorrect ballot")
            questions_to_answer = [q.pk for q in self.question_set.all()]
            for answer in answers:
                if not isinstance(answer, Answer):
                    raise Exception("answers must be an iterable of Answer")
                if answer.question.pk not in questions_to_answer:
                    raise Exception("Incorrect ballot")
                questions_to_answer.remove(answer.question.pk)
                answer.vote()
            Ballot.objects.create(
                user=user,
                vote=self,
            )
        else:
            raise Exception(msg)

    @property
    def nb_questions(self):
        """Return the number of questions in the vote.

        Returns:
            int: number of questions included in the vote.
        """
        return self.question_set.count

    @property
    def nb_documents(self):
        """Return the number of documents in the vote.

        Returns:
            int: number of documents included in the vote.
        """
        return self.document_set.count

    @property
    def voters(self):
        """Return the list of voters

        Returns:
            list<User>: list of voters
        """
        if self.see_voters:
            return [ballot.user for ballot in Ballot.objects.filter(vote=self)]
        return None


class Question(models.Model):
    """Question model.

    Args:
        vote (Vote): the vote linked to the question
        text (string): the text of the question

    vote and text are required.
    """

    class Meta:
        """Meta class for Question."""

        verbose_name = _("question")
        verbose_name_plural = _("questions")

    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name=_("vote"))
    text = models.TextField(verbose_name=_("text"))

    def __str__(self):
        """str representation of Question.

        Returns:
            string: representation of the question in format vote - question
        """
        return "{} - {}".format(str(self.vote), self.text)

    @property
    def nb_answers(self):
        """Return the number of possible answers for the question.

        Returns:
            int: number of possible answer for the question.
        """
        return self.answer_set.count


class Answer(models.Model):
    """Answer model.

    Args:
        question (Question): question linked to the answer
        answer (string): text of the answer
        number (int): number of vote for this answer

    question and answer are required.
    """

    class Meta:
        """Meta class for Answer."""

        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name=_("vote")
    )
    answer = models.TextField(verbose_name=_("answer"))
    number = models.IntegerField(null=True, default=0, verbose_name=_("number"))

    def __str__(self):
        """str representation of the Answer.

        Returns:
            string: str representation of the answer in the format vote - question - answer.
        """
        return "{} - {}".format(str(self.question), self.answer)

    @property
    def percentage(self):
        """Return the percentage of vote for this answer (ie the number of the total number of participation)

        Returns:
            int: percentage of vote for this answer
        """
        if self.question.vote.get_total_ballots:
            return self.number / self.question.vote.get_total_ballots * 100
        return 0

    def vote(self):
        """Vote (i.e. add one to the number)"""
        self.number += 1
        self.save()


class Ballot(models.Model):
    """Ballot model.

    This is used to keep track of who voted.

    Args:
        user_hash (string): hash containing information on the user
        vote (Vote): Vote in which the user voted.
    """

    class Meta:
        """Meta class for Balot"""

        verbose_name = _("ballot")
        verbose_name_plural = _("ballots")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name=_("vote"))


class Document(models.Model):
    """Document model

    Args:
        vote (Vote): vote linked to the document.
        name (string): name of the document
        document (File): document
    """

    class Meta:
        """Meta model for Document"""

        verbose_name = _("document")
        verbose_name_plural = _("documents")

    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name=_("vote"))
    name = models.CharField(max_length=255, verbose_name=_("name"))
    document = models.FileField(verbose_name=_("document"))

    def __str__(self):
        """str represention of Document

        Returns:
            string: string reprensetation of the document in the format vote - name
        """
        return "{} - {}".format(str(self.vote), self.name)


@receiver(models.signals.post_delete, sender=Document)
def auto_delete_document_on_delete(sender, instance, **kwargs):
    """
    Auto delete document files on deletion of the instance.
    """
    if instance.document:
        if os.path.isfile(instance.document.path):
            os.remove(instance.document.path)


@receiver(models.signals.pre_save, sender=Document)
def auto_delete_document_on_change(sender, instance, **kwargs):
    """
    Auto delete document files when the files are changed.
    """
    if not instance.pk:
        return False

    document = Document.objects.get(pk=instance.pk)

    old_file = document.document

    new_file = instance.document
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(pre_save, sender=Question)
def pre_save_question(sender, instance, *args, **kwargs):
    """
    Prevent adding a question to a ready vote.
    """
    if instance._state.adding:
        if instance.vote.ready:
            raise Exception("Cannot create question on a ready vote")


@receiver(pre_save, sender=Answer)
def pre_save_answer(sender, instance, *args, **kwargs):
    """
    Prevent adding an answer to a ready vote.
    """
    if instance._state.adding:
        if instance.question.vote.ready:
            raise Exception("Cannot create answer on a ready vote")
