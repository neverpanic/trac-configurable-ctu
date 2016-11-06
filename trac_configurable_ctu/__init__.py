"""
An extension of the standard Trac CommitTicketUpdater that allows configuring
a separate ticket_prefix regex. This is helpful in situations where the default
ticket reference rules are not applicable, such as when using GitHub, which
claims #[0-9]+.
"""

import re

from genshi.builder import tag

from trac.config import Option, ConfigSection
from trac.resource import Resource
from trac.versioncontrol import RepositoryManager
from trac.versioncontrol.web_ui.changeset import ChangesetModule
from trac.wiki.formatter import format_to_html
from tracopt.ticket.commit_updater import CommitTicketUpdater, CommitTicketReferenceMacro

class ConfigurableCommitTicketUpdater(CommitTicketUpdater):
    """
    An extension of Trac's CommitTicketUpdater that listens for new commits
    referencing tickets using a number of keywords and a configurable ticket
    prefix.
    """

    ticket_prefix = Option(
        'ticket', 'commit_ticket_update_ticket_prefix',
        CommitTicketUpdater.ticket_prefix,
        """Regular expression matching (but not capturing) the prefix that
        CommitTicketUpdater should look for in commit messages.""")

    @property
    def ticket_reference(self):
        """
        Return a regular expression that will match ticket references.
        """
        return self.ticket_prefix + '[0-9]+'

    @property
    def ticket_command(self):
        """
        Return a regular expression that will match ticket commands in the form
        of <action> <ticket-ref>.
        """
        return (r'(?P<action>[A-Za-z]*)\s*.?\s*'
                r'(?P<ticket>%s(?:(?:[, &]*|[ ]?and[ ]?)%s)*)' %
                (self.ticket_reference, self.ticket_reference))

    @property
    def ticket_re(self):
        """
        Return a compiled regular expression that will match tickets. The first
        match group will contain the ticket number.
        """
        return re.compile(self.ticket_prefix + '([0-9]+)')

    def make_ticket_comment(self, repos, changeset):
        """Create the ticket comment from the changeset data."""
        rev = changeset.rev
        revstring = str(rev)
        drev = str(repos.display_rev(rev))
        if repos.reponame:
            revstring += '/' + repos.reponame
            drev += '/' + repos.reponame
        return """\
In [changeset:"%s" %s]:
{{{
#!ConfigurableCommitTicketReference repository="%s" revision="%s"
%s
}}}""" % (revstring, drev, repos.reponame, rev, changeset.message.strip())

class ConfigurableCommitTicketReferenceMacro(CommitTicketReferenceMacro):
    """
    An extension of Trac CommitTicketUpdater's CommitTicketReferenceMacro that
    does not search for occurrences of the ticket reference in a referenced
    commit's message. This avoids the dependency on CommitTicketUpdater.
    """

    # pylint: disable=abstract-method

    ticket_replace_section_name = 'commit-ticket-update-replace'
    ticket_replace_section = ConfigSection(ticket_replace_section_name,
        """In this section, you can define patterns for substitution in the
        commit message in the format:

        name.pattern = PR-\d+
        name.replace = https://example.org/$(repository)s/\1

        The name has no further meaning than identifying a pair of pattern and
        replace and will be ignored.

        The following variables will be substituted in both pattern and replace
        before applying the regular expression:

        - $(repository)s    name of the repository committed to
        - $(revision)s      revision of the commit

        Note the usage of `$(...)s` instead of `%(...)s` as the latter form
        would be interpreted by the ConfigParser itself.
        """)

    def expand_macro(self, formatter, name, content, args=None):
        # pylint: disable=too-many-function-args
        args = args or {}
        reponame = args.get('repository') or ''
        rev = args.get('revision')
        # pylint: disable=no-member
        repos = RepositoryManager(self.env).get_repository(reponame)
        try:
            changeset = repos.get_changeset(rev)
            message = changeset.message
            rev = changeset.rev
            resource = repos.resource
        except Exception: # pylint: disable=broad-except
            message = content
            resource = Resource('repository', reponame)
        config = self.ticket_replace_section
        fields = {}
        for key, value in config.options():
            idx = key.rfind('.')
            if idx >= 0:
                prefix, attribute = key[:idx], key[idx+1:]
                field = fields.setdefault(prefix, {})
                field[attribute] = config.get(key)
            else:
                fields[key] = {'': value}
        for prefix, field in fields.iteritems():
            if not all (k in field for k in ['pattern', 'replace']):
                self.log.warn("Ignoring [%s] %s, missing .pattern or .replace"
                    % (self.ticket_replace_section_name, key))
                continue
            subst = {'repository': reponame, 'revision': rev}
            pattern = field['pattern'].replace('$(', '%(') % subst
            replace = field['replace'].replace('$(', '%(') % subst
            message = re.sub(pattern, replace, message)
        if ChangesetModule(self.env).wiki_format_messages:
            message = '\n'.join(map(lambda line: "> " + line, message.split('\n')))
            return tag.div(format_to_html(
                self.env,
                formatter.context.child('changeset', rev, parent=resource),
                message, escape_newlines=True), class_='message')
        else:
            return tag.pre(message, class_='message')
