bl_info = {
    "name": "XSection360",
    "description": "Create cross-sectional area image profile for calculating object drag from various angles.",
    "author": "Tom Wright",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Render > XSection360",
    "category": "Render"
}

from . import xs360_addon


def register():
    xs360_addon.register()


def unregister():
    xs360_addon.unregister()
