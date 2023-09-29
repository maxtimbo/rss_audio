import os
import shutil

import settings

logger = settings.get_fgLogger()

def move_audio(final_cuts, destination):
    for cut in final_cuts:
        path, filename = os.path.split(cut)
        final_destination = os.path.join(destination, filename)
        logger.info(f"Moving {cut} to {final_destination}")
        try:
            shutil.move(cut, final_destination)
            logger.info(f"{filename} move successful")
        except Exception as e:
            logger.critical(f"Something went wrong moving {filename}")




