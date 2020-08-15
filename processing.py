from dataio import ReadRaw
from PIL import Image
import os
import numpy as np

path = os.path.dirname(__file__)
os.chdir(path)


def scale_value_01(value, _min, _max):
    return (value - _min) / (_max - _min)


def scale_to_bw(value, _min, _max):
    scale01 = scale_value_01(value, _min, _max)

    return scale01 * 255


data_file = "output1.txt"
output_file = "OUTPUTg11.png"
resolution = (255, 255)

reader = ReadRaw(data_file, resolution)

data = reader.read_data()
_min, _max = min(data), max(data)
pixels = [scale_to_bw(i, _min, _max) for i in data]

img = Image.new('L', resolution, 255)

print(pixels)

img.putdata(pixels)

img.show()

img.save("output.png")
