import sys
import os
import bpy
from bpy_extras.io_utils import ExportHelper
from subprocess import Popen, CREATE_NEW_CONSOLE

# set local path & allow local imports
# filepath = bpy.path.abspath("//")
# sys.path.append(filepath)
# sys.path.append(__file__)
# os.chdir(filepath)

from .setup import apply_setup
from .equirectangular import Equirectangular
from . import xstools


class XS360PanelSettings:
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_category = "Tools"
    bl_context = "render"
    # bl_options = {"DEFAULT_CLOSED"}


class XS360Panel(XS360PanelSettings, bpy.types.Panel):
    """
    Creates a XSection360 panel in the render context of the properties editor
    """
    bl_label = "XSection360"
    bl_idname = "RENDER_PT_xs360"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        # save file input
        col = layout.column(align=True)
        col.label(text="Output File:")
        row = col.row(align=True)
        row.operator("wm.xs360_select_file", icon="FILE_FOLDER", text="")
        row.prop(xs360, "output_file", text="")

        # profile resolution
        col = layout.column(align=True)
        col.label(text="Profile Resolution")
        row = col.row(align=True)
        row.prop(xs360, "output_x", text="X")
        row.prop(xs360, "output_y", text="Y")

        # run button
        row = layout.row()
        row.scale_y = 2.0
        row.operator("wm.run_xs360", text="Run")

        # open in new console bool
        layout.prop(xs360, "new_console")


class XS360SetupSub(XS360PanelSettings, bpy.types.Panel):
    """
    Contains scene Setup options for XSection360 panel
    """
    bl_label = "Setup"
    bl_parent_id = "RENDER_PT_xs360"
    bl_idname = "RENDER_PT_xs360_setup"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        # target collection
        layout.prop(xs360, "setup_collection")

        # setup button
        layout.operator("wm.setup_xs360")

        layout.label(text="Camera may need further setup.")


class XS360CameraSub(XS360PanelSettings, bpy.types.Panel):
    """
    Contains camera options for XSection360 panel
    """
    bl_label = "Camera"
    bl_parent_id = "RENDER_PT_xs360"
    bl_idname = "RENDER_PT_xs360_cam"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        xs360 = scene.xs360

        # target camera
        layout.prop(xs360, "camera_360")

        # only show following properties if target camera assigned
        if xs360.camera_360 is not None:
            # camera distance (sphere radius)
            layout.prop(xs360, "camera_distance")

            row = layout.row()

            # Debug camera positioning
            row.label(text='Debug')
            row.prop(xs360, "debug_camera", text='')  # do debug?
            row.prop(xs360, "pixel_debug", text='Pixel')  # pixel position to debug

    @staticmethod
    def do_camera_debug(self, context):
        """
        Apply camera pixel debug
        Preview camera positioning for given final profile pixel
        """
        if not self.debug_camera:
            return  # cancel if no camera debugging not enabled

        pixel = self.pixel_debug

        # get final output resolution
        rX, rY = XS360Properties.get_resolution(context.scene)
        total = rX * rY

        # validate pixel range
        small = pixel < 0
        big = pixel > total - 1
        if small or big:
            return

        # get pixel coordinate
        coord = xstools.OutImage.pixel_to_coord(pixel, rX)

        # get projected longitude and latitude
        long, lat = Equirectangular.Pixel.coord_to_spherical(coord, (rX, rY))

        # apply to debug
        camera = self.camera_360
        distance = self.camera_distance
        xstools.transform_camera(camera, distance, long, lat)


class XS360FileSelect(bpy.types.Operator, ExportHelper):
    """Select raw drag profile output for XSection360"""
    bl_idname = 'wm.xs360_select_file'
    bl_label = 'Accept'

    filename_ext = ".txt"

    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def invoke(self, context, event):
        self.filepath = context.scene.xs360.output_file
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        context.scene.xs360.output_file = self.filepath
        return {'FINISHED'}


class RunXS360(bpy.types.Operator):
    """
    Run XSection360 on current scene
    """
    bl_idname = 'wm.run_xs360'
    bl_label = 'Run'
    bl_description = ''

    def execute(self, context):
        blend_file = bpy.data.filepath  # get blend file path
        xs360 = context.scene.xs360

        # save blend file
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)

        # get usable variables
        scene = context.scene.name
        save_file = bpy.path.abspath(xs360.output_file)
        distance = xs360.camera_distance

        # set creation flags - open in new console?
        flags = 0
        if xs360.new_console:
            flags = CREATE_NEW_CONSOLE

        # get output profile resolution
        x, y = XS360Properties.get_resolution(context.scene)

        from . import background
        command = ['blender',  blend_file, '--background', '--python', background.__file__, '--',
                   f'--scene={scene}',
                   f'--file={save_file}', f'-x={x}', f'-y={y}', f'--distance={distance}']
        print(" ".join(command))

        # run background script
        Popen(command, creationflags=flags)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        Only enable if scene camera has been set
        """
        return context.scene.camera is not None


class SetupXS360(bpy.types.Operator):
    """
    Setup scene for XSection360 rendering:
        -Copy mesh objects in target collection to new collection
        -Create new camera
        -Configure render settings
        -etc...
    """
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


class XS360Properties(bpy.types.PropertyGroup):
    setup_collection: bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Target",
        description="Collection from which mesh is extracted on setup"
    )

    # camera
    camera_360: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Camera",
        description="Camera to apply pixel debug to"
    )
    camera_distance: bpy.props.FloatProperty(
        name='Camera Distance',
        description='Camera distance from origin (sphere radius)',
        default=20,
        min=0
    )

    # debug camera
    debug_camera: bpy.props.BoolProperty(
        name='Debug Camera',
        description="Debug camera positioning?",
    )
    pixel_debug: bpy.props.IntProperty(
        name='Pixel Camera Debug',
        description="Pixel position for which to debug camera positioning",
        min=0,
        update=XS360CameraSub.do_camera_debug
    )

    # output process
    output_file: bpy.props.StringProperty(
        default="//test.txt",
        description="File that output is written to."
    )
    new_console: bpy.props.BoolProperty(
        name="Run In New Console",
        default=True,
        description="Run background XSection360 process in new console (or in Blender console)"
    )
    output_x: bpy.props.IntProperty(
        name="X Resolution",
        description="X Resolution of Output Profile (not render)",
        default=30,
        min=0
    )
    output_y: bpy.props.IntProperty(
        name="Y Resolution",
        description="Y Resolution of Output Profile (not render)",
        default=30,
        min=0
    )

    # Note: render size for each profile pixel should be set in scene render settings

    @staticmethod
    def get_resolution(scene):
        x = scene.xs360.output_x
        y = scene.xs360.output_y
        return x, y


classes = (
    XS360Panel,
    XS360SetupSub,
    XS360CameraSub,
    XS360Properties,
    XS360FileSelect,
    RunXS360,
    SetupXS360,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.xs360 = bpy.props.PointerProperty(type=XS360Properties)
    return


def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.xs360

    for cls in reversed(classes):
        unregister_class(cls)
    return


if __name__ == '__main__':
    register()
