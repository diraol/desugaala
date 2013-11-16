"""Views from vote app. """

import datetime
from random import shuffle
from functools import wraps

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.timezone import utc

from .models import Category, Option, Ballot, BallotCategory
from .models import BallotOption, AlreadyVoted
from .forms import LoginForm
from .helpers import json_rest, throttle_post

DEMO_MODE = getattr(settings, 'DEMO_MODE', False)


def perform_checks(func):
    @wraps(func)
    def inner(request, data, *args, **kwargs):
        try:
            uid = int(data['username'])
            user_row = dict(user_id=uid)

            if AlreadyVoted.objects.filter(user_id=user_row['user_id']).exists():
                return dict(result='already_voted')

            return func(request, data, user_row, *args, **kwargs)
        except ValueError:
            return dict(result='login_failed')

    return inner


def handle_errors(func):
    return func


@ensure_csrf_cookie
def vote_page(request):
    categories = Category.objects.all()
    options = []
    for category in categories:
        categoryOptions = list(category.option_set.all())
        shuffle(categoryOptions)
        options.append(categoryOptions)

    vars = dict(
        categories_options=zip(categories, options),
        login_form=LoginForm(),
        DEMO_MODE=DEMO_MODE,
        GOOGLE_ANALYTICS_TOKEN=getattr(settings, 'GOOGLE_ANALYTICS_TOKEN', '')
    )

    return render(request, 'vote.jade', vars)


@throttle_post
@json_rest
@perform_checks
def login_api(request, data, user_row):
    return dict(result='ok')


@throttle_post
@json_rest
@perform_checks
@handle_errors
def vote_api(request, data, user_row):
    timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)

    # mark user as already voted
    already_voted = AlreadyVoted(
        user_id=user_row['user_id'],
        ip_address=request.META['REMOTE_ADDR'],
        user_agent=request.META['HTTP_USER_AGENT'],
        timestamp=timestamp
    )

    ballot = Ballot(
        ip_address=request.META['REMOTE_ADDR'],
        user_agent=request.META['HTTP_USER_AGENT'],
        timestamp=timestamp
    )

    ballot_categories = []

    for categoryId, optionIds in data['ballot'].iteritems():
        # check that category exists
        category = Category.objects.get(id=int(categoryId))
        ballot_category = BallotCategory(category=category)
        ballot_options = []

        # check that every option only occurs once
        optionIds = [int(optionId) for optionId in optionIds]
        if len(set(optionIds)) != len(optionIds):
            raise ValueError('forged ballot with duplicate ids')

        for index, optionId in enumerate(optionIds):
            # check that options belong to this category
            option = Option.objects.get(id=optionId, category=category)

            ballot_options.append(BallotOption(
                order=index,
                option=option
            ))

        ballot_categories.append((ballot_category, ballot_options))

    # all checks passed, commit

    if not DEMO_MODE:
        already_voted.save()

    ballot.save()

    for ballot_category, ballot_options in ballot_categories:
        ballot_category.ballot = ballot
        ballot_category.save()

        for ballot_option in ballot_options:
            ballot_option.ballot_category = ballot_category
            ballot_option.save()

    return dict(result='ok')
