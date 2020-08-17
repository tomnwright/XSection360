from .equirectangular import Equirectangular
import bpy
from math import radians
from os.path import isfile


def transform_camera(camera: bpy.types.Object, distance, long, lat):
    """
    Set camera transformation
    Project position onto sphere of radius [distance] and align rotation
    :param camera: Camera to transform
    :param distance: Distance from centre point
    :param long: Longitudinal position
    :param lat: Latitudinal position
    """
    camera.location = Equirectangular.project_sphere((long, lat), False, distance)

    # rotate facing inwards, then apply lat & long
    rx, rz = 90 - lat, 180 + long
    camera.rotation_euler = (radians(rx), 0, radians(rz))


def create_pixel_sphere(radius, resolution):
    """
    Generate mesh with vertices for each projected pixel.
    Demonstrates position of each pixel.
    :param radius: Sphere radius
    :param resolution: Output image resolution
    """
    xR, yR = resolution

    # generate one vertex for each pixel
    verts = []
    for x in range(xR):
        for y in range(yR):
            v = Equirectangular.Pixel.project_sphere((x, y), resolution, radius)

            verts.append(v)

    name = f"Pixel Sphere ({xR}, {yR})"

    mesh = bpy.data.meshes.new(name)  # create mesh
    mesh.from_pydata(verts, [], [])
    obj = bpy.data.objects.new(name, mesh)  # create object; apply mesh

    bpy.context.scene.collection.objects.link(obj)  # place object in master collection
    bpy.context.view_layer.objects.active = obj  # make active object (?)
    obj.select_set(True)


def get_render_resolution(scene=None):
    if scene is None:
        scene = bpy.context.scene

    return scene.render.resolution_x, scene.render.resolution_y


def product(factors):
    result = 1
    for f in factors:
        result *= f
    return result


def iterate_flat(iterable, group_size):
    """
    Generator for iterating over [iterable] in groups of size [group_size]
    :param iterable: Target iterable
    :param group_size: Sub-group iteration size
    """
    if len(iterable) % group_size != 0:
        raise Exception("length of iterable must be divisible by four")

    for i in range(0, len(iterable), group_size):
        yield iterable[i: i + group_size]


class OutImage:
    @staticmethod
    def pixel_to_coord(pixel, res_width: int):
        """
        Convert pixel number to pixel coordinate
        :param pixel: Pixel number; start counting bottom left, go right
        :param res_width: x component of resolution
        :return: Pixel coordinates: zeroed bottom left
        """

        x = pixel % res_width
        y = pixel // res_width

        return x, y

    @staticmethod
    def coord_to_pixel(coord, res_width: int):
        """
        Convert pixel coordinate to pixel number
        :param coord: Pixel coordinates: zeroed bottom left
        :param res_width: x component of resolution
        :return: Pixel number; start counting bottom left, go right
        """
        x, y = coord

        return y * res_width + x

    @staticmethod
    def modify_filename(file_name):
        """
        Rename target file to ensure existing files are not overwritten
        """
        if not isfile(file_name):
            return file_name

        # does already exist
        count = 1
        while isfile(OutImage.insert_before_extension(file_name, count)):
            count += 1

        return OutImage.insert_before_extension(file_name, count)

    @staticmethod
    def insert_before_extension(filename: str, insert):
        """
        Insert string into filename before extension
        :param filename: target filename
        :param insert: string to be inserted
        """
        pos = filename.rfind('.')  # find extension dot position from right
        name, extension = filename[:pos], filename[pos:]
        return name + str(insert) + extension
