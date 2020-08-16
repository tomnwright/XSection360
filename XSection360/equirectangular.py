import numpy as np
import math


class Equirectangular:
    """
    Class for equirectangular projection
    """

    class Longitude:
        @staticmethod
        def linear_to_spherical(linear):
            """
            Convert linear to spherical coordinate (horizontal)
            :param linear: Linear x coordinate
            :return: Projected longitude
            """

            # scale to between -1 and 1: *=2, -=1
            # scale to between -180 and 180: *= 180
            return (linear * 360) - 180

        @staticmethod
        def spherical_to_linear(spherical):
            """
            Convert spherical to linear coordinate (horizontal)
            :param spherical: Projected longitude
            :return: Linear x coordinate
            """

            # inversion of linear_to_spherical
            return (spherical + 180) / 360

    class Latitude:
        @staticmethod
        def linear_to_spherical(linear):
            """
            Convert linear to spherical coordinate (vertical)
            :param linear: Linear y coordinate
            :return: Projected latitude
            """

            # scale to between -1 and 1: *=2, -=1
            # scale to between -90 and 90: *= 90
            return (linear * 180) - 90

        @staticmethod
        def spherical_to_linear(spherical):
            """
            Convert spherical to linear coordinate (vertical)
            :param spherical: Projected latitude
            :return: Linear y coordinate
            """

            # inversion of linear_to_spherical
            return (spherical + 90) / 180

    @staticmethod
    def spherical_coord(linear_coord: tuple):
        """
        Converts linear (image) coordinate to projected spherical coordinate (tuple)
        :param linear_coord: Linear coordinate (x, y)
        :return: Projected spherical coordinate (long, lat)
        """
        x, y = linear_coord

        long = Equirectangular.Longitude.linear_to_spherical(x)
        lat = Equirectangular.Latitude.linear_to_spherical(y)

        return long, lat

    @staticmethod
    def linear_coord(spherical_coord: tuple):
        """
        Converts projected spherical coordinate to linear (image) coordinate (tuple)
        :param spherical_coord: Projected spherical coordinate (long, lat)
        :return: Linear coordinate (x, y)
        """
        long, lat = spherical_coord

        x = Equirectangular.Longitude.spherical_to_linear(long)
        y = Equirectangular.Longitude.spherical_to_linear(lat)

        return x, y

    @staticmethod
    def project_sphere(coord: tuple, coord_linear=True, radius=1):
        """
        Calculates the corresponding point on a sphere of radius [radius]
        :param coord: Coordinates to project
        :param coord_linear: Are coordinates linear (x, y) or spherical (long, lat)?
        :param radius: Sphere radius
        :return: Projected (equirectangular) point - (x, y, z) vector tuple
        """
        #

        # ensure spherical pixel_coord
        if coord_linear:
            coord = Equirectangular.spherical_coord(coord)
        long, lat = coord

        # unit vectors
        right = (1, 0, 0)
        forward = (0, 1, 0)
        up = (0, 0, 1)

        # set zero point
        result = forward

        # rotate lat then long
        result = Vector.rotate(result, right, lat)
        result = Vector.rotate(result, up, long)

        return tuple(result * radius)

    class Pixel:
        """
        Methods to deal directly with pixel input
        """

        @staticmethod
        def to_linear(pixel, resolution):
            """
            Converts a pixel location axis to linear coordinate axis
            Takes into account pixel size, ensures no repeated seam
            First pixel numbered 0
            :param pixel: pixel axis value (x or y)
            :param resolution: image resolution in same axis
            :return: Linear coordinate value
            """

            block_size = 1 / resolution
            return block_size * (pixel + 0.5)

        @staticmethod
        def coord_to_linear(pixel_coord: tuple, resolution: tuple):
            """
            Convert pixel coordinate to linear coordinate
            :param pixel_coord: Pixel coordinate
            :param resolution: Image resolution
            :return: Linear coordinate
            """
            x, y = pixel_coord
            rX, rY = resolution

            lX = Equirectangular.Pixel.to_linear(x, rX)
            lY = Equirectangular.Pixel.to_linear(y, rY)

            return lX, lY

        @staticmethod
        def coord_to_spherical(pixel_coord: tuple, resolution):
            """
            Convert pixel coordinate to projected spherical coordinate
            :param pixel_coord: Pixel coordinate (x, y)
            :param resolution: Image resolution
            :return: Projected spherical coordinate (long, lat)
            """
            x, y = Equirectangular.Pixel.coord_to_linear(pixel_coord, resolution)

            long = Equirectangular.Longitude.linear_to_spherical(x)
            lat = Equirectangular.Latitude.linear_to_spherical(y)

            return long, lat

        @staticmethod
        def project_sphere(pixel_coord: tuple, resolution: tuple, radius):
            """
            Calculates the corresponding point on a sphere of radius [radius]
            Handle pixel coordinates directly
            :param pixel_coord: Pixel coordinate
            :param resolution: Image resolution
            :param radius: Projection sphere radius
            :return: Projected (equirectangular) point - (x, y, z) vector tuple
            """
            # linear coordinates
            x, y = Equirectangular.Pixel.coord_to_linear(pixel_coord, resolution)

            return Equirectangular.project_sphere((x, y), radius=radius)


class Vector:

    @staticmethod
    def rotate(vector, axis, deg):
        """
        Rotate vector through [deg] degrees around [axis] vector
        Uses Rodrigues' vector rotation formula
        :param vector: Target vector
        :param axis: Normalized axis vector
        :param deg: Counter-clockwise rotation in degrees
        :return: Rotated vector -> np.array
        """

        v = np.array(vector)
        k = np.array(axis)

        rad = math.radians(deg)
        cos = math.cos(rad)
        sin = math.sin(rad)

        return (v * cos) + (np.cross(k, v) * sin) + (k * np.dot(k, v) * (1 - cos))
