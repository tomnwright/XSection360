'''
This script is opened in the blender file and registered (by running).
The UI then allows a render to be executed, which ports the data to a separate Python process using an intermediary file.
'''
# import sys
# import os
# import threading

import sys
import os
import bpy
from bpy_extras.io_utils import ExportHelper
from subprocess import Popen, CREATE_NEW_CONSOLE

filepath = bpy.path.abspath("//")
sys.path.append(filepath)
os.chdir(filepath)

from setup import apply_setup
from equirectangular import Equirectangular
import xstools

bl_info = {
    "name": "XSection360",
    "description": "Calls Renderia to render scene (requires active camera).",
    "author": "Tom Wright",
    "version": (1, 0),
    "blender": (2, 81, 0),
    "location": "Properties > Render > Renderia",
    "category": "Render"
}


class XS360_Panel_Settings:
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_category = "Tools"
    bl_context = "render"
    bl_options = {"DEFAULT_CLOSED"}


class XS360_Panel(XS360_Panel_Settings, bpy.types.Panel):
    """Creates a Panel in the render context of the properties editor"""
    bl_label = "XSection360"
    bl_idname = "RENDER_PT_xs360"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        # save file input
        layout.label(text="Output File:")

        col = layout.column()
        row = col.row(align=True)
        row.operator("wm.xs360_select_file", icon="FILE_FOLDER", text="")
        row.prop(xs360, "output_file", text="")

        # run button
        row = layout.row()
        row.scale_y = 2.0
        row.operator("wm.run_xs360", text="Run")


class XS360_Setup_Sub(XS360_Panel_Settings, bpy.types.Panel):
    """Contains settings for Renderia Panel"""
    bl_label = "Setup"
    bl_parent_id = "RENDER_PT_xs360"
    bl_idname = "RENDER_PT_xs360_setup"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        layout.prop(xs360, "setup_collection")

        layout.operator("wm.setup_xs360")

        layout.label(text="Camera may need further setup.")


class XS360_Camera_Sub(XS360_Panel_Settings, bpy.types.Panel):
    """Contains settings for Renderia Panel"""
    bl_label = "Camera"
    bl_parent_id = "RENDER_PT_xs360"
    bl_idname = "RENDER_PT_xs360_cam"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        layout.prop(xs360, "camera_360")

        if xs360.camera_360 is not None:
            layout.prop(xs360, "camera_distance")

            row = layout.row()

            row.label(text='Debug')
            row.prop(xs360, "debug_camera", text='')
            row.prop(xs360, "pixel_debug", text='Pixel')

    @staticmethod
    def do_camera_debug(self, context):
        if not self.debug_camera:
            return

        pixel = self.pixel_debug

        rX, rY = xstools.OutImage.get_resolution()
        total = rX * rY

        # validate pixel range
        small = pixel < 0
        big = pixel > total - 1
        if small or big:
            return

        # get pixel pixel_coord
        coord = xstools.OutImage.pixel_to_coord(pixel, rX)

        long, lat = Equirectangular.pixel_coord_to_spherical(coord, (rX, rY))

        print(long, lat)
        camera = self.camera_360
        distance = self.camera_distance
        xstools.transform_camera(camera, distance, long, lat)


class XS360_File_Select(bpy.types.Operator, ExportHelper):
    bl_idname = 'wm.xs360_select_file'
    bl_label = 'Accept'

    filename_ext = ".txt"

    filter_glob: bpy.props.StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def invoke(self, context, event):
        self.filepath = context.scene.xs360.output_file
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        filedir = self.filepath
        context.scene.xs360.output_file = self.filepath
        return {'FINISHED'}


class Run_XS360(bpy.types.Operator):
    bl_idname = 'wm.run_xs360'
    bl_label = 'Run'
    bl_description = ''

    def execute(self, context):
        blend_file = bpy.data.filepath

        bpy.ops.wm.save_as_mainfile(filepath=blend_file)

        scene = context.scene.name
        save_file = bpy.path.abspath(context.scene.xs360.output_file)
        distance = context.scene.xs360.camera_distance

        Popen(['blender', blend_file, '--background', '--python', 'background.py', '--', f'--scene={scene}', f'--file={save_file}', f'--distance={distance}'], creationflags = CREATE_NEW_CONSOLE)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None


class Setup_XS360(bpy.types.Operator):
    bl_idname = 'wm.setup_xs360'
    bl_label = 'Setup'
    bl_description = ''

    def execute(self, context):
        collection = context.scene.xs360.setup_collection

        new_cam = apply_setup(collection)
        context.scene.xs360.camera_360 = new_cam

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.scene.xs360.setup_collection is not None


class XS360_Properties(bpy.types.PropertyGroup):
    setup_collection: bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Target",
        description="Collection from which mesh is extracted"
    )

    # camera
    camera_360: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Camera",
        description="Collection from which mesh is extracted"
    )
    camera_distance: bpy.props.FloatProperty(
        name='Camera Distance',
        description='Camera distance from origin (sphere radius)',
        default=20,
        min=0
    )
    # debug
    debug_camera: bpy.props.BoolProperty(
        name='Debug Camera',
    )

    pixel_debug: bpy.props.IntProperty(
        name='Pixel Camera Debug',
        min=0,
        update=XS360_Camera_Sub.do_camera_debug
    )

    output_file: bpy.props.StringProperty(
        default="//test.txt",
        description="File that output is written to."
    )


classes = (
    XS360_Panel,
    XS360_Setup_Sub,
    XS360_Camera_Sub,
    XS360_Properties,
    XS360_File_Select,
    Run_XS360,
    Setup_XS360,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.xs360 = bpy.props.PointerProperty(type=XS360_Properties)
    return


def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.xs360

    for cls in reversed(classes):
        unregister_class(cls)
    return


if __name__ == '__main__':
    register()
