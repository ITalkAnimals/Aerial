"""
Custom colored logger for Aerial Self-Host.
Used for better readability.

(Stolen from this StackOverflow post)
https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""

import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ)
        message = message.replace("$BOLD", BOLD_SEQ)
        message = message.replace("$BLACK", COLOR_SEQ % (30 + BLACK))
        message = message.replace("$RED", COLOR_SEQ % (30 + RED))
        message = message.replace("$GREEN", COLOR_SEQ % (30 + GREEN))
        message = message.replace("$YELLOW", COLOR_SEQ % (30 + YELLOW))
        message = message.replace("$BLUE", COLOR_SEQ % (30 + BLUE))
        message = message.replace("$MAGENTA", COLOR_SEQ % (30 + MAGENTA))
        message = message.replace("$CYAN", COLOR_SEQ % (30 + CYAN))
        message = message.replace("$WHITE", COLOR_SEQ % (30 + WHITE))
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


NAME_COLORS = {
    "DEBUG": BLUE,
    "INFO": GREEN,
    "WARNING": YELLOW,
    "ERROR": RED,
    "CRITICAL": RED,
}

TEXT_COLORS = {
    "DEBUG": WHITE,
    "INFO": WHITE,
    "WARNING": YELLOW,
    "ERROR": RED,
    "CRITICAL": RED,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        if self.use_color and record.levelname in NAME_COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + NAME_COLORS[record.levelname])
                + record.levelname
                + RESET_SEQ
            )
            msg_color = (
                COLOR_SEQ % (30 + TEXT_COLORS[record.levelname])
                + record.msg
                + RESET_SEQ
            )
            record.levelname = levelname_color
            record.msg = formatter_message(msg_color, True)
        return logging.Formatter.format(self, record)


class Logger(logging.Logger):
    FORMAT = f"[$MAGENTA%(name)-11.11s %(levelname).10s$RESET] %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return
