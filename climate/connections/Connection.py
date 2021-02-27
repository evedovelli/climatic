class Connection():
    """ Interface class for CLI connections.
    """

    def __init__(self):
        self.terminal = None

    def connect(self, log):
        """ Open the connection to the CLI.
        The 'connect' method should open a pexpect connection to CLI with the
        'pexpect.spawn' command. self.terminal must be filled with the open connection.

        @param log   The log for the connection. Use it as the 'logfile' in the spawn command.
        """
        raise NotImplementedError(
                "The 'connect' method MUST be implemented in inherit connection class.")

    def disconnect(self):
        """ Terminate connection.
        The 'disconnect' will close the pexpect connection.
        """
        raise NotImplementedError(
                "The 'disconnect' method MUST be implemented in inherit connection class.")
