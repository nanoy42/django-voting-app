# django-voting-app
<p align="center">

[![Documentation Status](https://readthedocs.org/projects/django-voting-app/badge/?version=latest)](https://django-voting-app.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/nanoy42/django-voting-app/badge.svg?branch=main)](https://coveralls.io/github/nanoy42/django-voting-app?branch=main)
[![github-actions](https://github.com/nanoy42/django-voting-app/workflows/Django%20CI/badge.svg)](https://github.com/nanoy42/django-voting-app/workflows/Django%20CI)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)]("https://github.com/psf/black)
[![GitHub release](https://img.shields.io/github/release/nanoy42/django-voting-app.svg)](https://github.com/nanoy42/django-voting-app/releases/)

![logo](https://github.com/nanoy42/django-voting-app/raw/main/res/logo/logo.png "Logo")

</p>
django-voting-app is a simple django app to organise votes.

Summary :

 * [Functionalities](#functionalities)
 * [Supported languages](#supported-languages)
 * [Documentation](#documentation)
 * [Screenshots](#screenshots)
 * [License](#license)
 * [Tests and dev](#tests-and-dev)

## Functionalities

 * Create votes, with a limited time (time of beginning and time of end)
 * Restrict votes to groups
 * Restrict the access to active members
 * Create as many questions and as many possible answers in a vote (no free choice allowed though)
 * Attach documents to a vote
 * Votes are anonymous, but it is possible to know who voted (this is required (we could find solution without) to ensure that someone doesn't vote twice)
 * Translate votes, questions and answers.

## Supported languages

django-voting-app supports:

 * English (100%)
 * French (100%)

The documentation is however only available in English.

## Documentation

The full documentation is available at [https://django-voting-app.readthedocs.io/en/latest](https://django-voting-app.readthedocs.io/en/latest).

## Screenshots

![home](https://github.com/nanoy42/django-voting-app/raw/main/res/screenshots/home.png "Home page")

![home](https://github.com/nanoy42/django-voting-app/raw/main/res/screenshots/votes-index.png "Votes index")

![home](https://github.com/nanoy42/django-voting-app/raw/main/res/screenshots/vote.png "Vote")

![home](https://github.com/nanoy42/django-voting-app/raw/main/res/screenshots/results.png "Results")

## License

django-voting-app - Simple django app to organise votes
Copyright (C) 2020 Yoann Piétri

django-voting-app is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

django-voting-app is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with django-voting-app. If not, see <https://www.gnu.org/licenses/>.

## Tests and dev

You can run the tests using the command 

```
python3 manage.py test core
```

Using with coverage : 

```
coverage run --source='src' src/manage.py test core
```

You can install the dev requirements with 

```
pipenv install --dev
```

or 

```
pip install -r requirements.txt
```