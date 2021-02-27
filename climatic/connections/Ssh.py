import pexpect

from .Connection import Connection

# Adjust the PTY window size to 800 characters wide to try to avoid truncating
# command output
PTY_WINSIZE_ROWS = 24
PTY_WINSIZE_COLS = 800

SSH_PORT = 22

class Ssh(Connection):
    """ Connects to a CLI using SSH.
    The device should have the IP configured.
    """

    def __init__(self, ip: str, user: str, port=SSH_PORT):
        """ Initialize the SSH connection object.
        @param ip    IP address to connect to. Ex: '192.168.33.4'.
        @param user  The SSH connection user.
        @param port  The SSH connection port. Default is 22.
        """
        self.user = user
        self.ip = ip
        self.port = port

        Connection.__init__(self)

    def connect(self, logfile):
        """ Start the SSH connection.
        @param logfile      Log file to save connection outputs.
        """
        # TODO
        #self.logger.debug("Connecting to ssh (%s).", self.ip)

        self.terminal = pexpect.spawn(
            'ssh -p {2} {0}@{1}'.format(self.user, self.ip, self.port), logfile=logfile, encoding='utf-8')
        self.terminal.setwinsize(PTY_WINSIZE_ROWS, PTY_WINSIZE_COLS)

    def disconnect(self):
        """ For SSH, the connection is closed during the logout
        """
        pass
