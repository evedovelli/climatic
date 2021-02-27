import time
import logging

from random import randint

####################################################################################################
## Formatter

class Formatter(logging.Formatter):
    """ Define custom log formatter
    """

    def __init__(self):
        """ Initialize Formatter
        """
        logging.Formatter.__init__(
            self, "%(asctime)s %(name)s %(levelname)s %(message)s", '%H:%M:%S')


    def format(self, record):
        """ Process a log record and add identation for each line.

        @param record    The LogRecord to be formatted.
        """
        str = logging.Formatter.format(self, record)
        return '\n | '.join(str.splitlines())


####################################################################################################
## ColoredFormatter

def ansi_color(text=None, background=None, bold=False, faint=False, underline=False):
    colors = {'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
              'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7}
    attrs = ['0']

    if bold:
        attrs.append('1')
    if faint:
        attrs.append('2')
    if underline:
        attrs.append('4')
    if text:
        attrs.append('3%d' % colors[text])
    if background:
        attrs.append('4%d' % colors[background])

    return '\033[%sm' % ';'.join(attrs)


colors = {
    'DEBUG':    {'html': 'green',   'ansi': ansi_color('white', 'green')},
    'INFO':     {'html': 'black',   'ansi': ansi_color('white', 'blue')},
    'WARNING':  {'html': 'orange',  'ansi': ansi_color('white', 'yellow', bold=True)},
    'ERROR':    {'html': 'crimson', 'ansi': ansi_color('white', 'red', bold=True)},
    'CRITICAL': {'html': 'magenta', 'ansi': ansi_color('white', 'magenta', bold=True)},
}

colorlist = [
    {'html': 'darkslategray',  'ansi': ansi_color('black', faint=True)},
    {'html': 'black',          'ansi': ansi_color('black', bold=True)},
    {'html': 'cyan',           'ansi': ansi_color('cyan')},
    {'html': 'teal',           'ansi': ansi_color('cyan', bold=True)},
    {'html': 'yellow',         'ansi': ansi_color('yellow')},
    {'html': 'orange',         'ansi': ansi_color('yellow', bold=True)},
    {'html': 'indigo',         'ansi': ansi_color('magenta')},
    {'html': 'purple',         'ansi': ansi_color('magenta', bold=True)},
    {'html': 'red',            'ansi': ansi_color('red')},
    {'html': 'crimson',        'ansi': ansi_color('red', bold=True)},
    {'html': 'green',          'ansi': ansi_color('green')},
    {'html': 'limegreen',      'ansi': ansi_color('green', bold=True)},
    {'html': 'mediumseagreen', 'ansi': ansi_color('green', faint=True)},
    {'html': 'navy',           'ansi': ansi_color('blue')},
    {'html': 'royalblue',      'ansi': ansi_color('blue', bold=True)},
]

class ColoredFormatter(logging.Formatter):
    """ Define log formatter with colors ('cause colored ink is free in screens)
    """

    def __init__(self):
        """ Initialize ColoredFormatter
        """
        f = "%(w_color)s%(asctime)s %(name)s{0} %(l_color)s[%(levelname)s]{0} %(message)s".format(
            ansi_color())
        logging.Formatter.__init__(self, f, '%H:%M:%S')

    def format(self, record):
        """ Process a log record, add colors, and add identation for each line.

        @param record    The LogRecord to be formatted.
        """
        record.w_color = colors[record.name]['ansi']
        record.l_color = colors[record.levelname]['ansi']
        str = logging.Formatter.format(self, record)

        pipe_color = record.w_color if record.levelno <= logging.INFO else record.l_color
        return '\n {0}|{1} '.format(pipe_color, ansi_color()).join(str.splitlines())


####################################################################################################
## Loggers information

def start(name, log_to_stdout=True, colored=True):
    """ Instantiate and configure logger.
    @param name           Name for the logger.
    @param log_to_stdout  If True, outputs to STDOUT.
    @param colored        If True, outputs with colors.
    """
    if not name in colors:
        # Assign random color if none supplied.
        colors[name] = colorlist[randint(0, len(colorlist) - 1)]

    logger = logging.getLogger(name)

    # Avoid configuring the same logger twice. Otherwise he would have the messages
    # replicated as it would have more than on Handler configured.
    if not hasattr(logger, 'configured'):
        logger.setLevel(logging.INFO)
        if log_to_stdout:
            stdout_handler = logging.StreamHandler()
            if colored:
                stdout_handler.setFormatter(ColoredFormatter())
            else:
                stdout_handler.setFormatter(Formatter())
            logger.addHandler(stdout_handler)
        logger.configured = True
    return logger
