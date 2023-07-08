import logging

import settings


class SetupConfig(settings.Config):
    def __init__(self):
        self.log_dir = ""

    def setup_interact(self):
        pass



