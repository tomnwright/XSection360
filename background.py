"""
Blender background script in which XSection360 processing is performed
Outputs a temporary txt file containing raw drag profile data
(No. white pixels rendered for each profile pixel)

Called by "Run" in XS360 Blender Addon
Example usage:

blender example.blend --background --python background.py -- -s="Scene" -f=temp.txt -x=255 -y=255 -d=15
"""

import os
import sys
import bpy
from time import time, sleep


class Processing:
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
            result += Processing.get_rgba_lightness(pixel)

        return result

    @staticmethod
    def process_image(file_path):
        """
        Apply above processing to file at given filepath
        :param file_path: Target image filepath
        :return: Sum lightness of target image pixels
        """
        img = bpy.data.images.load(file_path)  # load target image into blender
        pixels = Processing.get_pixels(img)  # get list of pixel tuples (rgba)

        return Processing.sum_lightness(pixels)  # return sum of each pixel lightness


class Suppressor:
    """
    Suppress console output by redirecting it to logfile
    Specifically, prevent console output after each render operation
    Found at https://blender.stackexchange.com/a/44563
    """

    def __init__(self, logfile='blender_render.log'):
        """
        :param logfile: File to which console output is redirected
        """
        self.logfile = logfile
        self.old = None

    def enter(self):
        """
        Enable output redirection.
        """
        open(self.logfile, 'a').close()
        self.old = os.dup(1)
        sys.stdout.flush()
        os.close(1)
        os.open(self.logfile, os.O_WRONLY)

    def exit(self):
        """
        Disable output redirection.
        """
        os.close(1)
        os.dup(self.old)
        os.close(self.old)


def start_message(scene_name, save_file, resolution, render_res):
    """
    Generates console message displayed upon running process.
    :param scene_name: Name of target scene
    :param save_file: Output (drag profile) image file
    :param resolution: Output (drag profile) temp file (txt)
    :param render_res: Render resolution for each drag profile pixel
    :return: Full message (str)
    """
    message = f'\n~~~ Running XSection360 ~~~\n( Scene: {scene_name}, Output: {save_file}\n'
    message += f'Resolution: {resolution}, Render Res: {render_res}\n'
    return message


def run_background(scene_name, save_file, resolution: tuple, cam_distance):
    """
    Run XS360 process.
    :param scene_name: Name of target scene
    :param save_file: Output file (txt) - raw drag profile
    :param resolution: Final drag profile resolution
    :param cam_distance: Distance of camera from center (sphere radius)
    """

    # set local path & allow local imports
    # filepath = bpy.path.abspath("//")
    # sys.path.append(filepath)
    # os.chdir(filepath)

    from . import xstools
    from .dataio import WriteRaw
    from .equirectangular import Equirectangular
    from .progress import ProgressBar


    # retrieve scene data
    scene: bpy.types.Scene = bpy.data.scenes[scene_name]
    camera = scene.camera
    render_res = xstools.OutImage.get_resolution(scene)

    writer = WriteRaw(save_file, resolution)
    suppressor = Suppressor()

    # set temp file to render to
    temp_file = f"//temp.{time()}.png"
    scene.render.filepath = temp_file

    # print start message
    print(start_message(scene_name, writer.filename, resolution, render_res))
    max_pixel = writer.pixels

    # begin pixel render process (set up progress bar)
    for pixel in ProgressBar(range(max_pixel), desc="Rendering"):

        # get xy pixel coordinates
        pixel_coord = writer.pixel_to_coord(pixel)

        # get projected longitude & latitude
        long, lat = Equirectangular.Pixel.coord_to_spherical(pixel_coord, resolution)
        # apply to camera
        xstools.transform_camera(camera, cam_distance, long, lat)

        # render (suppress render console output)
        suppressor.enter()
        bpy.ops.render.render(write_still=True)
        suppressor.exit()

        # process render result, write to file
        total_lightness = Processing.process_image(temp_file)
        writer.write(total_lightness)

    # end


def main():
    import sys  # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
            "Run blender in background mode with this script:"
            "  blender [blend file] --background --python " + __file__ + " -- [options]"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    # Example utility, add some text and renders or saves it (with options)
    # Possible types are: string, int, long, choice, float and complex.
    parser.add_argument(
        "-s", "--scene", dest="scene", type=str, required=True,
        help="",
    )
    parser.add_argument(
        "-f", "--file", dest="save_file", metavar='FILE', required=True,
        help="Save the generated file to the specified path",
    )
    parser.add_argument(
        "-x", "--xres", dest="x_resolution", type=int, required=True,
        help="Horizontal (X) resolution of output image (different to render resolution)",
    )
    parser.add_argument(
        "-y", "--yres", dest="y_resolution", type=int, required=True,
        help="Vertical (Y) resolution of output image (different to render resolution)",
    )
    parser.add_argument(
        "-d", "--distance", dest="cam_distance", type=float, required=True,
        help="Camera sphere projection distance",
    )

    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        return

    res = (args.x_resolution, args.y_resolution)
    run_background(args.scene, args.save_file, res, args.cam_distance)

    print("Done, exiting...")
    sleep(1)


if __name__ == '__main__':
    main()
