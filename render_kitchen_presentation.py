import bpy
import bmesh
import mathutils
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from build_kitchen_v2 import build_kitchen

def main():
    # 1. Build and save kitchen in dum_pudorys.blend
    build_kitchen(save_file=True)

    scene = bpy.context.scene
    cam_iso = bpy.data.objects['Isometric_Camera']
    scene.camera = cam_iso
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.use_border = False

    # 2. Render Full Isometric Overview
    out_iso_full = r'C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\kitchen_isometric_full.png'
    scene.render.filepath = out_iso_full
    print("Rendering Full Isometric Overview...")
    bpy.ops.render.render(write_still=True)
    print("Saved:", out_iso_full)

    # 3. Render Zoomed Kitchen & Dining Crop from Isometric_Camera
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_min_x = 0.16
    scene.render.border_max_x = 0.58
    scene.render.border_min_y = 0.32
    scene.render.border_max_y = 0.88
    out_iso_zoom = r'C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\kitchen_isometric_zoom.png'
    scene.render.filepath = out_iso_zoom
    print("Rendering Zoomed Kitchen & Dining Crop...")
    bpy.ops.render.render(write_still=True)
    print("Saved:", out_iso_zoom)

    # 4. Render Perspective Matched to kuchyne.jpg
    scene.render.use_border = False
    
    # Remove existing Photo_Camera if present
    if 'Photo_Camera' in bpy.data.objects:
        obj_old = bpy.data.objects['Photo_Camera']
        cam_old = obj_old.data
        bpy.data.objects.remove(obj_old)
        bpy.data.cameras.remove(cam_old)

    cam_data = bpy.data.cameras.new('Photo_Camera')
    cam_data.type = 'PERSP'
    cam_data.lens = 17.5  # 17.5mm wide angle (like smartphone ultra-wide / wide)
    cam_obj = bpy.data.objects.new('Photo_Camera', cam_data)
    scene.collection.objects.link(cam_obj)

    # Position: standing in living room near dining table corner, looking into kitchen
    cam_obj.location = (7.10, 7.90, 1.48)
    target = mathutils.Vector((4.30, 11.10, 1.15))
    dir_v = target - cam_obj.location
    rot_quat = dir_v.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    scene.camera = cam_obj
    out_persp = r'C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\kitchen_photo_perspective_matched.png'
    scene.render.filepath = out_persp
    print("Rendering Perspective View matching kuchyne.jpg...")
    bpy.ops.render.render(write_still=True)
    print("Saved:", out_persp)

    # Clean up Photo_Camera so main scene keeps Isometric_Camera as active
    scene.camera = cam_iso
    bpy.data.objects.remove(cam_obj)
    bpy.data.cameras.remove(cam_data)
    scene.render.use_border = False
    bpy.ops.wm.save_mainfile()
    print("All renders and cleanup completed successfully.")

if __name__ == '__main__':
    main()
