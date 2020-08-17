import os
from .xstools import OutImage

# DEPRECATED, NOT USING INTERMEDIARY RAW ANY MORE
# class RawProfile:
#     """
#     Drag profile IO base
#     """
#
#     def __init__(self, filename: str, resolution: tuple):
#         # validate filename ending
#         if not filename.endswith('.txt'):
#             filename += '.txt'
#         self.filename = filename
#
#         self.x, self.y = resolution
#
#     def pixel_to_coord(self, pixel):
#         """
#         Convert pixel number to pixel coordinate
#         :param pixel: Pixel number; start counting bottom left, go right
#         :return: Pixel coordinates: zeroed bottom left
#         """
#         return OutImage.pixel_to_coord(pixel, self.x)
#
#     def coord_to_pixel(self, coord):
#         """
#         Convert pixel coordinate to pixel number
#         :param coord: Pixel coordinates: zeroed bottom left
#         :return: Pixel number; start counting bottom left, go right
#         """
#         x, y = coord
#
#         return y * self.x + x
#
#     @property
#     def pixels(self):
#         return self.x * self.y
#
#
# class WriteRaw(RawProfile):
#     def __init__(self, filename: str, resolution: tuple, copy_from=None):
#         """
#         Writer for raw profile (later processed into image drag profile)
#         Writes one value on each line
#         Inherits from RawProfile
#         :param filename: target raw profile file path
#         :param resolution: profile resolution
#         :param copy_from: copy pixel data from existing raw profile
#         """
#         super().__init__(filename, resolution)
#
#         self.handle_existing()
#
#         with open(self.filename, 'w') as new_file:
#             # ensure that file is created immediately
#             pass
#
#         if copy_from is not None:
#             pass
#
#     def handle_existing(self):
#         """
#         Rename target file to ensure existing files are not overwritten
#         """
#         if not os.path.isfile(self.filename):
#             return
#
#         # does already exist
#         count = 1
#         while os.path.exists(self.insert_before_extension(self.filename, count)):
#             count += 1
#
#         self.filename = self.insert_before_extension(self.filename, count)
#
#     @staticmethod
#     def insert_before_extension(filename: str, insert):
#         """
#         Insert string into filename before extension
#         :param filename: target filename
#         :param insert: string to be inserted
#         """
#         extension_point = filename.rfind('.')  # find point position from right
#         return filename[:extension_point] + str(insert) + '.txt'
#
#     def copy_from(self, copy_file):
#         """
#         Copy pixel data from existing raw profile
#         Useful for renders not started/ended at pixel 0
#         (Currently not implemented in addon)
#         :param copy_file: File from which to copy pixel data
#         """
#         with open(copy_file, 'r') as read_file:
#             with open(self.filename, 'a') as write_file:
#                 write_file.writelines(read_file.readlines())
#
#     def write(self, value):
#         """
#         Write value to raw profile (with newline)
#         :param value: Value to be written
#         """
#         with open(self.filename, 'a') as write_file:
#             write_file.write(str(value) + "\n")
#
#
# class ReadRaw(RawProfile):
#     def __init__(self, filename: str, resolution: tuple):
#         """
#         Reader for raw profile (for processing into image drag profile)
#         Inherits from RawProfile
#         :param filename: target raw profile file path
#         :param resolution: profile resolution
#         """
#         super().__init__(filename, resolution)
#
#     def read_data(self):
#         """
#         Read all data from file
#         :return: List of float values, one from each line
#         """
#         result = []
#
#         print(self.filename)
#         with open(self.filename, "r") as read_file:
#             for line in read_file:
#                 result.append(float(line))
#
#         return result
