"""
XSection360 is a Blender addon for creating calculating relative cross-sectional
of a 3D object, from different angles. It uses equirectangular projection to
calculate and render camera positions for each pixel in an output image profile.

The addon was written to create drag profiles of plane objects, for flight simulation.

To Use:

1) Install addon
2) In the XSection360 Setup panel, set the target collection:
        a collection containing all the objects to be included
3) Click the Setup button - the scene will automatically be setup for XS360 processing
4) Use the camera debugger to make sure all objects are in frame from every angle.
        (Configure object position and camera ortho size)
        (The camera rotates about the World Origin)
5) Set an output png file; click Run
        ("Run in New Console" is recommended)
        Addon renders an image from each camera position,
        calculates the total lightness of the image pixels,
        and outputs it to output image profile
6) Wait for XSection360 Render & Process to complete
        DO NOT OPEN OUTPUT FILE DURING RENDER PROCESS
        as this will cause an access error, crashing the script
"""


bl_info = {
    "name": "XSection360",
    "description": "Create cross-sectional area image profile for calculating object drag from various angles.",
    "author": "Tom Wright",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Render > XSection360",
    "category": "Render"
}

from . import blender_gui


def register():
    blender_gui.register()


def unregister():
    blender_gui.unregister()
