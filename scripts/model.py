import bpy
import os
import sys
import requests
import json
from os import path
from pathlib import Path
import math
import builtins as __builtin__

################################################################################
# Constant variables.
################################################################################
# Metadata directory to where all metadata files generated.
METADATA_DIR = "./build/json/"

# Output directory to where all metadata files generated.
IMAGE_OUTPUTS_DIR = "./build/image/"
VIDEO_OUTPUTS_DIR = "./build/video/"
GLB_OUTPUTS_DIR = "./build/glb/"
VRM_OUTPUTS_DIR = "./build/vrm/"
BACKGROUND_DIR = "./background/"

# Define trait type list.
TRAIT_TYPE_LIST = ["background", "face", "body", "body_top",
                   "body_bottom", "hair", "top", "side", "middle", "bottom"]


def get_name():
    """Get the name for the currently active object"""
    return bpy.context.active_object.name


def degToRadian(angle):
    """Convert angle from degrees to radians"""
    return angle*(math.pi/180)


def move_obj(name, coords):
    """Set object location to the specified coordinates"""
    bpy.data.objects[name].location = coords


def rotate_obj(name, angles):
    """Set object rotation to the specified angles"""
    rotation = [degToRadian(angle) for angle in angles]
    bpy.data.objects[name].rotation_euler = rotation


def scale_obj(name, scale):
    """Set object scale"""
    bpy.data.objects[name].scale = scale


def clear_collection(collection):
    """Remove everything from the specified collection"""
    for obj in collection.objects:
        bpy.data.objects.remove(obj)


def add_keyframe_sequence(obj, attribute, values, frames):
    """Add a sequence of keyframes for an object"""
    for v, f in zip(values, frames):
        setattr(obj, attribute, v)
        obj.keyframe_insert(data_path=attribute, frame=f)


def initialize():
    # Remove all objects and collections.
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)


def set_render_config():
    ############################################################################
    # Set render config.
    ############################################################################
    r = bpy.context.scene.render
    r.engine = "BLENDER_EEVEE"
    # r.engine = "CYCLES"
    r.resolution_x = 512
    r.resolution_y = 512

    ############################################################################
    # File format.
    ############################################################################
    r.image_settings.file_format = 'PNG'

    ############################################################################
    # Bloom (optional).
    ############################################################################
    bpy.context.scene.eevee.use_bloom = True
    # bpy.context.scene.eevee.bloom_threshold = 3.0
    # bpy.context.scene.eevee.bloom_knee = 0.5
    # bpy.context.scene.eevee.bloom_radius = 2.0
    # bpy.context.scene.eevee.bloom_intensity = 0.1
    # bpy.context.scene.eevee.bloom_color = (1.0, 1.0, 1.0)
    # bpy.context.scene.eevee.bloom_clamp = 0.0


def append_all_objects(file_path):
    with bpy.data.libraries.load(file_path) as (data_from, data_to):
        files = []

        # Add all objects in blender file.
        for obj in data_from.objects:
            files.append({'name': obj})
        # print("files: ", files)

        # Add all materials in blender file.
        data_to.materials = data_from.materials

        bpy.ops.wm.append(directory=file_path + "/Object/", files=files)


def append_asset_misc(parts_dir):
    path = parts_dir + "misc/" + "misc.blend/Collection/"
    object_name = "misc"
    bpy.ops.wm.append(filename=object_name, directory=path)

    # Link camera to scene
    cam = bpy.data.objects["camera"]
    scene = bpy.context.scene
    scene.camera = cam


def add_camera_location(camera, location, frame):
    camera.location = location
    camera.keyframe_insert(data_path="location", frame=frame)


def make_hdri_world_node(hdri_image):
    # Get the environment node tree of the current scene.
    tree_nodes = bpy.context.scene.world.node_tree.nodes

    # Clear all nodes.
    tree_nodes.clear()

    # Add Background node.
    node_background = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node.
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')

    # Load and assign the image to the node property.
    node_environment.image = hdri_image
    node_environment.location = -300, 0

    # Add Output node.
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')
    node_output.location = 200, 0

    # Link all nodes.
    # node_environment(Color) -> (Color)node_background(Background)
    # (Color)node_background(Background) -> (Surface)node_output
    links = bpy.context.scene.world.node_tree.links
    links.new(node_environment.outputs["Color"],
              node_background.inputs["Color"])
    links.new(node_background.outputs["Background"],
              node_output.inputs["Surface"])


