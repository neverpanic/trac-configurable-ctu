import os

from setuptools import setup

def read_deps(filename):
    absfilename = os.path.join(os.path.dirname(__file__), filename)
    with open(absfilename) as f:
        return [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

setup(
    name='trac-configurable-ctu',
    version='1.0',
    author='Clemens Lang',
    author_email='cal@macports.org',
    url='https://github.com/neverpanic/trac-configurable-committicketupdater',
    description='Trac - CommitTicketUpdater from Trac core with configurable'
                'options, for example for use with GitHub',
    packages=['trac_configurable_ctu'],
    install_requires=read_deps('requirements.txt'),
    platforms='all',
    license='BSD',
    entry_points={'trac.plugins': [
        'trac-configurable-ctu.committicketupdater = trac_configurable_ctu:ConfigurableCommitTicketUpdater',
        'trac-configurable-ctu.committicketreferencemacro = trac_configurable_ctu:ConfigurableCommitTicketReferenceMacro',
    ]},
)
