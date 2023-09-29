import configparser
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import traceback

import feedparser

DEFAULT_CONFIG_FILE = Path('~/.config/fgscripts/acsconfig.ini').expanduser()

DEFAULT_FEED = "https://sundaystrippedp.podbean.com/rss"
DEFAULT_DOWNLOAD = Path("/tmp")
DEFAULT_DESTINATION = Path("/tmp")

DEFAULT_ARTIST = "Show Name"
DEFAULT_TITLE_PATTERN = "Segment {:1}"

DEFAULT_DURATION = 15
DEFAULT_THRESHOLD = -60
DEFAULT_OUTPUT_PATTERN = "OUTPUT{}.mp3"

DEFAULT_LOG_DIR = "~/.logs/fgscripts"
DEFAULT_LOG_FILE = "rss_audio.log"
DEFAULT_LOGGER_NAME = "fgscripts PodBean RSS Logger"
LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=True,
    formatters={
        'precise': {
            'format': '%(asctime)s %(levelname)s:~ %(filename)s - %(module)s - %(funcName)s ~: %(message)s',
            'datefmt': '%Y%m%d %H.%M.%S'
        },
        'brief': {
            'format': '%(asctime)s %(levelname)s: %(message)s',
            'datefmt': '%Y%m%d %H.%M.%S'
        }
    },
    handlers={
        'stream': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'brief'
        },
    },
    loggers={
        DEFAULT_LOGGER_NAME: {
            'handlers': ['stream'],
            'level': 'INFO',
            'propagate': False
        }
    }
)


def _makedirs(path):
    if Path.is_dir(path):
        logging.info(f'{path} already exists')
    else:
        try:
            Path.mkdir(path)
            logging.info(f'{path} created')
        except FileNotFoundError as exc:
            logging.critical(exc)
            print(exc)
            raise


def get_fgLogger():
    return logging.getLogger(DEFAULT_LOGGER_NAME)


def init_logging(log_dir=Path(DEFAULT_LOG_DIR).expanduser(), email_config=None):
    logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    logging.config.dictConfig(LOGGING_CONFIG)

    if log_dir:
        _makedirs(Path(log_dir))
        log_file = Path(log_dir, DEFAULT_LOG_FILE)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes = 1048576,
            backupCount = 5
        )

        formatter = LOGGING_CONFIG['formatters']['precise']
        _format = logging.Formatter(formatter['format'], datefmt = formatter['datefmt'])
        file_handler.setFormatter(_format)
        file_handler.doRollover()
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if email_config is not None:
        if email_config['password'] == "OS_ENVIRON":
            password = os.environ.get('EMAILPASS')
        else:
            password = email_config['password']

        if email_config['port'] is not None:
            port = email_config['port']
        else:
            port = "25"

        if email_config['secure'] is not None:
            secure = email_config['secure']
        else:
            secure = ()

        try:
            print('try')
            mail_handler = logging.handlers.SMTPHandler(
                mailhost = (email_config['mailhost'], port),
                fromaddr = email_config['from_name'],
                toaddrs = email_config['recipients'],
                subject = email_config['subject'],
                credentials = (email_config['username'], password),
                secure = secure,
            )
            brief_format = LOGGING_CONFIG['formatters']['brief']
            mail_format = logging.Formatter(brief_format['format'], datefmt = brief_format['datefmt'])
            mail_handler.setFormatter(mail_format)
            mail_handler.setLevel(logging.WARN)
            logger.addHandler(mail_handler)
        except Exception as e:
            error = traceback.format_exc()
            logger.critical(error)

class Config:
    def __init__(self):
        self.feed = ""
        self.download = ""
        self.destination = ""

        self.artist = ""
        self.title_pattern = ""

        self.duration = 0
        self.threshold = 0
        self.output_pattern = ""
        self.logger = ""


    def get_config(self, config_file=DEFAULT_CONFIG_FILE, email=False, verbose=False):
        if Path.is_file(Path(config_file)):
            config = configparser.ConfigParser()
            config.read(config_file)

            log_dir = Path(config['directories']['logdir'])
            print(log_dir)
            if email:
                init_logging(log_dir, config['email'])
            else:
                init_logging(log_dir)


            self.feed = config['directories']['feed']
            self.download = Path(config['directories']['download'])
            self.destination = Path(config['directories']['destination'])

            self.artist = config['metadata']['artist']
            self.title_pattern = config['metadata']['title_pattern']

            self.duration = float(config['silence']['duration'])
            self.threshold = int(config['silence']['threshold'])
            self.output_pattern = str(Path(self.download, config['silence']['output_pattern']))
        else:
            init_logging()
            self.logger = get_fgLogger()

            if email:
                self.logger.warning('email is not configured by default and will not be possible')

            self.feed = DEFAULT_FEED
            self.download = DEFAULT_DOWNLOAD
            self.destination = DEFAULT_DESTINATION

            self.artist = DEFAULT_ARTIST
            self.title_pattern = DEFAULT_TITLE_PATTERN

            self.duration = DEFAULT_DURATION
            self.threshold = DEFAULT_THRESHOLD
            self.output_pattern = DEFAULT_OUTPUT_PATTERN

        self.logger = get_fgLogger()

        if verbose:
            self.logger.setLevel(logging.DEBUG)

        self.validate_config(email)

    def validate_config(self, email=False):
        feed = feedparser.parse(self.feed)
        if feed.status != 200 and feed.status != 302:
            self.logger.critical(feed.status)
            self.logger.critical(f'Feed URL: {self.feed}')
            self.logger.critical('The feed url is not valid')
        else:
            self.logger.debug(f'Feed URL: {self.feed} appears to be valid, returned status: {feed.status}')

        if Path.is_dir(self.download):
            self.logger.debug(f'Using download directory: {self.download}')
        else:
            self.logger.critical(f'{self.download} is not a valid directory')

        if Path.is_dir(self.destination):
            self.logger.debug(f'Using destination directory: {self.destination}')
        else:
            self.logger.critical(f'{self.destination} is not a valid directory.')

        self.logger.debug(f'Using duration: {self.duration} seconds')
        self.logger.debug(f'Using threshold: {self.threshold}db')
        self.logger.debug(f'Output pattern: {self.output_pattern}')
        self.logger.debug(f'Test output: {self.output_pattern.format(1)}')
        self.logger.debug(f'Artist: {self.artist}')
        self.logger.debug(f'Title pattern: {self.title_pattern}')
        self.logger.debug(f'Test title: {self.title_pattern.format(1)}')

