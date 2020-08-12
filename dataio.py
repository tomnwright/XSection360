import os


class RawProfile:
    def __init__(self, filename: str, resolution: tuple):
        # validate filename ending
        if not filename.endswith('.txt'):
            filename += '.txt'
        self.filename = filename

        self.x, self.y = resolution

    def pixel_to_coord(self, pixel):
        """
        Convert pixel number to pixel coordinate
        :param pixel: Pixel number; start counting bottom left, go right
        :return: Pixel coordinates: zeroed bottom left
        """
        x = pixel % self.x
        y = pixel // self.x

        return x, y

    def coord_to_pixel(self, coord):
        """
        Convert pixel coordinate to pixel number
        :param coord: Pixel coordinates: zeroed bottom left
        :return: Pixel number; start counting bottom left, go right
        """
        x, y = coord

        return y * self.x + x

    @property
    def pixels(self):
        return self.x * self.y


class WriteRaw(RawProfile):
    def __init__(self, filename: str, resolution: tuple, copy_from=None):
        super().__init__(filename, resolution)

        self.handle_existing()

        with open(self.filename, 'w') as new_file:
            # ensure that file is created immediately
            pass

        if copy_from is not None:
            pass

    def handle_existing(self):
        if not os.path.isfile(self.filename):
            return

        # does already exist
        count = 1
        while os.path.exists(self.insert_before_ending(self.filename, count)):
            count += 1

        self.filename = self.insert_before_ending(self.filename, count)

    @staticmethod
    def insert_before_ending(filename: str, insert):
        return filename.replace('.txt', "") + str(insert) + '.txt'

    def copy_from(self, copy_file):
        with open(copy_file, 'r') as read_file:
            with open(self.filename, 'a') as write_file:
                write_file.writelines(read_file.readlines())

    def write(self, value):
        with open(self.filename, 'a') as write_file:
            write_file.write(value)
