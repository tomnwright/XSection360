import bpy
import sys

filepath = bpy.path.abspath("//")
sys.path.append(filepath)

from init import register

register()
