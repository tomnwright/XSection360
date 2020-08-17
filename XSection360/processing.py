import bpy


class ProcessRender:
    @staticmethod
    def get_rgba_lightness(rgba: tuple):
        """
        Calculate pixel lightness from RGB(A)
        :param rgba: Pixel data tuple: either RGB or RGBA
        :return: Lightness value (average of r,g,b)
        """
        return sum(rgba[:3]) / 3

    @staticmethod
    def get_pixels(image: bpy.types.Image):
        """
        Convert bpy.types.Image.pixels to list of pixel tuples
        Note: can also use xstools.iterate_flat
        :param image: Target image
        :return: Linear list of pixel tuples (RGBA)
        """
        return list(zip(*[iter(image.pixels)] * 4))

    @staticmethod
    def sum_lightness(pixels):
        """
        Calculate the sum lightness of given pixels
        :param pixels: List of RGB(A) pixel tuples
        :return: Float value: total (sum) lightness
        """
        result = 0

        for pixel in pixels:
            result += ProcessRender.get_rgba_lightness(pixel)

        return result

    @staticmethod
    def process(file_path):
        """
        Apply above processing to file at given filepath
        :param file_path: Target image filepath
        :return: Sum lightness of target image pixels
        """
        img = bpy.data.images.load(file_path)  # load target image into blender
        pixels = ProcessRender.get_pixels(img)  # get list of pixel tuples (rgba)

        return ProcessRender.sum_lightness(pixels)  # return sum of each pixel lightness


class ProcessRaw:
    def __init__(self, raw_data: list, save_file: str, resolution: tuple):
        """
        Class for processing raw data into output image
        Use this class as a generator
        :param raw_data: Average lightness of each rendered profile pixel
        :param save_file: Output file directory
        :param resolution: Resolution of output file
        """
        self.raw_data = raw_data
        self.save_file = save_file
        self.resolution = resolution

    def __iter__(self):
        return self.process()

    def __len__(self):
        return len(self.raw_data) + 1

    def process(self):
        """
        Performing processing
        Generator object: allows for progress bar
        """
        processed_pixels = []

        # create image
        image = bpy.data.images.new("XSection360 Result", *self.resolution)

        # calculate range
        min_raw = min(self.raw_data)
        max_raw = max(self.raw_data)

        # process pixels
        for raw in self.raw_data:
            scaled = self.range_to_bw(raw, min_raw, max_raw)
            new = [scaled, scaled, scaled, 1]
            print(new)
            processed_pixels += new
            yield None

        # write pixels
        image.pixels.foreach_set(processed_pixels)

        # save result
        image.filepath_raw = self.save_file
        image.file_format = 'PNG'
        image.save()

        yield None

    @staticmethod
    def range_to_bw(value, range_min, range_max) -> int:
        """
        Convert a value within the given range to BW (0 to 1)
        :param value: Target value, within range
        :param range_min: Range minimum
        :param range_max: Range maximum
        :return: Scaled BW int (between 0 and 1)
        """
        # scale value to 01 range
        scale01 = (value - range_min) / (range_max - range_min)

        return scale01
