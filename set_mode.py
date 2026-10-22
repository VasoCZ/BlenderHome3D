"""
set_mode.py
Usage:
  blender dum_pudorys.blend -b --python set_mode.py -- [day|night]
Or simply import set_mode(mode) in python scripts.
"""

import sys
import bpy

def set_mode(mode='day'):
    scene = bpy.context.scene
    world = scene.world
    if not world or not world.node_tree:
        return
    bg = world.node_tree.nodes.get("Background")
    if not bg:
        return

    sun = bpy.data.objects.get("Sun_Fill")
    bath_daylight = bpy.data.objects.get("Light_Daylight_Fill_Bathroom_1.10")

    if mode == 'day':
        # Day mode: soft natural sky
        bg.inputs["Color"].default_value = (0.82, 0.90, 1.0, 1.0)
        bg.inputs["Strength"].default_value = 0.85
        if sun:
            sun.data.energy = 3.0
            sun.hide_render = False
        if bath_daylight:
            bath_daylight.data.energy = 16.0
            bath_daylight.hide_render = False
        print(">>> Set scene mode to DAY (Sun ON @ 3.0W, Sky ON @ 0.85, Bath daylight ON).")
    elif mode == 'night':
        # Night mode: deep blue-black night sky
        bg.inputs["Color"].default_value = (0.07, 0.14, 0.30, 1.0)
        bg.inputs["Strength"].default_value = 0.035
        if sun:
            sun.data.energy = 0.0
            sun.hide_render = True
        if bath_daylight:
            bath_daylight.data.energy = 0.0
            bath_daylight.hide_render = True
        print(">>> Set scene mode to NIGHT (Sun OFF, Sky Blue-Black @ 0.035, Bath daylight OFF).")

if __name__ == '__main__':
    args = sys.argv
    mode = 'day'
    if '--' in args:
        idx = args.index('--')
        if len(args) > idx + 1:
            mode = args[idx + 1].lower()
    set_mode(mode)
    bpy.ops.wm.save_mainfile()
