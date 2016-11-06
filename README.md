Trac - Configurable CommitTicketUpdater
=======================================

Features
--------

This Trac plugin performs the same tasks as [Trac's CommitTicketUpdater](https://trac.edgewall.org/wiki/CommitTicketUpdater)
but gives you the option of changing the regular expression it uses to find
tickets in commit messages. This is useful if a different party already claims
Trac's standard ticket syntax, for example when you are using GitHub.

Requirements
------------

`trac_configurable_ctu` requires Trac ~= 1.0.

To install `trac_configurable_ctu`, use the included `setup.py`, for example
using `pip install` in a directory with the code.

Setup
-----

**`trac_configurable_ctu`** contains two plugins:
 - `ConfigurableCommitTicketUpdater`, and
 - `ConfigurableCommitTicketReferenceMacro`

Both are required for `trac_configurable_ctu` to work correctly.

Edit your `trac.ini` as follows to enable and configure both plugins:

    [components]
    trac_configurable_ctu.ConfigurableCommitTicketReferenceMacro = enabled
    trac_configurable_ctu.ConfigurableCommitTicketUpdater = enabled

    [ticket]
    commit_ticket_update_ticket_prefix = (?:trac-ticket(?:[: ]+)?)

Note that the regular expression to match ticket expressions must not include
the ticket number (which is expected right after the regular expression) and
must not create capturing groups.

The display of the referenced commit messages in the ticket comment can be
modified with replacements using regular expressions. These can be defined in
their own configuration section:

    [commit-ticket-update-replace]
    name.pattern = PR-\d+
    name.replace = https://example.org/$(repository)s/\1

The name has no further meaning than identifying a pair of pattern and replace
and will be ignored.

The following variables will be substituted in both pattern and replace before
applying the regular expression:

- $(repository)s    name of the repository committed to
- $(revision)s      revision of the commit

Note the usage of `$(...)s` instead of `%(...)s` as the latter form would be
interpreted by the ConfigParser itself.

Development
-----------

In a [virtualenv](http://www.virtualenv.org/), install the requirements:

    pip install trac
    pip install tox
    pip install -e .

Run pylint with

    tox -e pylint 

Changelog
---------

### 1.0

* Public release.

License
-------

This plugin is released under the BSD-2-Clause license.

It was initially written for [MacPorts' Trac](https://trac.macports.org/).
