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
import os
import sys
import requests
from subprocess import call, check_output, STDOUT
from requests.exceptions import SSLError, ConnectionError

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, User
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS

from django_voting_app import __version__
from .models import Answer, Question, Vote, Document
from .utils import compare_versions, get_dependencies, is_database_synchronized


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
def results(request):
    """Votes results. Display all the active votes.

    Avery active votes are displayed even if they are not finished.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    if request.user.is_staff:
        votes = Vote.objects.filter(ready=True).order_by("-begin_date")
    else:
        votes = Vote.objects.filter(ready=True, public_results=True).order_by(
            "-begin_date"
        )
    return render(request, "results.html", {"votes": votes, "active": "results"})


@login_required
@user_passes_test(lambda user: user.is_active)
def results_detail(request, pk):
    """Results details for a vote.

    Args:
        request (HttpRequest): django request object
        pk (int): primary key of the vote

    Returns:
        HttpResponse: django response object.
    """
    vote = get_object_or_404(Vote, pk=pk)
    voters = vote.voters
    if not vote.can_see_results(request.user):
        messages.warning(
            request,
            _("You can't see the results (vote not finished or insufficient rights)"),
        )
        return redirect(reverse("results"))
    questions = vote.question_set.all()
    return render(
        request,
        "results_detail.html",
        {"vote": vote, "questions": questions, "active": "results", "voters": voters},
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


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def new_vote(request):
    """Create a vote with only one web page.

    This is not pretty.
    The html page is not pretty.
    The code that handles the POST request is not pretty.
    It doesn't use a Django form.
    This could be improve in various ways.

    There are two reasons why this is not pretty :
        * First we cannot do a single form as we use 4 models
        with an unknown number of instances for the questions,
        answers and documents
        * Second, the multilingual is really complex to handle.

    Args:
        request (HttpRequest): django request.

    Returns:
        HttpResponse: django response.
    """
    groups = Group.objects.all()
    if request.method == "POST":
        try:
            with transaction.atomic():
                begin_date = request.POST["begin-date"]
                end_date = request.POST["end-date"]

                if "see-voters" in request.POST:
                    see_voters = True
                else:
                    see_voters = False

                if "public-results" in request.POST:
                    public_results = True
                else:
                    public_results = False

                vote = Vote(
                    begin_date=begin_date,
                    end_date=end_date,
                    see_voters=see_voters,
                    public_results=public_results,
                )

                for language in settings.MODELTRANSLATION_LANGUAGES:
                    vote.__setattr__(
                        f"name_{language}", request.POST[f"{language}-name"]
                    )
                    vote.__setattr__(
                        f"description_{language}",
                        request.POST[f"{language}-description"],
                    )

                vote.save()
                if "groups" in request.POST:
                    for group_pk in request.POST.getlist("groups"):
                        group = Group.objects.get(pk=group_pk)
                        vote.groups.add(group)

                first_language = settings.MODELTRANSLATION_LANGUAGES[0]
                questions_map = {}
                for key in request.POST:
                    if f"{first_language}-question-name-" in key:
                        question = Question(vote=vote)
                        for language in settings.MODELTRANSLATION_LANGUAGES:
                            question.__setattr__(
                                f"text_{language}", request.POST[f"{language}{key[2:]}"]
                            )
                        question.save()
                        question_id = int(key.split("-")[3])
                        questions_map[question_id] = question

                for key in request.POST:
                    if f"{first_language}-answer" in key:
                        question_id = int(key.split("-")[4])
                        answer = Answer(question=questions_map[question_id])
                        for language in settings.MODELTRANSLATION_LANGUAGES:
                            answer.__setattr__(
                                f"answer_{language}",
                                request.POST[f"{language}{key[2:]}"],
                            )
                        answer.save()

                for key in request.POST:
                    if f"{first_language}-document-name" in key:
                        document_id = int(key.split("-")[3])
                        document = Document(vote=vote)
                        for language in settings.MODELTRANSLATION_LANGUAGES:
                            document.__setattr__(
                                f"name_{language}", request.POST[f"{language}{key[2:]}"]
                            )
                            document.__setattr__(
                                f"document_{language}",
                                request.FILES[
                                    f"{language}-document-file-{document_id}"
                                ],
                            )
                        document.save()
            messages.success(request, "The vote was created")
            return redirect(reverse("votes-index"))
        except Exception as e:
            messages.error(
                request,
                f"There was an error creating the vote. The error message is {e}",
            )
            return redirect(reverse("new-vote"))
    return render(request, "new_vote.html", {"active": "new-vote", "groups": groups})


@login_required
@user_passes_test(lambda user: user.is_active)
@user_passes_test(lambda user: user.is_staff)
def checks(request):

    current_version = __version__
    response = requests.get(
        "https://api.github.com/repos/nanoy42/django-voting-app/releases/latest"
    )
    last_available_version = response.json()["tag_name"][1:]

    use_git = (
        False
        if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, "w"))
        else True
    )

    branch = None
    if use_git:
        branch = (
            check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf8")
        )

    diff = compare_versions(current_version, last_available_version)
    update_strategies = {
        "equal": _("You have the latest version available."),
        "patch": _(
            "Your version differs by a patch. Consider using the updater script (git only)."
        ),
        "minor": _(
            "Your version differs by minor changes. Consider using the updater script (git only)."
        ),
        "major": _("Your version differs by major changes. Consider a manual update."),
    }
    update_strategy = update_strategies[diff]

    dependencies = get_dependencies()
    python_version_info = sys.version_info

    python_version = f"{python_version_info.major}.{python_version_info.minor}.{python_version_info.micro}"

    current_url = str(request.build_absolute_uri()).split("/")[2]

    https_enabled = True
    try:
        requests.get(f"https://{current_url}/")
    except (SSLError, ConnectionError):
        https_enabled = False

    user_count = User.objects.all().count()
    active_user_count = User.objects.filter(is_active=True).count()
    group_count = Group.objects.all().count()
    admin_count = User.objects.filter(is_staff=True).count()
    vote_count = Vote.objects.all().count()

    all_migrations_applied = is_database_synchronized(DEFAULT_DB_ALIAS)

    is_media_writable = os.access(settings.MEDIA_ROOT, os.W_OK)
    return render(
        request,
        "checks.html",
        {
            "active": "checks",
            "current_version": current_version,
            "last_available_version": last_available_version,
            "update_strategy": update_strategy,
            "use_git": use_git,
            "branch": branch,
            "dependencies": dependencies,
            "python_version": python_version,
            "current_url": current_url,
            "https_enabled": https_enabled,
            "user_count": user_count,
            "active_user_count": active_user_count,
            "group_count": group_count,
            "admin_count": admin_count,
            "vote_count": vote_count,
            "all_migrations_applied": all_migrations_applied,
            "is_media_writable": is_media_writable,
        },
    )