def make_background_composition(download_image):
    bpy.context.area.ui_type = 'CompositorNodeTree'

    bpy.context.scene.use_nodes = True
    node_tree = bpy.context.scene.node_tree

    for every_node in node_tree.nodes:
        node_tree.nodes.remove(every_node)

    render_node = node_tree.nodes.new('CompositorNodeRLayers')
    render_node.location = -300, 300

    comp_node = node_tree.nodes.new('CompositorNodeComposite')
    comp_node.location = 400, 300

    alpha_node = node_tree.nodes.new(type="CompositorNodeAlphaOver")
    alpha_node.location = 150, 450

    scale_node = node_tree.nodes.new(type="CompositorNodeScale")
    bpy.data.scenes["Scene"].node_tree.nodes["Scale"].space = 'RENDER_SIZE'
    scale_node.location = -150, 500

    image_node = node_tree.nodes.new(type="CompositorNodeImage")
    image_node.image = download_image
    image_node.location = -550, 500

    # image_node -> scale_node -> alpha_node -> comp_node
    #              render_node -> alpha_node -> comp_node
    links = node_tree.links
    links.new(render_node.outputs[0], alpha_node.inputs[2])
    links.new(alpha_node.outputs[0], comp_node.inputs[0])
    links.new(scale_node.outputs[0], alpha_node.inputs[1])
    links.new(image_node.outputs[0], scale_node.inputs[0])

    # https://docs.blender.org/api/current/bpy.types.Area.html
    bpy.context.area.ui_type = 'VIEW_3D'


def render_video(id):
    START_FRAME = 1
    END_FRAME = 180

    # Set the animation start/end/current frames.
    scene = bpy.context.scene
    scene.frame_start = START_FRAME
    scene.frame_end = END_FRAME
    scene.frame_current = START_FRAME

    # Make facial acts.
    for object in bpy.data.objects:
        if "face" == object.name:
            shape_keys = object.data.shape_keys.key_blocks

            current_frame = bpy.context.scene.frame_current
            print("current_frame: ", current_frame)

            # Change shape key value and insert key frame.
            shape_keys["eyeBlinkLeft"].keyframe_insert(
                data_path="value", frame=1)
            shape_keys["eyeBlinkRight"].keyframe_insert(
                data_path="value", frame=1)
            shape_keys["mouthSmileLeft"].keyframe_insert(
                data_path="value", frame=120)
            shape_keys["mouthSmileRight"].keyframe_insert(
                data_path="value", frame=120)

            shape_keys["eyeBlinkLeft"].value = 1.0
            shape_keys["eyeBlinkRight"].value = 1.0
            shape_keys["eyeBlinkLeft"].keyframe_insert(
                data_path="value", frame=40)
            shape_keys["eyeBlinkRight"].keyframe_insert(
                data_path="value", frame=40)

            shape_keys["mouthSmileLeft"].value = 1.0
            shape_keys["mouthSmileRight"].value = 1.0
            shape_keys["mouthSmileLeft"].keyframe_insert(
                data_path="value", frame=160)
            shape_keys["mouthSmileRight"].keyframe_insert(
                data_path="value", frame=160)
            # Make camera track object.
            scene.camera.constraints.new(type='TRACK_TO').target = object

    # Camera initial transform.
    # https://docs.blender.org/api/current/bpy.types.Camera.html
    #
    # - location x: 0m, y: -20m, z: 0m
    # 1. x: 10m, y: 0m, z: 10m
    # 2. x: 0m, y: 10m, z: 0m
    # 3. x: -10m, y: 0m, z: 5m
    # 4. x: 0m, y: -20m, z: 0m

    # Set camera translation
    add_camera_location(scene.camera, (0, -20, 0), 1)
    add_camera_location(scene.camera, (30, 0, 20), 40)
    add_camera_location(scene.camera, (0, 30, 0), 80)
    add_camera_location(scene.camera, (-20, 0, 5), 120)
    add_camera_location(scene.camera, (0, -20, 0), 160)

    # Get image from ipsum image site.
    # try:
    #     r = requests.get("https://picsum.photos/1024")
    #     if r.status_code == 200:
    #         with open(BACKGROUND_DIR + "back.jpg", 'wb') as f:
    #             for chunk in r:
    #                 f.write(chunk)
    # except requests.ConnectionError:
    #     print("Failed to download image from ipsum site.")

    # Set camera backgroun with that image.
    # download_image = bpy.data.images.load(BACKGROUND_DIR + "back.jpg")
    # scene.camera.data.show_background_images = True
    # background_image = scene.camera.data.background_images.new()
    # background_image.image = download_image
    # bpy.context.scene.render.film_transparent = True

    # make_background_composition(download_image)

    # https://styly.cc/tips/nimi-blender-hdri/
    # hdri_image = bpy.data.images.load(BACKGROUND_DIR + "pool_4k.exr")
    hdri_image = bpy.data.images.load(
        BACKGROUND_DIR + "christmas_photo_studio_04_4k.exr")
    make_hdri_world_node(hdri_image)
    bpy.context.scene.render.film_transparent = False

    # Set render config of file format.
    # https://docs.blender.org/api/current/bpy.types.FFmpegSettings.html#bpy.types.FFmpegSettingsv
    # bpy.context.scene.render.fps = 20
    # bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    # bpy.context.scene.render.ffmpeg.format = "MPEG4"
    # bpy.context.scene.render.use_file_extension = False
    # bpy.context.scene.render.filepath = VIDEO_OUTPUTS_DIR + id + ".mp4"

    ###################################################################
    # Write video file.
    ###################################################################
    # bpy.ops.render.render(animation=True)
    ###################################################################


