# CONTRIBUTING

django-voting-app is opened to any contribution.

## Conventions

The project uses :

* black formatting
* isort
* google style for documentation

## Commits

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) convention.

Changelog should be generated using [https://github.com/conventional-changelog/conventional-changelog](https://github.com/conventional-changelog/conventional-changelog)

## Version number

Version numbers follow the [Sementic Versionning](https://semver.org/) convention.

## Branches

There are two special branches on the project :

* main
* dev

When writing new code, except for critical quick fixes, you should create a new branch from dev and make a merge request to dev without updating the version number or the changelog. Dev will be merged into main when releasing a new version, where the version number and the changelog will be updated.

When writing code for a critical quick fix, you should create a new branch fro main, and then merge into main with the changelog and version number changed.

## Working on issues

If you want to work on an issue, please say you want by commenting on the issue. This prevents duplicate work.
