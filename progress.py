from math import floor
from time import time, sleep
from math import fmod


class progress_bar:
    def __init__(self, iterable, length=10, desc=''):
        self.iterable = iterable
        self.max = len(iterable)
        self.bar_length = length
        self.desc = desc

    def __iter__(self):
        start_time = time()
        last_time = start_time

        for e, iter in enumerate(self.iterable):
            yield iter

            current_time = time()
            wait_time = current_time - last_time
            rate = 1 / wait_time

            progress = self.progress(e)
            prefix = self.prefix()
            bar = self.bar(self.bar_length, progress)

            remaining_seconds = self.time_remaining(progress, current_time - start_time)
            suffix = self.suffix(e, self.seconds_to_string(remaining_seconds), rate)

            print(prefix + bar + suffix, end='\r')
            last_time = current_time

    def progress(self, e):
        return (e + 1) / self.max

    def prefix(self):

        if len(self.desc) > 0:
            return self.desc + " "
        return ""

    def suffix(self, e, remaining, rate):
        return f' {e + 1}/{self.max} [{remaining} remaining, {round(rate, 2)} iter/s]'

    @staticmethod
    def bar(length, progress):
        dots = floor(progress * length)
        spaces = length - dots

        percent = int(progress * 100)

        return f'{percent}% |' + dots * '*' + spaces * ' ' + '|'

    @staticmethod
    def time_remaining(progress, elapsed):
        total = elapsed / progress
        return total - elapsed

    @staticmethod
    def seconds_to_string(seconds):

        days = int(floor(seconds / 86400))
        days_text = str(days) + 'd '
        if days < 1:
            days_text = ''
        remaining = fmod(seconds, 86400)

        hours = int(floor(remaining / 3600))
        hours_text = str(hours) + 'h '
        if hours < 1:
            hours_text = ''
        remaining = fmod(remaining, 3600)

        minutes = int(floor(remaining / 60))
        minutes_text = str(minutes) + 'min '
        if minutes < 1:
            minutes_text = ''
        remaining = fmod(remaining, 60)

        seconds = round(remaining, 2)

        return days_text + hours_text + minutes_text + str(seconds) + 's'
