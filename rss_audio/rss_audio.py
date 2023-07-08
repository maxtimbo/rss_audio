import argparse
import logging

import create_ini
import helptext
import settings
from settings import Config
import rss_runner
from split_audio import split_audio

def Main():
    parser = argparse.ArgumentParser(description=helptext.HELPTEXT)
    group = parser.add_mutually_exclusive_group()
    subparsers = parser.add_subparsers(dest="subparser")

    group.add_argument('--new_config', help='create a new blank config file')
    group.add_argument('--setup', help='instructions to configure or modify config file', action='store_true')

    normal_run = subparsers.add_parser("run")
    normal_run.add_argument('-c', '--config', help='optional config file')

    normal_run.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    normal_run.add_argument('-e', '--email', help='email log output', action='store_true')

    args = parser.parse_args()

    if args.new_config is not None:
        create_ini.new_ini(args.new_config)
    else:

        if args.setup:
            print(helptext.SETUP_TEXT)

        else:
            config = Config()

            if args.config:
                config.get_config(args.config, email=args.email, verbose=args.verbose)
            else:
                config.get_config(email=args.email, verbose=args.verbose)

            logger = settings.get_fgLogger()

            if args.verbose:
                logger.setLevel(logging.DEBUG)

            if args.email:
                print('email')

            mp3_link = rss_runner.get_newest_entry(config.feed)
            local_filename = rss_runner.download_audio(mp3_link, config.download)
            split_audio(local_filename, config.output_pattern, config.threshold, config.duration, verbose=args.verbose)


if __name__ == '__main__':
    Main()

