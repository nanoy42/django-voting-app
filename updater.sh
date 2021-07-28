#!/bin/bash
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

# Updater script for django-voting-app.

REPO="nanoy42/django-voting-app"

# Colors
RED='\033[1;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_logo () {
    printf "\n"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@.                   &@@@@@@@@@"
    echo "@@@@@@@@@@.        @@@        &@@@@@@@@@"
    echo "@@@@@@@@@@.       @@@@%       &@@@@@@@@@"
    echo "@@@@@@@@@@.      #######      &@@@@@@@@@"
    echo "@@@@@@@@@@.                   &@@@@@@@@@"
    echo "@@@@@@@   .                   #   @@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@      @@@@@  @@@@@@# *@@@@@  #@@@@@@"
    echo "@@@@  @@@@, (@@@  @@@@@  @@@@@  * @@@@@@"
    echo "@@@@  @@@@@  @@@% #@@@. @@@@@  @@  @@@@@"
    echo "@@@@  @@@@@  @@@@  @@@ #@@@@& #@@@ *@@@@"
    echo "@@@@  @@@@@  @@@@@ .@  @@@@@        &@@@"
    echo "@@@@  @@&   @@@@@@& , @@@@@  @@@@@@  @@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
}

print_help () {
    printf "updater.sh - Updater for django-voting-app. \n"
    printf "Usage:\n"
    printf "  $0 [-f | --force]\n"
    printf "  $0 (-h | --help)\n"
    printf "Options:\n"
    printf "  -f --force Force the update even if there is major changes or different branch than main\n"
    printf "  -h --help  Show this help\n"
}

get_current_version () {
    current_version=$(git describe --tags --abbrev=0 | grep -Po '([0-9\.]+)')
    echo "$current_version"
}

get_last_version () {
    last_version=$(curl --silent "https://api.github.com/repos/$REPO/releases/latest" | grep -Po '"tag_name": "v\K.*?(?=")')
    echo "$last_version"
}

compare_version () {
    IFS='.'
    read -a version1_split <<< "$1"
    read -a version2_split <<< "$2"

    version1_major=${version1_split[0]}
    version2_major=${version2_split[0]}

    version1_minor=${version1_split[1]}
    version2_minor=${version2_split[1]}

    version1_patch=${version1_split[2]}
    version2_patch=${version2_split[2]}

    if [ $version1_major != $version2_major ]
    then
        echo "major"
    elif [ $version1_minor != $version2_minor ]
    then
        echo "minor"
    elif [ $version1_patch != $version2_patch ]
    then
        echo "patch"
    else
        echo "equal"
    fi
}

get_branch_name () {
    branch_name=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
    echo $branch_name
}

update () {
    printf "\n"
    git pull --rebase --stat origin main
    printf "\n"
}

print_changelog () {
    changelog=$(curl --silent "https://api.github.com/repos/$REPO/releases/latest" | grep -Po '"body": "\K.*?(?=")')
    printf "$changelog\n"
}

var_help=false
var_force=false
do_update=false

for var in "$@"
do
    known_option=false
    if [ $var = "--help" ] || [ $var = "-h" ]
    then
        var_help=true
        known_option=true
    fi

    if [ $var = "--force" ] || [ $var = "-f" ]
    then
        var_force=true
        known_option=true
    fi

    if [ "$known_option" = false ]
    then
        printf "${YELLOW}Unkown option $var${NC}\n"
    fi
done


if [ "$var_help" = true ]
then
    print_help
else
    print_logo
    
    printf "\nWelcome to django-voting-app updater\n\n"

    printf "${YELLOW}This script was introduced in version 1.3.0 and is tagged as experiemntal\n\n${NC}"

    if [ -d .git ]
    then

        current_version="$(get_current_version)"
        last_version="$(get_last_version)"
        branch_name="$(get_branch_name)"

        if [ -z $last_version ]
        then
            printf "${RED}Can't find the latest available version${NC}\n"
            exit 1
        fi

        comparison=$(compare_version $current_version $last_version)

        printf "Current version: $current_version\n"
        printf "Available version: $last_version\n"
        printf "On branch: $branch_name\n\n"

        if [ $comparison = "equal" ]
        then
            printf "${GREEN}No update to do !${NC}\n"
            exit 0
        fi

        if [ $branch_name != "main" ]
        then
            if [ "$var_force" != true ]
            then
                printf "${RED}Update from another branch than main is not recommended.${NC}\n"
                printf "${RED}The -f | --force is not present and the branch is not main. Aborting the update.${NC}\n"
                exit 1
            else
                printf "${YELLOW}Update from another branch than main is not recommended.${YELLOW}\n"
                printf "${YELLOW}The -f | --force is present. Ignoring the branch.${NC}\n"
            fi
        printf "\n"
        fi
        
        if [ $comparison = "patch" ]
        then
            printf "${BLUE}Patch update to do.${NC}\n"
            do_update=true
        elif [ $comparison = "minor" ]
        then
            printf "${BLUE}Minor update to do.${NC}\n"
            do_update=true
        elif [ $comparison = "major" ]
        then
            if [ "$var_force" != true ]
            then
                printf "${RED}Major update to do.${NC}\n"
                printf "${RED}The -f | --force is not present. Aborting the update.${NC}\n"
                exit 1
            else
                printf "${YELLOW}Major update to do.${NC}\n"
                printf "${YELLOW}The -f | --force is present. Attempting the update.${NC}\n"
                do_update=true
            fi
        fi
    else
        printf "${RED}django-voting-app was not installed using git. Cannot update.${NC}\n"
        exit 1
    fi
fi

if [ "$do_update" = true ]
then
    update
    new_current_version="$(get_current_version)"
    new_comparison=$(compare_version $new_current_version $last_version)

    if [ $new_comparison != "equal" ]
    then
        printf "${RED}Update failed.${NC}\n"
        exit 1
    fi

    print_changelog
    printf "\n"
    printf "${GREEN}Update successful.${NC}\n"
fi

exit 0