"""This example exists to show multiple commands"""

import easyargs

@easyargs
class GitClone(object):
    """A git clone"""

    def clone(self, src, _dest):
        """Clone a repository"""

    def commit(self, a=False, m=None, amend=False):
        """Commit a change to the index"""

if __name__ == '__main__':
    GitClone()
