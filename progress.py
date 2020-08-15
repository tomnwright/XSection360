from math import floor
from time import time, sleep
from math import fmod


class ProgressBar:

    def __init__(self, iterable, length=10, desc=''):
        """
        General progress bar for iterator
        Displays progress, eta, and iter rate
        :param iterable: Iterable to show progress for
        :param length: Length of bar (characters)
        :param desc: Description, displayed in prefix
        """
        self.iterable = iterable
        self.max = len(iterable)
        self.bar_length = length
        self.desc = desc

    def __iter__(self):

        # setup time
        start_time = time()
        last_time = start_time

        for e, iter in enumerate(self.iterable):
            yield iter

            # config time
            current_time = time()
            wait_time = current_time - last_time
            rate = 1 / wait_time

            # generate bar and prefix
            progress = self.progress(e)
            prefix = self.prefix()
            bar = self.bar(self.bar_length, progress)

            # generate suffix (incl. eta)
            remaining_seconds = self.time_remaining(progress, current_time - start_time)
            suffix = self.suffix(e, self.seconds_to_string(remaining_seconds), rate)

            # output to console
            print(prefix + bar + suffix, end='\r')
            last_time = current_time

    def progress(self, e):
        """
        Calculate current progress
        :param e: Iteration number
        :return: Progress (0 to 1)
        """
        return (e + 1) / self.max

    def prefix(self):
        """
        Generate bar prefix (description)
        :return: Progress bar prefix
        """
        if len(self.desc) > 0:
            return self.desc + " "

        return ""

    def suffix(self, e, remaining, rate):
        """
        Generate bar suffix (iter number, eta, iter rate)
        :param e: Iteration number
        :param remaining: Estimated time remaining
        :param rate: Iteration rate
        :return: Progress bar suffix
        """
        return f' {e + 1}/{self.max} [{remaining} remaining, {round(rate, 2)} iter/s]'

    @staticmethod
    def bar(length, progress):
        """
        Generate bar. Includes percentage
        :param length: Bar length (characters)
        :param progress: Progress (0 to 1)
        :return: Raw progress bar string
        """
        dots = floor(progress * length)
        spaces = length - dots

        percent = int(progress * 100)

        return f'{percent}% |' + dots * '*' + spaces * ' ' + '|'

    @staticmethod
    def time_remaining(progress, elapsed):
        """
        Calculate estimated time remaining
        :param progress: Iteration progress (0 to 1)
        :param elapsed: Time elapsed since iteration start
        :return: Estimated time for remaining iterations
        """
        total = elapsed / progress
        return total - elapsed

    @staticmethod
    def seconds_to_string(seconds):
        """
        Generate usable time string.
        Format: d h m s
        Hidden if 0 AND left-most value (can_hide)
        :param seconds: Raw seconds value
        :return: Time string (dhms)
        """
        # make sure in-between values are not hidden
        can_hide = True

        # days
        days = int(floor(seconds / 86400))
        days_text = str(days) + 'd '
        if days < 1:
            days_text = ''
        else:
            can_hide = False
        remaining = fmod(seconds, 86400)

        # hours
        hours = int(floor(remaining / 3600))
        hours_text = str(hours) + 'h '
        if hours < 1 and can_hide:
            hours_text = ''
        else:
            can_hide = True
        remaining = fmod(remaining, 3600)

        # minutes
        minutes = int(floor(remaining / 60))
        minutes_text = str(minutes) + 'min '
        if minutes < 1 and can_hide:
            minutes_text = ''
        remaining = fmod(remaining, 60)

        # seconds
        seconds = round(remaining, 2)

        return days_text + hours_text + minutes_text + str(seconds) + 's'


if __name__ == '__main__':
    for i in ProgressBar(range(100)):
        sleep(0.2)
