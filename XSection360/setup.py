"""
Setup scene for XSection360 processing:
    - Set world background to black
    - Copy mesh objects in target collection to new collection
    - Set duplicate object material to solid white
    - Create camera in new collection
    - Disable/exclude all other objects/collections
    - Configure render settings
"""

import bpy


def create_flat_mat(name, colour):
    """
    Creates flat material (Emission - intensity 1.0)
    :param name: Name of new material
    :param colour: Emission input colour - (r,g,b,a)
    :return: Created material: bpy.types.Material
    """
    mat = bpy.data.materials.new(name)  # create material
    mat.use_nodes = True

    nodes = mat.node_tree.nodes

    # remove default shader
    old_node = nodes['Principled BSDF']
    nodes.remove(old_node)

    # create new shader
    emission = nodes.new(type='ShaderNodeEmission')

    # retrieve node sockets to be connected
    inp = nodes['Material Output'].inputs['Surface']
    out = emission.outputs['Emission']

    # connect nodes
    mat.node_tree.links.new(inp, out)
    # set emission input colour
    emission.inputs[0].default_value = colour

    return mat


def set_world_bg(colour):
    """
    Set the background colour of the current scene world.
    :param colour: World background colour
    """
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = colour
    # ADD?: handle case when world nodes already configured without "Background"


def exclude_all_collections(view_layer: bpy.types.ViewLayer):
    """
    Exclude (uncheck in outliner) all collections for given ViewLayer
    :param view_layer: bpy.types.ViewLayer from which to exclude collections
    """
    children = view_layer.layer_collection.children

    for layer_collection in children:
        layer_collection.exclude = True


def copy_mesh_to_new_collection(name, from_collection: bpy.types.Collection = None, set_mat=None):
    """
    Copy (all or some) mesh objects to new collection.
    :param name: Name of new collection
    :param from_collection: Collection from which to copy mesh objects; if None copies from entire scene
    :param set_mat: Material to set duplicate objects; if None not set
    :return: Created colletion: bpy.types.Collection
    """

    col = bpy.data.collections.new(name)  # create new collection
    bpy.context.scene.collection.children.link(col)  # link new collection to current scene master collection

    # specify objects to be copied
    if from_collection is None:
        objects = bpy.context.scene.objects[:]
    else:
        objects = from_collection.objects

    # copy each object
    for obj in objects:

        # skip if not mesh object
        if obj.type != 'MESH':
            continue

        # duplicate object
        copy = obj.copy()

        # add duplicate to new collection
        col.objects.link(copy)

        if set_mat is not None:
            # set copy material
            obj.data.materials.clear()
            obj.data.materials.append(set_mat)

    return col


def hide_all_without_collection():
    """
    Hide all objects missed by exclude_all_collections.
    """
    # Retrieve objects linked to master collection
    objects = bpy.context.scene.collection.objects

    for obj in objects:
        obj.hide_render = True
        obj.hide_viewport = True


def config_render_settings(scene: bpy.types.Scene):
    """
    Configure render settings
    """

    # Set colour management View Transform to 'Standard' (Important for linear rgb scale)
    scene.view_settings.view_transform = 'Standard'

    # Set filter size to 0 to remove anti-aliasing
    scene.render.filter_size = 0

    # turn off dithering
    scene.render.dither_intensity = 0

    # configure Eevee settings
    scene.eevee.taa_render_samples = 1
    scene.render.engine = 'BLENDER_EEVEE'


def create_camera(name: str, collection: bpy.types.Collection, ortho_scale=2):
    """
    Create camera for processing
    :param name: New camera name
    :param collection: New camera collection
    :param ortho_scale: New camera orthographic scale
    :return: Newly-created camera
    """
    # create and configure camera data
    cam = bpy.data.cameras.new(name)
    cam.type = 'ORTHO'
    cam.ortho_scale = ortho_scale

    # create object
    cam_obj = bpy.data.objects.new(name, cam)
    collection.objects.link(cam_obj)  # add object to collection

    # assign as active scene camera
    bpy.context.scene.camera = cam_obj

    return cam_obj


def configure_viewer_node():
    """
    DEPRECATED - script now run in background, Viewer Node not available
    Configure compositing nodes to allow access to Render Result (through Viewer node).
    From https://ammous88.wordpress.com/2015/01/16/blender-access-render-results-pixels-directly-from-python-2/
    """

    # switch on nodes
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = 185, 285

    # create output node
    v = tree.nodes.new('CompositorNodeViewer')
    v.location = 750, 210
    v.use_alpha = False

    # Links
    links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input

    # use bpy.data.images['Viewer Node'].pixels to access image after render
    # size is always width * height * 4 (rgba)

    # copy buffer to numpy array for faster manipulation
    # arr = np.array(pixels[:])


def apply_setup(target_collection):
    """
    Apply all above setup tasks.
    """
    set_world_bg((0, 0, 0, 1))
    config_render_settings(bpy.context.scene)

    # hide or exclude
    view_layer = bpy.context.view_layer
    exclude_all_collections(view_layer)
    hide_all_without_collection()

    mat = create_flat_mat('WHITE', (1, 1, 1, 1))
    workingCol = copy_mesh_to_new_collection('Output', target_collection, mat)

    cam = create_camera('Cam 360', workingCol)

    return cam
