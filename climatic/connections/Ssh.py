import pexpect

from .Connection import Connection

# Increase the PTY window size to to try to avoid truncating command output
PTY_WINSIZE_ROWS = 24
PTY_WINSIZE_COLS = 500

SSH_PORT = 22


class Ssh(Connection):
    """ Connects to a CLI using SSH.
    The device should have the IP configured.
    """

    def __init__(self, ip: str, user: str, port=SSH_PORT, ciphers: str = None):
        """ Initialize the SSH connection object.
        @param ip       IP address to connect to. Ex: '192.168.33.4'.
        @param user     The SSH connection user.
        @param port     The SSH connection port. Default is 22.
        @param ciphers  A comma sepparated list of ciphers. Ex: 'blowfish-cbc,3des-cbc'
        """
        self.user = user
        self.ip = ip
        self.port = port
        self.ciphers = ciphers

        Connection.__init__(self)

    def connect(self, logfile, logger=None):
        """ Start the SSH connection.
        @param logfile  Log file to save connection outputs.
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Connecting to SSH (%s).", self.ip)

        cipher_spec = ''
        if self.ciphers != None:
            cipher_spec = '-c {}'.format(self.ciphers)

        self.terminal = pexpect.spawn('ssh -p {2} {0}@{1} {3}'.format(
            self.user, self.ip, self.port, cipher_spec), logfile=logfile, encoding='utf-8')
        self.terminal.setwinsize(PTY_WINSIZE_ROWS, PTY_WINSIZE_COLS)

    def disconnect(self, logger=None):
        """ For SSH, the connection is closed during the logout
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Disconnecting from SSH (%s).", self.ip)
