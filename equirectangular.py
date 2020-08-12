import numpy as np
import math


class Equirectangular:
    # Class for equirectangular projection

    # CONVERSION
    # linear image coordinates 0 to 1
    # spherical coordinates -180 to 180
    # (centres 0 deg to 0.5 linear)
    @staticmethod
    def linear_to_spherical(linear):
        # convert linear to spherical coordinate axis

        # scale to between -1 and 1: *=2, -=1
        # scale to between -180 and 180: *- 180
        return (linear * 360) - 180

    @staticmethod
    def spherical_to_linear(spherical):
        # convert spherical to linear coordinate axis

        # inversion of linear_to_spherical
        return (spherical + 180) / 360

    @staticmethod
    def spherical_coord(linear_coord):
        x, y = linear_coord

        long = Equirectangular.linear_to_spherical(x)
        lat = Equirectangular.linear_to_spherical(y)

        return long, lat

    @staticmethod
    def linear_coord(spherical_coord):
        long, lat = spherical_coord

        x = Equirectangular.spherical_to_linear(long)
        y = Equirectangular.spherical_to_linear(lat)

        return x, y

    @staticmethod
    def project_sphere(coord, coord_linear=True, radius=1):
        # calculates the corresponding point on a unit sphere

        # ensure spherical coord
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

    @staticmethod
    def pixel_to_linear(pixel, resolution):
        # converts a pixel location axis to linear coordinate axis
        # takes into account pixel size, ensures no repeated seam
        # first pixel numbered 0

        block_size = 1 / resolution
        return block_size * (pixel + 0.5)

    @staticmethod
    def pixel_to_spherical(pixel, resolution):
        linear = Equirectangular.pixel_to_linear(pixel, resolution)
        return Equirectangular.linear_to_spherical(linear)

    @staticmethod
    def pixel_project_sphere(pixel_coord, resolution, radius):
        x, y = pixel_coord
        resX, resY = resolution

        x = Equirectangular.pixel_to_linear(x, resX)
        y = Equirectangular.pixel_to_linear(y, resY)

        return Equirectangular.project_sphere((x, y), radius=radius)


class Vector:

    @staticmethod
    def rotate(vector, axis, deg):
        # uses Rodrigues rotation formula to rotate vector deg degrees around axis
        # axis must be normalized

        v = np.array(vector)
        k = np.array(axis)

        rad = math.radians(deg)
        cos = math.cos(rad)
        sin = math.sin(rad)

        return (v * cos) + (np.cross(k, v) * sin) + (k * np.dot(k, v) * (1 - cos))


if __name__ == '__main__':

    # test axis conversion
    for i in np.arange(0, 1, 0.05):
        output = Equirectangular.linear_to_spherical(i)
        print(i, output)

#idea: addon for setup, background script for running
#run command line from within addon?
#preview camera angles