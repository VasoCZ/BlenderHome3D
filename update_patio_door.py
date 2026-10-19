"""
update_patio_door.py
===================
Fits and installs 'Japanese Sliding Window with Screen' into the patio door opening
of Room 1.04 (Obývací pokoj) in 'dum_pudorys.blend':
1. Replaces any duplicate/rough instance with the clean, complete assembly.
2. Scales and positions the assembly:
   - Width: scaled in X to span exactly X in [7.125, 8.925] m (width = 1.800 m).
   - Height: FloorLevel_Guide aligned with floor level Z = 0.000 m. Top reaches Z = 1.745 m.
   - Depth: positioned in Y in [11.710, 11.813] m within the 0.365 m wall thickness (Y in [11.635, 12.000] m).
3. Adds top lintel (nadpraží) to 'Exterior_Walls':
   - Spans X in [7.125, 8.925] m, Y in [11.635, 12.000] m, Z in [1.745, 1.800] m.
   - Completely covers the window frame from above so it is flush with wall top Z = 1.800 m.
4. Renders verification views (top-down, isometric zoom, interior, and floor plan overview).
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

def hex_to_linear(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    to_lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (to_lin(r), to_lin(g), to_lin(b), 1.0)

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 1. Clean up duplicate / partial collection (.001) if present
    coll_001 = bpy.data.collections.get("Japanese Sliding Window with Screen.001")
    if coll_001:
        print("[INFO] Cleaning up duplicate collection '.001'...")
        for obj in list(coll_001.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll_001)

    # Clean any leftover .001 objects
    for obj in list(bpy.data.objects):
        if "Japanese Sliding Window" in obj.name and ".001" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Find primary root object
    root = bpy.data.objects.get("Japanese Sliding Window with Screen")
    if not root:
        # Fallback search
        for obj in bpy.data.objects:
            if "Japanese Sliding Window" in obj.name and obj.type == 'EMPTY':
                root = obj
                break
    if not root:
        raise RuntimeError("Object 'Japanese Sliding Window with Screen' not found in scene!")

    frame = bpy.data.objects.get("Frame_Aluminum")
    floor_guide = bpy.data.objects.get("FloorLevel_Guide")
    if not frame:
        raise RuntimeError("Component 'Frame_Aluminum' not found!")

    # Reset root transform to analyze native local bounds
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)
    bpy.context.view_layer.update()

    # Bounding box of Frame_Aluminum
    bbox_frame = [frame.matrix_world @ Vector(c) for c in frame.bound_box]
    frame_min_x = min(c.x for c in bbox_frame)
    frame_max_x = max(c.x for c in bbox_frame)
    frame_cur_w = frame_max_x - frame_min_x
    frame_center_x = (frame_min_x + frame_max_x) / 2.0

    frame_min_z = min(c.z for c in bbox_frame)
    frame_max_z = max(c.z for c in bbox_frame)

    floor_z = floor_guide.location.z if floor_guide else 0.0580
    frame_visible_h = frame_max_z - floor_z

    print(f"Native frame: width={frame_cur_w:.4f} m, visible_height={frame_visible_h:.4f} m")

    # 3. Target parameters for Room 1.04 Patio Door:
    # Opening: X in [7.125, 8.925] m (width = 1.800 m)
    # North wall: Y in [11.635, 12.000] m (thickness = 0.365 m)
    # Cutaway wall height: Z = 1.800 m
    # Top lintel: Z in [1.745, 1.800] m -> target frame visible top = 1.745 m
    target_min_x = 7.125
    target_max_x = 8.925
    target_w = target_max_x - target_min_x  # 1.800 m
    target_center_x = (target_min_x + target_max_x) / 2.0  # 8.025 m

    target_top_z = 1.745
    target_floor_z = 0.000
    target_visible_h = target_top_z - target_floor_z  # 1.745 m

    # Scale factors
    scale_x = target_w / frame_cur_w
    scale_z = target_visible_h / frame_visible_h
    scale_y = 1.0  # Keep natural profile depth (0.103 m)

    print(f"Applying scale: X={scale_x:.6f}, Y={scale_y:.6f}, Z={scale_z:.6f}")

    # Position calculations:
    # X: center of frame lands at target_center_x
    loc_x = target_center_x - scale_x * frame_center_x

    # Z: FloorLevel_Guide lands at target_floor_z (0.000 m)
    # Z_world = loc_z + scale_z * floor_z = 0 -> loc_z = -scale_z * floor_z
    loc_z = target_floor_z - scale_z * floor_z

    # Y: inside face of frame placed at Y = 11.710 m
    # This leaves 7.5 cm interior reveal and 18.7 cm exterior reveal
    loc_y = 11.710

    root.scale = (scale_x, scale_y, scale_z)
    root.location = (loc_x, loc_y, loc_z)
    bpy.context.view_layer.update()

    # Verify world bounds
    bbox_after = [frame.matrix_world @ Vector(c) for c in frame.bound_box]
    min_after = Vector([min(c[i] for c in bbox_after) for i in range(3)])
    max_after = Vector([max(c[i] for c in bbox_after) for i in range(3)])
    print(f"[OK] Japanese Sliding Window placed:")
    print(f"     X: [{min_after.x:.4f}, {max_after.x:.4f}] (width: {max_after.x - min_after.x:.4f} m)")
    print(f"     Y: [{min_after.y:.4f}, {max_after.y:.4f}] (depth: {max_after.y - min_after.y:.4f} m)")
    print(f"     Z: [{min_after.z:.4f}, {max_after.z:.4f}] (top: {max_after.z:.4f} m)")

    # 4. Update 'Exterior_Walls' to add top lintel (nadpraží) covering the window from above
    ew = bpy.data.objects.get("Exterior_Walls")
    if not ew:
        raise RuntimeError("Object 'Exterior_Walls' not found in scene!")

    bm = bmesh.new()
    bm.from_mesh(ew.data)

    def add_box_to_bm(bm, x0, x1, y0, y1, z0, z1, mat_idx=0):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        faces = [
            [v[0], v[1], v[2], v[3]],  # bottom
            [v[4], v[7], v[6], v[5]],  # top
            [v[0], v[4], v[5], v[1]],  # south (-Y)
            [v[2], v[6], v[7], v[3]],  # north (+Y)
            [v[0], v[3], v[7], v[4]],  # west (-X)
            [v[1], v[5], v[6], v[2]],  # east (+X)
        ]
        for fverts in faces:
            f = bm.faces.new(fverts)
            f.material_index = mat_idx

    # Add top lintel spanning full opening width (7.125 to 8.925) and full wall thickness (11.635 to 12.000)
    # Height Z in [1.745, 1.800] m
    add_box_to_bm(bm, 7.125, 8.925, 11.635, 12.000, 1.745, 1.800, mat_idx=0)

    # Weld vertices at seams and recalculate normals
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(ew.data)
    bm.free()
    ew.data.update()
    print("[OK] Top lintel (nadpraží) added to Exterior_Walls at Z in [1.745, 1.800] m.")

    # 5. Ensure Isometric_Camera is preserved
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # 6. Save updated blend file
    bpy.ops.wm.save_mainfile()
    print(f"[OK] Successfully saved '{blend_path}'!")

    # 7. Render verification views
    render_verification_views(iso_cam)

def render_verification_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: Top-down close-up of patio door opening (proves the top is covered)
    cam1_data = bpy.data.cameras.new("Cam_Patio_TopDown")
    cam1_data.type = 'ORTHO'
    cam1_data.ortho_scale = 3.5
    cam1 = bpy.data.objects.new("Cam_Patio_TopDown", cam1_data)
    scene.collection.objects.link(cam1)
    cam1.location = Vector((8.025, 11.817, 6.0))
    cam1.rotation_euler = (0, 0, 0)
    scene.camera = cam1
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.filepath = os.path.abspath("patio_door_topdown.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: patio_door_topdown.png")

    # View 2: Perspective isometric zoom from terrace
    cam2_data = bpy.data.cameras.new("Cam_Patio_IsoZoom")
    cam2 = bpy.data.objects.new("Cam_Patio_IsoZoom", cam2_data)
    scene.collection.objects.link(cam2)
    cam2.location = Vector((6.2, 14.8, 3.2))
    cam2.rotation_euler = (Vector((8.025, 11.8, 1.0)) - cam2.location).to_track_quat('-Z', 'Y').to_euler()
    cam2_data.type = 'PERSP'
    cam2_data.lens = 45
    scene.camera = cam2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("patio_door_isometric.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: patio_door_isometric.png")

    # View 3: Interior view from Living Room 1.04 looking out
    cam3_data = bpy.data.cameras.new("Cam_Patio_Interior")
    cam3 = bpy.data.objects.new("Cam_Patio_Interior", cam3_data)
    scene.collection.objects.link(cam3)
    cam3.location = Vector((8.025, 8.8, 1.3))
    cam3.rotation_euler = (Vector((8.025, 12.0, 1.0)) - cam3.location).to_track_quat('-Z', 'Y').to_euler()
    cam3_data.type = 'PERSP'
    cam3_data.lens = 38
    scene.camera = cam3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("patio_door_interior.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: patio_door_interior.png")

    # View 4: Full overview with preserved Isometric_Camera
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # Clean up temporary cameras
    for c in [cam1, cam2, cam3]:
        bpy.data.objects.remove(c, do_unlink=True)
    for cd in [cam1_data, cam2_data, cam3_data]:
        bpy.data.cameras.remove(cd)

    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print("Cleaned up temporary cameras and resaved 'dum_pudorys.blend'.")

if __name__ == "__main__":
    main()
