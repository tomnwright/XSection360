# arguments to take:
#   -scene
#   -export file
#   -camera distance
#   -pixel start
# arguments infered through scene:
#   -resolution


class Process:

    # @staticmethod
    # def run_360(self, ):

    @staticmethod
    def get_rgba_value(rgba: tuple):
        return sum(rgba[:3]) / 3

    @staticmethod
    def sum_values(pixels):
        return sum(Process.get_rgba_value(p) for p in pixels)


def run_background(scene_name, save_file, cam_distance):
    import os
    import sys
    import bpy

    filepath = bpy.path.abspath("//")
    sys.path.append(filepath)
    os.chdir(filepath)

    import xstools
    from dataio import WriteRaw
    from equirectangular import Equirectangular
    from progress import bar

    scene: bpy.types.Scene = bpy.data.scenes[scene_name]
    camera = scene.camera
    resolution = xstools.OutImage.get_resolution(scene)

    writer = WriteRaw(save_file, resolution)

    max_pixel = writer.pixels
    for pixel in range(max_pixel):
        pixel_coord = writer.pixel_to_coord(pixel)

        long, lat = Equirectangular.pixel_coord_to_spherical(pixel_coord, resolution)

        xstools.transform_camera(camera, cam_distance, long, lat)

        bpy.ops.render.render()

        progress = pixel / (max_pixel - 1)
        #print(bar(10, progress))


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
        "-d", "--distance", dest="cam_distance", type=float, required=True,
        help="Camera sphere projection distance",
    )
    # parser.add_argument(
    #     "-p", "--pixel", dest="start_pixel", type=int,
    #     help="Camera sphere projection distance",
    # )
    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        return

    if not args.scene:
        print("Error: --scene=\"some string\" argument not given, aborting.")
        parser.print_help()
        return
    if not args.save_file:
        print("Error: --file=\"some string\" argument not given, aborting.")
        parser.print_help()
        return
    if not args.cam_distance:
        print("Error: --distance=value argument not given, aborting.")
        parser.print_help()
        return

    # Run the example function
    # example_function(args.text, args.save_path, args.render_path)
    run_background(args.scene, args.save_file, args.cam_distance)

    print("batch job finished, exiting")


if __name__ == '__main__':
    main()
