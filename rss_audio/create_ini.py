import configparser
from pathlib import Path

def new_ini(filename):
    cwd = Path.cwd()
    path = cwd.joinpath(filename)
    if Path.is_file(path):
        print(f'{filename} already exists')
    else:
        config = configparser.ConfigParser()
        config['directories'] = {
            'feed': '',
            'download': '',
            'destination': '',
            'logdir': ''
        }

        config['metadata'] = {
                'artist': '',
                'title_pattern': ''
        }

        config['silence'] = {
            'duration': '',
            'threshold': '',
            'output_pattern': '',
        }

        config['email'] = {
            'mailhost': '',
            'port': '587',
            'from_name': '',
            'recipients': '',
            'username': '',
            'password': '',
            'secure': ''
        }

        with open(filename, 'w') as file_obj:
            config.write(file_obj)

        print(f'{path} created')


