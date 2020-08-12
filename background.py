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
        "-s", "--scene", dest="text", type=str, required=True,
        help="This text will be used to render an image",
    )

    parser.add_argument(
        "-s", "--save", dest="save_path", metavar='FILE',
        help="Save the generated file to the specified path",
    )
    parser.add_argument(
        "-r", "--render", dest="render_path", metavar='FILE',
        help="Render an image to the specified path",
    )

    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        return

    if not args.text:
        print("Error: --text=\"some string\" argument not given, aborting.")
        parser.print_help()
        return

    # Run the example function
    #example_function(args.text, args.save_path, args.render_path)

    print("batch job finished, exiting")


if __name__ == '__main__':
    main()
