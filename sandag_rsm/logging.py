import logging
import sys


class ElapsedTimeFormatter(logging.Formatter):
    def format(self, record):
        duration_milliseconds = record.relativeCreated
        hours, rem = divmod(duration_milliseconds / 1000, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours:
            record.elapsedTime = "{:0>2}:{:0>2}:{:05.2f}".format(
                int(hours), int(minutes), seconds
            )
        else:
            record.elapsedTime = "{:0>2}:{:05.2f}".format(int(minutes), seconds)
        return super(ElapsedTimeFormatter, self).format(record)


def logging_start(level=None):
    formatter = ElapsedTimeFormatter(
        fmt="[{elapsedTime}] {levelname:s}: {message:s}",
        style="{",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    if level is not None:
        logging.getLogger().setLevel(level)
