import bpy
import sys

filepath = bpy.path.abspath("//")
sys.path.append(filepath)

from blender_addon import run

run(filepath)
