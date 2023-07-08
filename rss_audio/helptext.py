
HELPTEXT = """
rss audio command line interface
"""

SETUP_TEXT = """
Before running this tool, you should first configure the ini file.

Below is an example of the config file:

``` config.ini
[directories]
feed =
download =
destination =
logdir =

[silence]
duration =
threshold =
output_pattern =

[email]
mailhost =
from_name =
recipients =
username =
password =
secure =
```

The [directories] and [silence] sections are required to use this tool.
You may also elect to send emails of the log data upon completion.
This is useful if you create a cron job or a scheduled task to run this tool.
When configuring the ini, please use absolute paths.
For example:
Good: `/home/user/Documents/logs`
Bad: `~/Documents/logs`

Below is a detailed explanation of each entry:

``` config.ini
[directories]
feed = URL to the audio rss feed. Example: https://beertodaybeertomorrow.podbean.com/rss

download = Download directory. This is also the working directory for the silence split tool. Example: /tmp

destination = This directory is where the audio files will go once the job is complete. Example: /automation_share/audio_import

logdir = A log file will be created when this tool runs. You can inspect the logfile if there are any issues. Here, you should define the directory where is should be stored. Example: /home/user/.logs


[silence]
duration = Silence, in seconds, to search for that will define the split. Default: 15

threshold = Silence threshold in db. Default: -60

output_pattern = Filename pattern for the output of the silence split.
This filename must have `{}` in order to define where the iterator will be. For example: OUTPUT{}.mp3.
If there is only one 15 second long silence detected, there will be two files.
The output files will be `OUTPUT1.mp3` and `OUTPUT2.mp3`.

You can do this however you like. Some other examples:

CAT{}.mp3 -> CAT1.mp3, CAT2.mp3
{}Segment.mp3 -> 1Segment.mp3, 2Segment.mp3
Date_{}_Segment.mp3 -> Date_1_Segment.mp3, Date_2_Segment.mp3

[email]
mailhost =
from_name =
recipients =
username =
password =
secure =
```

Once configured, you must pass the config file to the tool:
`python3 rss_audio.py -c /home/user/.config/myconfig.ini`
"""
