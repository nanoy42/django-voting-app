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

import toml
from pathlib import Path
from django.db.migrations.executor import MigrationExecutor
from django.db import connections


def compare_versions(current, available):
    """Compare two versions. They should be in the format
    MAJOR.MINOR.PATCH.

    Returns "major" if the major numbers are different.
    Returns "minor" if the minor numbers are different.
    Returns "patch" if the patch numbers are different.
    Returns "equal" if the two versions are the same.

    Args:
        current (string): the current version.
        available (string): the available version

    Returns:
        string: the level on which the two versions differ.
    """

    current_major, current_minor, current_patch = current.split(".")
    available_major, available_minor, available_patch = available.split(".")

    if current_major != available_major:
        return "major"

    if current_minor != available_minor:
        return "minor"

    if current_patch != available_patch:
        return "patch"

    return "equal"


def get_dependencies():
    path = Path(__file__).parent.parent.parent.absolute()
    file = open(path / "poetry.lock")
    toml_ob = toml.load(file)
    res = []
    for package in toml_ob["package"]:
        if package["category"] == "main":
            res.append((package["name"], package["version"]))
    return res


def is_database_synchronized(database):
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)