def render_image(id):
    ###################################################################
    # Render image.
    ###################################################################
    print("generate png file.")
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.use_file_extension = False
    bpy.context.scene.render.filepath = IMAGE_OUTPUTS_DIR + id + ".png"

    bpy.ops.render.render(write_still=True)
    ###################################################################


def render_glb(id):
    ###################################################################
    # Save gltf.
    ###################################################################
    # https://docs.blender.org/api/current/bpy.ops.export_scene.html
    # TODO : Set compresssion.
    print("generate glb file.")
    bpy.ops.export_scene.gltf(filepath=GLB_OUTPUTS_DIR + id + ".glb",
                              check_existing=True,
                              export_format='GLB',
                              ui_tab='GENERAL',
                              export_copyright='',
                              export_image_format='AUTO',
                              export_texture_dir='',
                              export_keep_originals=False,
                              export_texcoords=True,
                              export_normals=True,
                              export_draco_mesh_compression_enable=False,
                              export_draco_mesh_compression_level=6,
                              export_draco_position_quantization=14,
                              export_draco_normal_quantization=10,
                              export_draco_texcoord_quantization=12,
                              export_draco_color_quantization=10,
                              export_draco_generic_quantization=12,
                              export_tangents=False,
                              export_materials='EXPORT',
                              export_colors=True,
                              use_mesh_edges=False,
                              use_mesh_vertices=False,
                              export_cameras=False,
                              use_selection=False,
                              use_visible=False,
                              use_renderable=False,
                              use_active_collection=False,
                              export_extras=False,
                              export_yup=True,
                              export_apply=False,
                              export_animations=True,
                              export_frame_range=True,
                              export_frame_step=1,
                              export_force_sampling=True,
                              export_nla_strips=True,
                              export_def_bones=False,
                              #   optimize_animation_size=True,
                              export_current_frame=False,
                              export_skins=True,
                              export_all_influences=True,
                              export_morph=True,
                              export_morph_normal=True,
                              export_morph_tangent=False,
                              export_lights=False,
                              #   export_displacement=False,
                              will_save_settings=False,
                              filter_glob="*.glb;*.gltf"
                              )
    ###################################################################


def render_vrm(id):
    ###################################################################
    # Save vrm.
    ###################################################################
    print("generate vrm file.")
    bpy.ops.export_scene.vrm(
        filepath=VRM_OUTPUTS_DIR + id + ".vrm",
        filter_glob="*.vrm",
        export_invisibles=True,
        export_only_selections=False,
        export_fb_ngon_encoding=False,
    )
    ###################################################################


