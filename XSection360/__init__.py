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
