from .equirectangular import Equirectangular
import bpy
from math import radians


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
    def get_resolution(scene=None):
        if scene is None:
            scene = bpy.context.scene

        return scene.render.resolution_x, scene.render.resolution_y