def remove_assets():
    print("bpy.data: ", bpy.data)
    for collection in bpy.data.collections:
        if collection.name != "misc":
            for obj in [o for o in collection.objects if o.type == "MESH"]:
                print("remove obj: ", obj)
                bpy.data.objects.remove(obj)
        bpy.data.collections.remove(collection)

    # https://blender.stackexchange.com/questions/75310/blender-consuming-all-memory
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        bpy.data.textures.remove(block)

    for block in bpy.data.images:
        bpy.data.images.remove(block)

    for block in bpy.data.armatures:
        bpy.data.armatures.remove(block)

    for block in bpy.data.objects:
        bpy.data.objects.remove(block)

    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)

    for block in bpy.data.cache_files:
        bpy.data.cache_files.remove(block)

    for block in bpy.data.lights:
        bpy.data.lights.remove(block)

    for block in bpy.data.node_groups:
        bpy.data.node_groups.remove(block)

    for block in bpy.data.shape_keys:
        bpy.data.shape_keys.remove(block)

    for block in bpy.data.texts:
        bpy.data.texts.remove(block)

    for block in bpy.data.textures:
        bpy.data.textures.remove(block)

    for block in bpy.data.worlds:
        bpy.data.worlds.remove(block)

    for block in bpy.data.libraries:
        bpy.data.libraries.remove(block)

    for block in bpy.data.brushes:
        bpy.data.brushes.remove(block)

    for block in bpy.data.actions:
        bpy.data.actions.remove(block)

################################################################################
# Set parent of accessories with head bone.
################################################################################


def add_accessory_objects():
    bodyArmatureObject = bpy.context.scene.objects.get("Armature")
    print("bodyArmatureObject: ", bodyArmatureObject)
    topObject = bpy.context.scene.objects.get("top")
    sideObject = bpy.context.scene.objects.get("side")
    middleObject = bpy.context.scene.objects.get("middle")
    bottomObject = bpy.context.scene.objects.get("bottom")
    # print("topObject: ", topObject)

    # https://blender.stackexchange.com/questions/77465/python-how-to-parent-an-object-to-a-bone-without-transformation

    # Select body armature in object mode.
    bpy.ops.object.mode_set(mode="OBJECT")
    bodyArmatureObject.select_set(True)
    bpy.context.view_layer.objects.active = bodyArmatureObject

    # Select head bone in edit mode.
    bpy.ops.object.mode_set(mode="EDIT")
    bodyArmatureObject.data.edit_bones.active = bodyArmatureObject.data.edit_bones[
        "J_Bip_C_Head"]

    # Select top mesh object and body armature in object mode.
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    if topObject:
        topObject.select_set(True)
    if sideObject:
        sideObject.select_set(True)
    if middleObject:
        middleObject.select_set(True)
    if bottomObject:
        bottomObject.select_set(True)
    bodyArmatureObject.select_set(True)
    bpy.context.view_layer.objects.active = bodyArmatureObject

    # Set body armature as parent of top mesh object.
    bpy.ops.object.parent_set(type="BONE", keep_transform=True)


def change_bone_angle(bone_name, axis, angle):
    # Set armature object as active.
    bpy.ops.object.mode_set(mode="OBJECT")
    armature_object = bpy.data.objects["Armature"]
    bpy.context.view_layer.objects.active = armature_object

    # Rotate selected_bone as axis and angle.
    bpy.ops.object.mode_set(mode="POSE")
    selected_bone = armature_object.pose.bones[bone_name]
    selected_bone.rotation_mode = "XYZ"
    selected_bone.rotation_euler.rotate_axis(axis, math.radians(angle))

    bpy.ops.object.mode_set(mode="OBJECT")
    selected_bone.keyframe_insert(data_path="rotation_euler", frame=1)


