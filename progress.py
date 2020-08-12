import math
import sys

def bar(length, progress):
    dots = math.floor(progress * length)
    spaces = length - dots

    return '|' + dots * '*' + spaces * ' ' + '|'

def write_bar(length, process):
    sys.stdout.write('\r' + bar(length, process))
    sys.stdout.flush()

if __name__ == '__main__':
    import time

    for i in range(101):
        b = bar(30, i / 100)



        time.sleep(0.05)
