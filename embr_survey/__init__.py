# get this stuff out of the way so that when we create the window,
# we don't end up with programmable/fixed-function conflict
import os
import sys
import logging


# https://stackoverflow.com/a/39215961/2690232


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def setup_logger(pth, now):
    embr_logger = logging.getLogger('embr_survey')
    embr_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(pth, '%slog.log' % now))
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sl = StreamToLogger(embr_logger, logging.ERROR)
    sys.stderr = sl
    embr_logger.addHandler(fh)