def generate(id, adict, parts_dir):
    # * ########################################################################
    # * Add blender file objects as to trait_type and value.
    # * ########################################################################

    for attr in adict["attributes"]:
        # Get trait_type and value.
        trait_type = attr["trait_type"].replace(" ", "_").lower()
        value = attr["value"].replace(" ", "_").lower()

        # Check trait_type and value error.
        if trait_type not in TRAIT_TYPE_LIST:
            continue
        if attr["value"] == "" or attr["value"] == "none":
            continue

            # Get file path as to trait_type and value.
        file_path = f"{parts_dir}/{trait_type}/{trait_type}_{value}.blend"

        # Append blender file objects.
        append_all_objects(file_path)

    # * ########################################################################
    # * Append misc file which includes camera and light.
    # * ########################################################################
    append_asset_misc(parts_dir)

    # * ########################################################################
    # * Get each bpy object.
    # * ########################################################################
    # For hair object and armature.
    hairObject = bpy.context.scene.objects.get("Hair")
    hairArmatureObject = bpy.context.scene.objects.get("HairArmature")
    print("hairObject: ", hairObject)
    print("hairArmatureObject: ", hairArmatureObject)

    # For body_top object and armature.
    bodyTopObject = bpy.context.scene.objects.get("BodyTop")
    bodyTopArmatureObject = bpy.context.scene.objects.get("BodyTopArmature")
    print("bodyTopObject: ", bodyTopObject)
    print("bodyTopArmatureObject: ", bodyTopArmatureObject)

    # For body_bottom object and armature.
    bodyBottomObject = bpy.context.scene.objects.get("BodyBottom")
    bodyBottomArmatureObject = bpy.context.scene.objects.get(
        "BodyBottomArmature")
    print("bodyBottomObject: ", bodyBottomObject)
    print("bodyBottomArmatureObject: ", bodyBottomArmatureObject)

    # For face object.
    faceObject = bpy.context.scene.objects.get("Face")
    print("faceObject: ", faceObject)

    # For body object and armature.
    bodyObject = bpy.context.scene.objects.get("Body")
    bodyArmatureObject = bpy.context.scene.objects.get("Armature")
    bodyArmature = bpy.data.armatures["Armature"]
    print("bodyArmatureObject: ", bodyArmatureObject)
    print("bodyArmature: ", bodyArmature)

    # For accessory object.
    topObject = bpy.context.scene.objects.get("top")
    middleObject = bpy.context.scene.objects.get("middle")
    sideObject = bpy.context.scene.objects.get("side")
    bottomObject = bpy.context.scene.objects.get("bottom")
    hairBoneGroupArray = []
    # print("topObject: ", topObject)
    # print("middleObject: ", middleObject)
    # print("sideObject: ", sideObject)
    # print("bottomObject: ", bottomObject)

    # * ########################################################################
    # * Use body vrm0 extension data.
    # * ########################################################################
    vrm0 = bodyArmatureObject.data.vrm_addon_extension.vrm0
    humanoid = vrm0.humanoid
    # for human_bone in vrm0.humanoid.human_bones:
    #     print("bone: ", human_bone.bone)
    #     print("node.value: ", human_bone.node.value)
    #     print("node.armature_data_name: ", human_bone.node.armature_data_name)
    # print("humanoid.all_required_bones_are_assigned(): ",
    #       humanoid.all_required_bones_are_assigned())

    # * ########################################################################
    # * Error check.
    # * ########################################################################
    if humanoid.all_required_bones_are_assigned() == False:
        raise ValueError(
            "humanoid.all_required_bones_are_assigned() is False.")
    if faceObject == None:
        raise ValueError("faceObject is None.")
    if hairObject == None:
        raise ValueError("hairObject is None.")
    if hairArmatureObject == None:
        raise ValueError("hairArmatureObject is None.")
    if hairArmatureObject.data == None:
        raise ValueError("hairArmatureObject.data is None.")
    if bodyArmature == None:
        raise ValueError("bodyArmature is None.")
    if bodyArmatureObject == None:
        raise ValueError("bodyArmatureObject is None.")
    if bodyArmatureObject.type != "ARMATURE":
        raise ValueError("bodyArmatureObject.type is not ARMATURE.")

    secondary_animation = (
        hairArmatureObject.data.vrm_addon_extension.vrm0.secondary_animation
    )
    for bone_group in secondary_animation.bone_groups:
        hairBoneGroupArray.append(bone_group)

    # * ########################################################################
    # * Set parent of face with body armature.
    # * ########################################################################

    # Deselect all.
    bpy.ops.object.select_all(action="DESELECT")
    # Select face object.
    faceObject.select_set(True)
    # Set body armature object active.
    bpy.context.view_layer.objects.active = bodyArmatureObject
    # Set parent of face object to body armature.
    bpy.ops.object.parent_set(
        type="OBJECT", keep_transform=True)

    # * ########################################################################
    # * Add hair armature.
    # * ########################################################################

    hairColliderGroupArray = []
    armature = bpy.data.objects.get("Armature")
    if armature != None and armature.type == "ARMATURE":
        collider_groups = (
            armature.data.vrm_addon_extension.vrm0.secondary_animation.collider_groups
        )
        for collider_group in collider_groups:
            # print("collider_group.name: ", collider_group.name)
            if collider_group.name.startswith("J_Bip_C_Head") == True or \
                    collider_group.name.startswith("J_Bip_L_UpperArm") == True or \
                    collider_group.name.startswith("J_Bip_R_UpperArm") == True or \
                    collider_group.name.startswith("J_Bip_L_LowerArm") == True or \
                    collider_group.name.startswith("J_Bip_R_LowerArm") == True or \
                    collider_group.name.startswith("J_Bip_L_Hand") == True or \
                    collider_group.name.startswith("J_Bip_R_Hand") == True or \
                    collider_group.name.startswith("J_Bip_C_UpperChest") == True or \
                    collider_group.name.startswith("J_Bip_C_Spine") == True or \
                    collider_group.name.startswith("J_Bip_C_Neck") == True:
                hairColliderGroupArray.append(collider_group)

    # * ########################################################################
    # * Join body top armature to body armature.
    # * ########################################################################

    bpy.ops.object.select_all(action="DESELECT")
    selectedObjects = [bodyArmatureObject, bodyTopArmatureObject]
    # print("bodyTopArmatureObject: ", bodyTopArmatureObject)
    # print("selectedObjects: ", selectedObjects)
    with bpy.context.temp_override(active_object=bodyArmatureObject, selected_editable_objects=selectedObjects):
        bpy.ops.object.join()

    # * ########################################################################
    # * Join hair armature to body armature.
    # * ########################################################################

    bpy.ops.object.select_all(action="DESELECT")
    selectedObjects = [bodyArmatureObject, hairArmatureObject]
    print("-- bodyArmatureObject: ", bodyArmatureObject)
    print("selectedObjects: ", selectedObjects)
    with bpy.context.temp_override(active_object=bodyArmatureObject, selected_editable_objects=selectedObjects):
        bpy.ops.object.join()
    print("-- bodyArmatureObject: ", bodyArmatureObject)

    # * ########################################################################
    # * Set parent of hair with body armature.
    # * ########################################################################

    # Initialize objection selection by deselecting all.
    bpy.ops.object.select_all(action="DESELECT")
    # Select hair object, if any.
    hairObject.select_set(True)
    # Select armature object, if any.
    bpy.context.view_layer.objects.active = bodyArmatureObject
    # Set parent of face object to body armature.
    bpy.ops.object.parent_set(
        type="OBJECT", keep_transform=True)
    # Initialize objection selection by deselecting all.
    bpy.ops.object.select_all(action="DESELECT")

    # * ########################################################################
    # * Set parent of hair armature with body armature of J_Bip_C_Head.
    # * ########################################################################

    # Initialize headBone and headEditBone as None.
    headBone = None
    headEditBone = None

    # Find J_Bip_C_Head bone.
    for bone in bodyArmatureObject.data.bones:
        if (bone.name == "J_Bip_C_Head"):
            # print("found J_Bip_C_Head object")
            headBone = bone
            break

    # Set active object.
    bpy.context.view_layer.objects.active = bodyArmatureObject
    bodyArmatureObject.data.bones.active = headBone

    # Set armature edit mode.
    if bpy.context.mode != "EDIT_ARMATURE":
        bpy.ops.object.mode_set(mode="EDIT")

    # Find J_Bip_C_Head edit bone.
    for bone in bodyArmature.edit_bones:
        # 3-1. Find J_Bip_C_Head bone.
        if (bone.name == "J_Bip_C_Head"):
            # print("found headBone: ", headBone)
            headEditBone = bone
            break

        # Connect J_Sec_Hair1... to headEditBone as child bone.
    if headBone != None and headEditBone != None:
        for bone in bodyArmature.edit_bones:
            # Naming pattern.
            # J_Sec_Hair1_01, J_Sec_Hair2_01, ..., J_Sec_HairN_01.
            if "J_Sec_Hair1" in bone.name:
                bpy.ops.armature.select_all(action="DESELECT")
                bone.parent = headEditBone
                bone.use_connect = True

        # Set object mode.
    bpy.ops.object.mode_set(mode="OBJECT")

    # * ########################################################################
    # * Bind blend shape for face.
    # * ########################################################################
    blend_shape_groups = (
        armature.data.vrm_addon_extension.vrm0.blend_shape_master.blend_shape_groups
    )
    for blend_shape_group in blend_shape_groups:
        for bind in blend_shape_group.binds:
            if bind.index == "Fcl_MTH_A" or \
                    bind.index == "Fcl_MTH_I" or \
                    bind.index == "Fcl_MTH_U" or \
                    bind.index == "Fcl_MTH_E" or \
                    bind.index == "Fcl_MTH_O" or \
                    bind.index == "Fcl_EYE_Close_L" or \
                    bind.index == "Fcl_EYE_Close_R":
                bind.mesh.value = "Face"
                bind.weight = 100

    # * ########################################################################
    # * Handle hair sping bone.
    # * ########################################################################
    # Get secondary animation data.
    secondary_animation = (
        armature.data.vrm_addon_extension.vrm0.secondary_animation
    )

    # Copy hair secondary animation bone group to body secondary animation bone group.
    for hairBoneGroup in hairBoneGroupArray:
        bone_group = secondary_animation.bone_groups.add()

        bone_group.comment = hairBoneGroup.comment
        bone_group.stiffiness = hairBoneGroup.stiffiness
        bone_group.gravity_power = hairBoneGroup.gravity_power
        bone_group.gravity_dir = hairBoneGroup.gravity_dir
        bone_group.drag_force = hairBoneGroup.drag_force
        bone_group.hit_radius = hairBoneGroup.hit_radius

        # Copy hair bone list.
        for hairBone in hairBoneGroup.bones:
            # print("hairBone.value: ", hairBone.value)
            bone = bone_group.bones.add()
            bone.value = hairBone.value

        # Copy hair collider list.
        for hairColliderGroup in hairColliderGroupArray:
            collider_group = bone_group.collider_groups.add()
            collider_group.value = hairColliderGroup.name

        # for collider_group in bone_group.collider_groups:
        #     print("collider_group.value: ", collider_group.value)

        bone_group.show_expanded = hairBoneGroup.show_expanded
        bone_group.show_expanded_bones = hairBoneGroup.show_expanded_bones
        bone_group.show_expanded_collider_groups = hairBoneGroup.show_expanded_collider_groups

    # * ########################################################################
    # * Set parent of accessories with head bone.
    # * ########################################################################
    add_accessory_objects()

    # * ########################################################################
    # * Join body_top and body_bottom to body.
    # * ########################################################################

    if (bodyTopObject):
        bpy.ops.object.select_all(action="DESELECT")
        selectedObjects = [bodyObject, bodyTopObject]
        # print("bodyTopObject: ", bodyTopObject)
        # print("selectedObjects: ", selectedObjects)
        with bpy.context.temp_override(active_object=bodyObject, selected_editable_objects=selectedObjects):
            bpy.ops.object.join()

    if (bodyBottomObject):
        bpy.ops.object.select_all(action="DESELECT")
        selectedObjects = [bodyObject, bodyBottomObject]
        # print("bodyBottomObject: ", bodyBottomObject)
        # print("selectedObjects: ", selectedObjects)
        with bpy.context.temp_override(active_object=bodyObject, selected_editable_objects=selectedObjects):
            bpy.ops.object.join()

    # * ########################################################################
    # * Change the angle of J_Bip_L_UpperArm and J_Bip_R_UpperArm.
    # * J_Bip_L_LowerArm and J_Bip_R_LowerArm also.
    # * ########################################################################
    change_bone_angle("J_Bip_L_UpperArm", "X", -70)
    change_bone_angle("J_Bip_L_LowerArm", "X", -10)
    change_bone_angle("J_Bip_R_UpperArm", "X", -70)
    change_bone_angle("J_Bip_R_LowerArm", "X", -10)

    # * ########################################################################
    # * Render model to image.
    # * ########################################################################
    render_image(str(id))

    # * ########################################################################
    # * Remove background object.
    # * ########################################################################
    background_object = bpy.context.scene.objects.get("background")
    bpy.data.objects.remove(background_object)

    # * ########################################################################
    # * Render model to glb.
    # * ########################################################################
    # render_glb(str(id))

    # * ########################################################################
    # * Render model to vrm.
    # * ########################################################################
    render_vrm(str(id))

    # * ########################################################################
    # * Remove assets.
    # * ########################################################################
    remove_assets()

    # * ########################################################################
    # * Print log.
    # * ########################################################################
    print("Generated model id: {}\n".format(id))


