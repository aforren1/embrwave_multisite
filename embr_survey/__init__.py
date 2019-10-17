# get this stuff out of the way so that when we create the window,
# we don't end up with programmable/fixed-function conflict
import os
import sys
import logging
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


is_exe = getattr(sys, 'frozen', False)
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
    if is_exe:
        sys.stderr = sl
    embr_logger.addHandler(fh)


# https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
if is_exe:
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = os.path.join(sys.executable, '..')  # sys.executable for onefile option
else:
    application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
