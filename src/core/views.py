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
Views for core app.
"""

import hashlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Answer, Ballot, Question, Vote


def legals(request):
    """Legals view.

    Args:
        request (HttpRequest): django request object

    Returns:
        Httpresponse: django response object
    """
    return render(request, "legals.html")


@login_required
@user_passes_test(lambda user: user.is_active)
def home(request):
    """Home page.

    All the ready votes are displayed even if :
      * the user is not in one the groups of the vote
      * the vote has not yet begun
      * the vote is finished

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    votes = Vote.objects.filter(ready=True).order_by("-begin_date")
    return render(request, "home.html", {"votes": votes, "active": "home"})


@login_required
@user_passes_test(lambda user: user.is_active)
@transaction.atomic
def vote(request, pk):
    """Vote page.

    The pks of the answer are passed through the post form.
    Next, the answer objects are retrieved and passed to the vote function.

    Args:
        request (HttpRequest): django http request
        pk (int): primary key of the vote

    Returns:
        HttpResponse: django response object
    """
    vote = get_object_or_404(Vote, pk=pk)
    res, msg = vote.can_vote(request.user)
    if not res:
        messages.error(request, msg)
        return redirect(reverse("home"))
    questions = vote.question_set.all()
    if request.POST:
        answers = []
        for question in questions:
            if "question-{}".format(question.pk) not in request.POST:
                messages.error(request, _("Your ballot is incorrect"))
                return redirect(reverse("vote", kwargs={"pk": vote.pk}))
            try:
                answer = Answer.objects.get(
                    pk=request.POST["question-{}".format(question.pk)]
                )
            except Answer.DoesNotExist:
                messages.error(request, _("Your ballot is incorrect"))
                return redirect(reverse("vote", kwargs={"pk": vote.pk}))
            answers.append(answer)
        vote.vote(request.user, answers)
        messages.success(request, _("Thank you for voting"))
        return redirect(reverse("home"))
    return render(request, "vote.html", {"vote": vote, "questions": questions})


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def votes_index(request):
    """Votes index. Display all the votes.

    This view is restricted to staff.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    votes = Vote.objects.all().order_by("-begin_date")
    return render(request, "votes_index.html", {"votes": votes, "active": "index"})


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def results(request):
    """Votes results. Display all the active votes.

    Avery active votes are displayed even if they are not finished.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    votes = Vote.objects.filter(ready=True).order_by("-begin_date")
    return render(request, "results.html", {"votes": votes, "active": "results"})


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def results_detail(request, pk):
    """Results details for a vote.

    Args:
        request (HttpRequest): django request object
        pk (int): primary key of the vote

    Returns:
        HttpResponse: django response object.
    """
    vote = get_object_or_404(Vote, pk=pk)
    if not vote.can_see_results:
        messages.warning(request, _("You can't see results before the end of the vote"))
        return redirect(reverse("results"))
    questions = vote.question_set.all()
    return render(
        request,
        "results_detail.html",
        {"vote": vote, "questions": questions, "active": "results"},
    )


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def ready(request, pk):
    """Make a vote ready

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the vote

    Returns:
        HttpResponse: django response object.
    """
    vote = get_object_or_404(Vote, pk=pk)
    vote.make_ready()
    messages.success(request, _("Vote is ready."))
    return redirect(reverse("votes-index"))