def console_print(*args, **kwargs):
    # For blender console.
    for a in bpy.context.screen.areas:
        if a.type == 'CONSOLE':
            c = {}
            c['area'] = a
            c['space_data'] = a.spaces.active
            c['region'] = a.regions[-1]
            c['window'] = bpy.context.window
            c['screen'] = bpy.context.screen
            s = " ".join([str(arg) for arg in args])
            for line in s.split("\n"):
                bpy.ops.console.scrollback_append(c, text=line)


# def print(*args, **kwargs):
#     """Console print() function."""

#     console_print(*args, **kwargs)  # to py consoles
#     __builtin__.print(*args, **kwargs)  # to system console


def print_all_values(input):
    if isinstance(input, dict):
        for key, value in input.items():
            print_all_values(value)
    elif isinstance(input, list):
        for value in input:
            print_all_values(value)
    else:
        print(input)


def main():
    # Parts directory containing each directory like "body" or "head" or "misc".
    # Add the tailing directory mark.
    parts_dir = sys.argv[3] + "/"
    start_token_id = int(sys.argv[4])
    # Because range function exclude the last one.
    end_token_id = int(sys.argv[5]) + 1
    # print("parts_dirs: ", parts_dir)

    ###########################################################################
    # Check directory exists.
    ###########################################################################
    if path.exists(parts_dir) == False:
        print(
            f"ERROR: Parts directory({parts_dir}) does not exist. Set the parts directory.")
        return

    if path.exists(IMAGE_OUTPUTS_DIR) == False:
        print(f"ERROR: Outputs directory({IMAGE_OUTPUTS_DIR}) does not exist.")
        os.makedirs(IMAGE_OUTPUTS_DIR, exist_ok=True)
    if path.exists(GLB_OUTPUTS_DIR) == False:
        print(f"ERROR: Outputs directory({GLB_OUTPUTS_DIR}) does not exist.")
        os.makedirs(GLB_OUTPUTS_DIR, exist_ok=True)
    if path.exists(VRM_OUTPUTS_DIR) == False:
        print(f"ERROR: Outputs directory({VRM_OUTPUTS_DIR}) does not exist.")
        os.makedirs(VRM_OUTPUTS_DIR, exist_ok=True)
    if path.exists(VIDEO_OUTPUTS_DIR) == False:
        print(f"ERROR: Outputs directory({VIDEO_OUTPUTS_DIR}) does not exist.")
        os.makedirs(VIDEO_OUTPUTS_DIR, exist_ok=True)

    print("Start generating models...")

    ###########################################################################
    # Initialize.
    ###########################################################################
    initialize()

    ###########################################################################
    # Set rendering configuration.
    ###########################################################################
    set_render_config()

    ###########################################################################
    # Remove all files in build directory.
    ###########################################################################
    for f in os.listdir(IMAGE_OUTPUTS_DIR):
        os.remove(os.path.join(IMAGE_OUTPUTS_DIR, f))
    for f in os.listdir(VIDEO_OUTPUTS_DIR):
        os.remove(os.path.join(VIDEO_OUTPUTS_DIR, f))
    for f in os.listdir(GLB_OUTPUTS_DIR):
        os.remove(os.path.join(GLB_OUTPUTS_DIR, f))
    for f in os.listdir(VRM_OUTPUTS_DIR):
        os.remove(os.path.join(VRM_OUTPUTS_DIR, f))
    ###########################################################################

    ###########################################################################
    # Generate models as to metadata.
    ###########################################################################
    for token_id in range(start_token_id, end_token_id):
        json_file_path = METADATA_DIR + str(token_id) + ".json"

        print(f"Build #{token_id} nft metadata from {json_file_path}")
        with open(json_file_path, "r") as metadata_file:
            data = json.load(metadata_file)
            try:
                generate(token_id, data, parts_dir)
            except ValueError as Error:
                print("Error: ", Error)

    ###########################################################################
    # Print lmg.
    ###########################################################################
    print("Done.")


main()
