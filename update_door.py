"""
update_door.py
Script to fit and position the entrance door assembly ('Door', 'ram', 'dvere', 'dvere.001')
precisely into the entrance door opening of room 1.01 (Zádveří) in 'dum_pudorys.blend'.

Opening parameters (South wall):
- X in [4.640, 5.740] m -> Width = 1.100 m
- Y in [0.000, 0.365] m -> Wall thickness = 0.365 m
- Z in [0.000, 1.800] m -> Cutaway wall height = 1.800 m

Target door dimensions & placement:
- Frame ('ram') outer X: [4.640, 5.740] (width = 1.100 m)
- Frame ('ram') outer Y: [0.000, 0.1377] (flush with exterior facade Y=0.000)
- Frame ('ram') outer Z: [0.000, 1.800] (flush with floor Z=0.000 and wall top Z=1.800)
- Door leaf ('dvere') and handle ('dvere.001') child transforms update automatically.
"""

import os
import shutil
import bpy
from mathutils import Vector, Matrix

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    door = bpy.data.objects.get("Door")
    ram = bpy.data.objects.get("ram")
    wing = bpy.data.objects.get("dvere")
    handle = bpy.data.objects.get("dvere.001")

    if not ram:
        raise RuntimeError("Object 'ram' not found in scene!")

    # Current world bounding box of ram
    bbox_world = [ram.matrix_world @ Vector(c) for c in ram.bound_box]
    cur_min_x = min(c.x for c in bbox_world)
    cur_max_x = max(c.x for c in bbox_world)
    cur_min_y = min(c.y for c in bbox_world)
    cur_max_y = max(c.y for c in bbox_world)
    cur_min_z = min(c.z for c in bbox_world)
    cur_max_z = max(c.z for c in bbox_world)

    cur_sx = cur_max_x - cur_min_x
    cur_sz = cur_max_z - cur_min_z

    print(f"Current ram bounds: X=[{cur_min_x:.4f}, {cur_max_x:.4f}], Y=[{cur_min_y:.4f}, {cur_max_y:.4f}], Z=[{cur_min_z:.4f}, {cur_max_z:.4f}]")
    print(f"Current dimensions: width={cur_sx:.4f}, depth={(cur_max_y - cur_min_y):.4f}, height={cur_sz:.4f}")

    target_min_x = 4.640
    target_max_x = 5.740
    target_sx = target_max_x - target_min_x  # 1.100 m

    target_min_z = 0.000
    target_max_z = 1.800
    target_sz = target_max_z - target_min_z  # 1.800 m

    target_min_y = 0.000  # Flush with exterior wall surface

    scale_x = target_sx / cur_sx
    scale_z = target_sz / cur_sz
    scale_y = 1.0

    print(f"Applying scale: X={scale_x:.6f}, Y={scale_y:.6f}, Z={scale_z:.6f}")

    # World transformation matrix
    M = Matrix.Identity(4)
    M[0][0] = scale_x
    M[1][1] = scale_y
    M[2][2] = scale_z
    M[0][3] = target_min_x - scale_x * cur_min_x
    M[1][3] = target_min_y - scale_y * cur_min_y
    M[2][3] = target_min_z - scale_z * cur_min_z

    ram.matrix_world = M @ ram.matrix_world
    bpy.context.view_layer.update()

    print("--- UPDATED WORLD BOUNDS ---")
    for obj in [ram, wing, handle]:
        if obj:
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            min_c = Vector([min(c[i] for c in bbox) for i in range(3)])
            max_c = Vector([max(c[i] for c in bbox) for i in range(3)])
            print(f"{obj.name:12s}: min={min_c}, max={max_c}, size={max_c - min_c}")

    # Ensure Isometric_Camera is the active scene camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # Save updated blend file
    bpy.ops.wm.save_mainfile()
    print("Successfully saved 'dum_pudorys.blend'!")

    # Render verification views
    render_views(iso_cam)

def render_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # 1. Close-up front view from driveway
    cam_data1 = bpy.data.cameras.new("Cam_Front_Door")
    cam_obj1 = bpy.data.objects.new("Cam_Front_Door", cam_data1)
    scene.collection.objects.link(cam_obj1)
    cam_obj1.location = Vector((5.19, -3.5, 1.3))
    cam_obj1.rotation_euler = (Vector((5.19, 0.2, 0.9)) - cam_obj1.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("door_front_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: door_front_view.png")

    # 2. Angled perspective view showing door, wall opening, cornice and driveway
    cam_data2 = bpy.data.cameras.new("Cam_Perspective_Door")
    cam_obj2 = bpy.data.objects.new("Cam_Perspective_Door", cam_data2)
    scene.collection.objects.link(cam_obj2)
    cam_obj2.location = Vector((3.2, -4.5, 2.2))
    cam_obj2.rotation_euler = (Vector((5.19, 0.5, 1.0)) - cam_obj2.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj2
    scene.render.filepath = os.path.abspath("door_perspective_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: door_perspective_view.png")

    # 3. Interior view from room 1.01 Zádveří looking out at the door
    cam_data3 = bpy.data.cameras.new("Cam_Interior_Door")
    cam_obj3 = bpy.data.objects.new("Cam_Interior_Door", cam_data3)
    scene.collection.objects.link(cam_obj3)
    cam_obj3.location = Vector((5.19, 2.0, 1.2))
    cam_obj3.rotation_euler = (Vector((5.19, 0.0, 0.9)) - cam_obj3.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj3
    scene.render.filepath = os.path.abspath("door_interior_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: door_interior_view.png")

    # 4. Full floor plan overview using user's preserved Isometric_Camera
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # Clean up temporary cameras so scene is left tidy
    for cam in [cam_obj1, cam_obj2, cam_obj3]:
        bpy.data.objects.remove(cam, do_unlink=True)
    for cdata in [cam_data1, cam_data2, cam_data3]:
        bpy.data.cameras.remove(cdata)

    if iso_cam:
        scene.camera = iso_cam

    # Resave cleaned blend file
    bpy.ops.wm.save_mainfile()
    print("Final blend file saved with preserved Isometric_Camera.")

if __name__ == "__main__":
    main()
