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
Tests for core app.
"""

import os
import tempfile
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.db import IntegrityError
from django.template import Template, TemplateSyntaxError
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from core.models import Answer, Document, Question, Vote, is_member_or


class IsMemberOfTestCase(TestCase):
    """Test class for the is_member_or function."""

    def setUp(self):
        """Set up the tests"""
        self.user_1 = User.objects.create(username="test1", email="test1@test.test")
        self.user_2 = User.objects.create(username="test2", email="test2@test.test")
        self.group_1 = Group.objects.create(name="Group1")
        self.group_2 = Group.objects.create(name="Group2")
        self.user_1.groups.add(self.group_1)
        self.user_1.save()

    def test_is_member_of(self):
        """Test the function is_member_or"""
        self.assertTrue(is_member_or(self.user_1, Group.objects.all()))
        self.assertFalse(is_member_or(self.user_2, Group.objects.all()))


class VoteTestCase(TestCase):
    """Test class for Vote model."""

    def setUp(self):
        """Set up the tests."""
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.vote_before = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=2),
        )
        self.vote_after = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now() - timedelta(hours=2),
            end_date=timezone.now() - timedelta(hours=1),
        )
        self.user = User.objects.create(username="test1", email="test1@test.test")
        self.question = Question.objects.create(vote=self.vote, text="Yellow or red ?")
        self.answer1 = Answer.objects.create(question=self.question, answer="Yellow")
        self.answer2 = Answer.objects.create(question=self.question, answer="Red")

    def test_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.vote), "Test vote")

    def test_before(self):
        """Test the before method."""
        self.assertTrue(self.vote_before.before)
        self.assertFalse(self.vote.before)

    def test_after(self):
        """Test the after method."""
        self.assertTrue(self.vote_after.after)
        self.assertFalse(self.vote.after)

    def test_active(self):
        """Test the active method."""
        self.assertFalse(self.vote_before.active)
        self.assertFalse(self.vote_after.active)
        self.assertFalse(self.vote.active)
        self.vote_before.make_ready()
        self.vote_after.make_ready()
        self.vote.make_ready()
        self.assertFalse(self.vote_before.active)
        self.assertFalse(self.vote_after.active)
        self.assertTrue(self.vote.active)

    def test_has_voted(self):
        """Test the has_voted method."""
        self.vote.make_ready()
        self.assertFalse(self.vote.has_voted(self.user))
        self.vote.vote(self.user, [self.answer1])
        self.assertTrue(self.vote.has_voted(self.user))

    def test_can_vote(self):
        """Test the can_vote method."""
        res, msg = self.vote.can_vote(self.user)
        self.assertFalse(res)
        self.assertEqual(msg, "This vote is not open")

        self.vote.make_ready()
        res, msg = self.vote.can_vote(self.user)
        self.assertTrue(res)
        self.assertEqual(msg, "")

        self.vote.vote(self.user, [self.answer1])
        res, msg = self.vote.can_vote(self.user)
        self.assertFalse(res)
        self.assertEqual(msg, "You already voted for this vote")

        self.vote_before.make_ready()
        res, msg = self.vote_before.can_vote(self.user)
        self.assertFalse(res)
        self.assertEqual(msg, "This vote is not open")

        self.vote_after.make_ready()
        res, msg = self.vote_after.can_vote(self.user)
        self.assertFalse(res)
        self.assertEqual(msg, "This vote is closed")

    def test_can_vote_group(self):
        """Test the can_vote method with groups involved."""
        self.group_1 = Group.objects.create(name="Group1")
        self.group_2 = Group.objects.create(name="Group2")
        self.user.groups.add(self.group_1)
        self.user.save()
        self.user_2 = User.objects.create(username="test2", email="test2@test.test")
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
            ready=True,
        )
        self.vote.groups.add(self.group_1)
        self.vote.groups.add(self.group_2)
        self.vote.save()
        res, msg = self.vote.can_vote(self.user)
        self.assertTrue(res)
        self.assertEqual(msg, "")
        res, msg = self.vote.can_vote(self.user_2)
        self.assertFalse(res)
        self.assertEqual(msg, "You are not allowed to vote in this vote")

    def test_make_ready(self):
        """Test the make_ready method."""
        self.vote.make_ready()
        self.assertTrue(self.vote.ready)

    def test_vote(self):
        """Test the vote method."""
        self.vote.make_ready()
        with self.assertRaises(Exception):
            self.vote.vote(self.user, [self.answer1, self.answer2])

        with self.assertRaises(Exception):
            self.vote.vote(self.user, [True])

        self.vote2 = Vote.objects.create(
            name="Test vote2",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.question2 = Question.objects.create(vote=self.vote2, text="Test")
        self.answer_other = Answer.objects.create(
            question=self.question2, answer="test"
        )

        with self.assertRaises(Exception):
            self.vote.vote(self.user, [self.answer_other])

        self.vote.vote(self.user, [self.answer1])
        self.assertEqual(self.answer1.number, 1)
        self.assertEqual(self.answer1.percentage, 100)
        self.assertTrue(self.vote.has_voted(self.user))

        with self.assertRaises(Exception):
            self.vote.vote(self.user, [self.answer2])

        vote2 = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        question21 = Question.objects.create(vote=vote2, text="Yellow or red ?")
        answer211 = Answer.objects.create(question=question21, answer="Yellow")
        answer212 = Answer.objects.create(question=question21, answer="Red")
        question22 = Question.objects.create(vote=vote2, text="Blue or green ?")
        answer221 = Answer.objects.create(question=question22, answer="Blue")
        answer222 = Answer.objects.create(question=question22, answer="Green")

        with self.assertRaises(Exception):
            vote2.vote(self.user, [answer211, answer212])

    def test_voters(self):
        self.vote.make_ready()
        self.assertEqual(None, self.vote.voters)

        self.vote.vote(self.user, [self.answer1])
        self.assertEqual(None, self.vote.voters)

        self.vote.see_voters = True
        self.vote.save()
        self.assertEqual([self.user], self.vote.voters)

    def test_nb_questions(self):
        """
        Test the nb_questions method.
        """
        self.assertEqual(self.vote.nb_questions(), 1)


class QuestionTestCase(TestCase):
    """Test for the Question model."""

    def setUp(self):
        """Set up the tests."""
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.question = Question.objects.create(vote=self.vote, text="Yellow or red ?")

    def test_str(self):
        """Test the __str__ method."""
        self.assertTrue(str(self.question), "Test vote - Yellow or red ?")

    def test_create_question_on_ready_vote(self):
        """Test that it is not possible to create a question on a ready vote."""
        self.vote.make_ready()
        with self.assertRaises(Exception):
            Question.objects.create(vote=self.vote, text="Cat or dog ?")


class AnswerTestCase(TestCase):
    """Test class for Answer."""

    def setUp(self):
        """Set up the tests."""
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.question = Question.objects.create(vote=self.vote, text="Yellow or red ?")
        self.answer1 = Answer.objects.create(question=self.question, answer="Yellow")
        self.answer2 = Answer.objects.create(question=self.question, answer="Red")
        self.user = User.objects.create(username="test1", email="test1@test.test")
        self.user2 = User.objects.create(username="test2", email="test2@test.test")

    def test_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.answer1), "Test vote - Yellow or red ? - Yellow")

    def test_vote(self):
        """Test the vote method."""
        self.vote.make_ready()
        self.assertEqual(self.answer1.number, 0)
        self.assertEqual(self.answer2.number, 0)
        self.answer1.vote()
        self.assertEqual(self.answer1.number, 1)
        self.assertEqual(self.answer2.number, 0)

    def test_percentage(self):
        """Test the percentage method."""
        self.vote.make_ready()
        self.assertEqual(self.answer1.percentage, 0)
        self.assertEqual(self.answer2.percentage, 0)
        self.vote.vote(self.user, [self.answer1])
        self.assertEqual(self.answer1.percentage, 100)
        self.assertEqual(self.answer2.percentage, 0)
        self.vote.vote(self.user2, [self.answer2])
        self.assertEqual(self.answer1.percentage, 50)
        self.assertEqual(self.answer2.percentage, 50)

    def test_create_answer_on_ready_vote(self):
        """Test that it is not possible to create an answer on a ready vote."""
        self.vote.make_ready()
        with self.assertRaises(Exception):
            Answer.objects.create(question=self.question, answer="Blue")

    def test_question_nb_answers(self):
        """
        Test the nb_answers method.
        """
        self.assertEqual(self.question.nb_answers(), 2)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class DocumentTestCase(TestCase):
    """Test class for Document."""

    def setUp(self):
        """Set up the tests."""
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.file = SimpleUploadedFile(
            "test.txt",
            b"test",
        )
        self.document = Document.objects.create(
            vote=self.vote, name="test", document=self.file
        )

    def test_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.document), "Test vote - test")

    def test_change(self):
        """Test that files are deleted on change."""
        self.assertTrue(os.path.isfile(self.document.document.path))
        self.file2 = SimpleUploadedFile(
            "test2.txt",
            b"test2",
        )
        old_path = self.document.document.path
        self.document.document = self.file2
        self.document.save()
        self.assertFalse(os.path.isfile(old_path))
        self.assertTrue(os.path.isfile(self.document.document.path))

    def test_delete(self):
        """Test that files are deleted on delete."""
        self.assertTrue(os.path.isfile(self.document.document.path))
        self.document.delete()
        self.assertFalse(os.path.isfile(self.document.document.path))

    def test_vote_nb_documents(self):
        """
        Test the nb_documents method.
        """
        self.assertEqual(self.vote.nb_documents(), 1)


class ViewsTestCase(TestCase):
    """Test class for views."""

    def setUp(self):
        """Set up the tests."""
        self.vote = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
        )
        self.vote2 = Vote.objects.create(
            name="Test vote",
            description="This is a test vote",
            begin_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=1),
            ready=False,
        )
        self.question = Question.objects.create(vote=self.vote, text="Yellow or red ?")
        self.answer1 = Answer.objects.create(question=self.question, answer="Yellow")
        self.answer2 = Answer.objects.create(question=self.question, answer="Red")
        self.vote.make_ready()
        self.c = Client()
        self.login_required_urls = ["/", "/vote/1", "/results"]
        self.no_login_required_urls = ["/login", "/legals"]
        self.staff_required_urls = ["/votes-index", "/results/1", "/results"]
        self.password = "password"
        self.superuser = User.objects.create_superuser(
            "superuser", "test@example.com", self.password
        )
        self.common_user = User.objects.create(username="test", email="test@test.test")
        self.common_user.set_password(self.password)
        self.common_user.save()

    def test_login_required(self):
        """Test that views that require login indeed require login."""
        for url in self.login_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url,
                "/login?next={}".format(url),
            )
        self.c.login(username=self.common_user.username, password=self.password)
        for url in self.login_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 200)

    def test_no_login_required(self):
        """Test that views that don't require login indeed don't require login."""
        for url in self.no_login_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 200)

    @override_settings(VOTE_SEE_BEFORE_END=True)
    def test_staff_required(self):
        """Test that views that require staff access indeed require staff access.

        The parameter VOTE_SEE_BEFORE_END is set to True, otherwise the view /results/1 would not be accessible.
        """
        for url in self.staff_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url,
                "/login?next={}".format(url),
            )
        self.c.login(username=self.common_user.username, password=self.password)
        for url in self.staff_required_urls:
            response = self.c.get(url)
        self.c.login(username=self.superuser.username, password=self.password)
        for url in self.staff_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 200)

    @override_settings(VOTE_SEE_BEFORE_END=False)
    def test_results_before_end(self):
        """Test that hte results cannot be accessed if the vote is not ended and VOTE_SEE_BEFORE_END is set to False."""
        self.c.login(username=self.superuser.username, password=self.password)
        response = self.c.get("/results/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/results")

    def test_login(self):
        """Test the login view."""
        response = self.c.post(
            "/login", {"username": self.superuser.username, "password": self.password}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_ready_view(self):
        """Test the ready view."""
        self.c.login(username=self.superuser.username, password=self.password)
        response = self.c.get("/ready/2")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/votes-index")
        self.vote2.refresh_from_db()
        self.assertTrue(self.vote2.ready)

    def test_vote_view(self):
        """Test the vote view."""
        self.c.login(username=self.common_user.username, password=self.password)
        response = self.c.get("/vote/2")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_vote(self):
        """Test the vote view."""
        self.c.login(username=self.common_user.username, password=self.password)

        response = self.c.post("/vote/1", {"question": self.answer1.pk})
        self.answer1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.vote.has_voted(self.common_user))
        self.assertEqual(self.answer1.number, 0)

        response = self.c.post("/vote/1", {"question-{}".format(self.question.pk): 0})
        self.answer1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.vote.has_voted(self.common_user))
        self.assertEqual(self.answer1.number, 0)

        response = self.c.post(
            "/vote/1", {"question-{}".format(self.question.pk): self.answer1.pk}
        )
        self.answer1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.vote.has_voted(self.common_user))
        self.assertEqual(self.answer1.number, 1)

        response = self.c.post(
            "/vote/1", {"question-{}".format(self.question.pk): self.answer1.pk}
        )
        self.answer1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.vote.has_voted(self.common_user))
        self.assertEqual(self.answer1.number, 1)

        response = self.c.get("")
        self.assertEqual(response.status_code, 200)

    def test_make_ready_action(self):
        """
        Test the custom action to make votes ready
        """
        self.c.login(username=self.superuser.username, password=self.password)
        self.assertFalse(self.vote2.ready)
        data = {"action": "make_ready", "_selected_action": [self.vote2.pk]}
        response = self.c.post("/admin/core/vote/", data)
        self.vote2.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.vote2.ready)

    def test_templatetags(self):
        """
        Test the custom templatetag to get available languages.
        """
        template = """
        {% load core_extras %}
        {% get_modeltranslation_available_languages %}
        """
        with self.assertRaises(TemplateSyntaxError):
            Template(template, {})

    def test_create_vote(self):
        """
        Test admin page to create vote.
        """
        self.c.login(username=self.superuser.username, password=self.password)
        data = {
            f"name_{settings.MODELTRANSLATION_DEFAULT_LANGUAGE}": "test",
            "begin_date_0": "2021-02-10",
            "begin_date_1": "17:25:58",
            "end_date_0": "2021-02-10",
            "end_date_1": "17:26:27",
            "see_voters": 1,
        }
        response = self.c.post("/admin/core/vote/add/", data)
        self.assertEqual(response.status_code, 302)

    def test_modify_vote(self):
        """
        Test admin page to modify vote
        """
        self.c.login(username=self.superuser.username, password=self.password)
        data = {
            f"name_{settings.MODELTRANSLATION_DEFAULT_LANGUAGE}": "test",
            "begin_date_0": "2021-02-10",
            "begin_date_1": "17:25:58",
            "end_date_0": "2021-02-10",
            "end_date_1": "17:26:27",
        }
        response = self.c.post("/admin/core/vote/1/change/", data)
        self.assertEqual(response.status_code, 302)