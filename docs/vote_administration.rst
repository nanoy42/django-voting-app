Administration guide
====================

This guide targets the administrators that want to know how to create votes, questions and answers on django-voting-app.

All the described operations can be done in the admin panel (accessible with the ``/admin`` url or by clicking on your username and then Admin).

Create votes, questions an answers
##################################

Votes
~~~~~

You can create votes ont the admin panel. You need to specify 

* a name
* a begin date
* a end date
* if voters will be displayed on the results page
* if the results are public (i.e. can be accessed by non staff members)

.. warning:: The see_voters option will only be editable when creating the vote and not editing it afterwards.

You can optionally add :

* a description
* restrictions on groups
* translation of some fields (see the related section)

The restriction to a specific vote is made using groups. If you specify one (or more) group(s) the user must be in one the groups in order to access the vote.
If you don't specify any group, any (active) user can access the vote.

User who are not active can't connect to the interface.

A vote is accessible to a user if the 3 following conditions are met :

* the vote has begun (i.e. the begin date is passed) and has not yet ended (i.e. the end date is not passed)
* the vote is ready (see related section)
* the user has the right of vote for this vote (i.e. he has not yet voted and the conditions on groups are met)

Questions
~~~~~~~~~

For each vote, you can create an unlimited number of questions. On the voting page, all questions will be displayed and the user must answer to every one of them.

.. note:: If you want your users to be able to skip a question of the vote, you can always add a "don't know" answer.

You can create questions on the admin panel. You need to specify :

* a related vote
* a text, which is the question

Additionally you can add :

* translations for some fields (see the related section)

A question must be related to a unique vote. 

.. warning:: It is a bad idea to change the vote of an answer afterwards (after the vote has begun to be more precise). You will get wrong results if you do so.

Answers
~~~~~~~

For each question, you can create an unlimited number of answers. Users will have to select a unique answer for each question.

You can create answers on the admin panel. You need to specify : 

* a related question
* the answer

Additionally you can add :

* translations for some fields (see the related section).

An answer must be related to a unique question.

.. warning:: It is a bad idea to change the question of an answer afterwards (after the vote has begun to be more precise). You will get wrong results if you do so.

Documents
#########

Documents are files to help people vote. There are displayed on the voting page.

For each vote, you can link an unlimited number of documents. A document is related to a unique vote.

You can create documents on the admin panel. You need to specify :

* a vote
* a name
* a file

Additionally you can add :

* translations for some fields (see the related section)

Readyness
#########

Votes will not begin if they are not ready. In fact they will not be displayed on available votes.

When you make a vote ready, you should no longer make any modification. The app will prevent you from doing certain modification but not all of them.

When a vote is ready, you cannot make the vote not ready again (you have to delete it and start again).

To make a vote ready, you can use the action ont the admin panel or go to the administrators index of votes.

See results
###########

Depending on ``VOTE_SEE_BEFORE_END`` you will be able to see the results as the vote goes or when the vote is passed.

You can see the results of all the votes on the corresponding page.

Only administrators can see the results.

A note on translations
######################

Some fields may be translated to another languages. By default you can translate to any languages supported by the app, namely 

* en (English)
* fr (French)

If you want more (or less) languages, you can edit the ``MODELTRANSLATION_LANGUAGES`` parameter.

The following fields can be translated :

+----------+---------------------+
| Model    | Translatable fields |
+==========+=====================+
| Vote     | name, description   |
+----------+---------------------+
| Question | text                |
+----------+---------------------+
| Answer   | answer              |
+----------+---------------------+
| Document | name, document      |
+----------+---------------------+


Dynamic vote creation
#####################

In addition to the previous documentation, it is possible from version 1.3.0 to create the vote, the questions, the answers and the documents using a single web page.

This is only accessible to staff member. The remarks are the same as before.

.. warning:: This is tagged as experimental on version 1.3.0 and onwards.