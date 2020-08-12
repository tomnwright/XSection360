from equirectangular import Equirectangular
import bpy
from math import radians

class Process:
    @staticmethod
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

    @staticmethod
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
                v = Equirectangular.pixel_project_sphere((x, y), resolution, radius)

                verts.append(v)

        name = f"Pixel Sphere ({xR}, {yR})"

        mesh = bpy.data.meshes.new(name)  # create mesh
        mesh.from_pydata(verts, [], [])
        obj = bpy.data.objects.new(name, mesh)  # create object; apply mesh

        bpy.context.scene.collection.objects.link(obj)  # place object in master collection
        bpy.context.view_layer.objects.active = obj  # make active object (?)
        obj.select_set(True)

    # @staticmethod
    # def run_360(self, ):

    @staticmethod
    def get_rgba_value(rgba:tuple):
        return sum(rgba[:3]) / 3

    @staticmethod
    def sum_values(pixels):
        return sum(Process.get_rgba_value(p) for p in pixels)

def

def main():
    import sys
    import argparse





if __name__ == '__main__':
    main()