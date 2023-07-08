import ffmpeg
import re
import subprocess
import sys

import settings

logger = settings.get_fgLogger()

silence_start_re = re.compile(r' silence_start: (?P<start>[0-9]+(\.?[0-9]*))$')
silence_end_re = re.compile(r' silence_end: (?P<end>[0-9]+(\.?[0-9]*)) ')
total_duration_re = re.compile(r'size[^ ]+ time=(?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9\.]{5}) bitrate=')

def _logged_popen(cmd_line, *args, **kwargs):
    logger.debug(f'Running command: {subprocess.list2cmdline(cmd_line)}')
    return subprocess.Popen(cmd_line, *args, **kwargs)

def get_chunks(in_file, silence_threshold, silence_duration, start_time=None, end_time=None):
    input_kwargs = {}
    if start_time is not None:
        input_kwargs['ss'] = start_time
    else:
        start_time = 0.
    if end_time is not None:
        input_kwargs['t'] = end_time - start_time

    p = _logged_popen(
        (ffmpeg
             .input(in_file, **input_kwargs)
             .filter("silencedetect", f"{silence_threshold}dB", silence_duration)
             .output('-', format='null')
             .compile()
         ) + ['-nostats'],
        stderr=subprocess.PIPE
    )
    output = p.communicate()[1].decode('utf-8')

    if p.returncode != 0:
        sys.exit(1)

    logger.debug(output)

    lines = output.splitlines()

    chunk_starts = []
    chunk_ends = []

    for line in lines:
        silence_start_match = silence_start_re.search(line)
        silence_end_match = silence_end_re.search(line)
        total_duration_match = total_duration_re.search(line)
        if silence_start_match:
            chunk_ends.append(float(silence_start_match.group('start')))
            if len(chunk_starts) == 0:
                chunk_starts.append(start_time or 0.)
        elif silence_end_match:
            chunk_starts.append(float(silence_end_match.group('end')))
        elif total_duration_match:
            hours = int(total_duration_match.group('hours'))
            minutes = int(total_duration_match.group('minutes'))
            seconds = float(total_duration_match.group('seconds'))
            end_time = hours * 3600 + minutes * 60 + seconds

    if len(chunk_starts) == 0:
        chunk_starts.append(start_time)

    if len(chunk_starts) > len(chunk_ends):
        chunk_ends.append(end_time or 10000000)

    return list(zip(chunk_starts, chunk_ends))


def split_audio(
        in_file,
        out_pattern,
        silence_threshold,
        silence_duration,
        start_time=None,
        end_time=None,
        verbose=False
    ):
    chunk_times = get_chunks(in_file, silence_threshold, silence_duration, start_time, end_time)

    for i, (start_time, end_time) in enumerate(chunk_times):
        time = end_time - start_time
        out_filename = out_pattern.format(i, i=i)

        _logged_popen(
            (ffmpeg
                .input(in_file, ss=start_time, t=time)
                .output(out_filename)
                .overwrite_output()
                .compile()
             ),
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
        ).communicate()
