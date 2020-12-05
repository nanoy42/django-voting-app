.. django-voting-app documentation master file, created by
   sphinx-quickstart on Sun Oct 18 02:17:20 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-voting-app's documentation!
=============================================

This is documentation for django-voting-app version 1.0.0.

django-voting-app is small django app tor organize votes.

Here is a quick recap of the functionalities :

   * Create votes, with a limited time (time of beginning and time of end)
   * Restrict votes to groups
   * Restrict the access to active members
   * Create as many questions and as many possible answers in a vote (no free choice allowed though)
   * Attach documents to a vote
   * Votes are anonymous, but it is possible to know who voted (this is required (we could find solution without) to ensure that someone doesn't vote twice)
   * Translate votes, questions and answers.

.. toctree::
  :maxdepth: 2
  :caption: Contents:

  installation
  configuration
  creating_votes
  voting_process_and_results
