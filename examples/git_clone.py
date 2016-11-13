"""This example exists to show multiple commands"""

import easyargs

@easyargs
class GitClone(object):
    """A git clone"""

    def clone(self, src, _dest):
        """
        Clone a repository
        :param src: The source repository to clone from
        :param _dest: The directory to check the source code to
        """

    def commit(self, a=False, m=None, amend=False):
        """
        Commit a change to the index
        :param a: Add all tracked files to the index
        :param m: Supply the commit message on the command line
        :param amend: Amend the previous commit
        """
        print 'Committing {m}'.format(m=m)

if __name__ == '__main__':
    GitClone()
