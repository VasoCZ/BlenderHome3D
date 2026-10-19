"""
update_paving_curbs.py
======================
Updates the outdoor paving and adds realistic concrete garden curbs:
1. Configures 'Foundation_Slab' with realistic paver thickness using a Solidify modifier:
   - 2D all-quad rectilinear surface at Z = 0.000 m.
   - Solidify modifier: thickness = 0.08 m (8 cm), offset = -1.0 (downwards to Z = -0.08 m).
   - Preserves user material 'Stone ground tile'.
2. Generates 'Garden_Curbs' (Zahradní obrubníky) framing all exterior perimeter edges:
   - Follows the 12 rectilinear boundary segments of the paved area.
   - Width = 0.08 m (8 cm).
   - Height = raised +0.035 m (3.5 cm) above paving level Z = 0.000 m (Z in [-0.100, +0.035] m).
   - Beautiful 5 mm bevel on top edges for realistic specular highlights.
   - Dedicated dark anthracite concrete material 'Mat_Garden_Curb' (#1A1B1D, roughness 0.65).
   - Casts crisp contact shadows onto the paving and naturally frames the diorama.
3. Renders verification views (isometric zoom, terrace view, driveway view, full overview).
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

    # ----------------------------------------------------
    # 1. Update Foundation_Slab with Solidify modifier (8 cm thickness)
    # ----------------------------------------------------
    slab_obj = bpy.data.objects.get("Foundation_Slab")
    if not slab_obj:
        raise RuntimeError("Object 'Foundation_Slab' not found!")

    # Preserve existing material
    existing_mat = slab_obj.data.materials[0] if slab_obj.data.materials else None

    # Unified grid cuts from update_slab.py
    x_cuts = [-1.2, 2.19, 5.0, 8.19, 10.0, 11.2]
    y_cuts = [-9.0, -1.2, 0.0, 12.0, 13.2, 18.0]

    active_cells = []
    active_cells.extend([(1, 0), (2, 0)]) # Driveway
    for r in [1, 2, 3]:
        for c in range(5):
            active_cells.append((c, r))   # Walkway + House base
    active_cells.extend([(2, 4), (3, 4)]) # Terrace

    # Build clean 2D quad mesh at Z = 0.000 m directly into slab_obj.data
    bm_slab = bmesh.new()

    v_cache = {}
    def get_slab_vert(c, r):
        key = (c, r)
        if key not in v_cache:
            v_cache[key] = bm_slab.verts.new((x_cuts[c], y_cuts[r], 0.000))
        return v_cache[key]

    for c, r in active_cells:
        v_sw = get_slab_vert(c, r)
        v_se = get_slab_vert(c+1, r)
        v_ne = get_slab_vert(c+1, r+1)
        v_nw = get_slab_vert(c, r+1)
        bm_slab.faces.new([v_sw, v_se, v_ne, v_nw])

    bmesh.ops.recalc_face_normals(bm_slab, faces=bm_slab.faces)
    slab_obj.data.clear_geometry()
    bm_slab.to_mesh(slab_obj.data)
    bm_slab.free()
    slab_obj.data.update()

    if existing_mat and (not slab_obj.data.materials or slab_obj.data.materials[0] != existing_mat):
        slab_obj.data.materials.clear()
        slab_obj.data.materials.append(existing_mat)

    # Configure Solidify modifier on Foundation_Slab (8 cm real paver thickness)
    slab_obj.modifiers.clear()
    mod_solid = slab_obj.modifiers.new(name="Solidify_Paving", type='SOLIDIFY')
    mod_solid.thickness = 0.08  # 8 cm thickness (range 6-10 cm per user request)
    mod_solid.offset = -1.0     # Downwards to Z = -0.08 m so top remains at Z = 0.00 m
    mod_solid.use_even_offset = True
    mod_solid.use_rim = True
    mod_solid.use_rim_only = False
    print("[OK] Foundation_Slab configured with Solidify modifier (thickness = 8 cm, offset = -1.0).")

    # ----------------------------------------------------
    # 2. Material for Garden Curbs: Mat_Garden_Curb
    # ----------------------------------------------------
    mat_curb_name = "Mat_Garden_Curb"
    mat_curb = bpy.data.materials.get(mat_curb_name)
    if not mat_curb:
        mat_curb = bpy.data.materials.new(name=mat_curb_name)
    if mat_curb.node_tree is None and hasattr(mat_curb, "use_nodes"):
        mat_curb.use_nodes = True
    bsdf = mat_curb.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Dark anthracite concrete (#1A1B1D)
        bsdf.inputs["Base Color"].default_value = hex_to_linear("1A1B1D")
        bsdf.inputs["Roughness"].default_value = 0.65
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.20
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.20

    # ----------------------------------------------------
    # 3. Construct Garden Curbs (Zahradní obrubníky)
    # ----------------------------------------------------
    curb_obj_name = "Garden_Curbs"
    if curb_obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[curb_obj_name], do_unlink=True)
    if curb_obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[curb_obj_name])

    curb_mesh = bpy.data.meshes.new(curb_obj_name)
    bm_curb = bmesh.new()

    # 12 boundary vertices of the paving in CCW order
    inner_pts = [
        (2.19, -9.00), (8.19, -9.00), (8.19, -1.20), (11.20, -1.20),
        (11.20, 13.20), (10.00, 13.20), (10.00, 18.00), (5.00, 18.00),
        (5.00, 13.20), (-1.20, 13.20), (-1.20, -1.20), (2.19, -1.20)
    ]
    n = len(inner_pts)
    w_curb = 0.08  # 8 cm curb width

    # Calculate exact orthogonal corner miter points
    edge_normals = []
    for i in range(n):
        p0 = inner_pts[i]
        p1 = inner_pts[(i + 1) % n]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        # Right-hand normal for CCW polygon: outward normal pointing away from paving
        edge_normals.append((uy, -ux))

    outer_pts = []
    for i in range(n):
        n_prev = edge_normals[(i - 1) % n]
        n_curr = edge_normals[i]
        ox = w_curb * (n_prev[0] + n_curr[0])
        oy = w_curb * (n_prev[1] + n_curr[1])
        outer_pts.append((inner_pts[i][0] + ox, inner_pts[i][1] + oy))

    z_curb_top = 0.035  # Raised 3.5 cm above paving Z = 0.000 m (range 2-5 cm per user request)
    z_paving = 0.000    # Paving surface level
    z_curb_bot = -0.100 # Embedded 2 cm below paver bottom Z = -0.08 m

    # Create vertices for curb ring
    v_in_top = [bm_curb.verts.new((x, y, z_curb_top)) for x, y in inner_pts]
    v_in_pav = [bm_curb.verts.new((x, y, z_paving))   for x, y in inner_pts]
    v_in_bot = [bm_curb.verts.new((x, y, z_curb_bot)) for x, y in inner_pts]

    v_out_top = [bm_curb.verts.new((x, y, z_curb_top)) for x, y in outer_pts]
    v_out_bot = [bm_curb.verts.new((x, y, z_curb_bot)) for x, y in outer_pts]

    for i in range(n):
        i_next = (i + 1) % n

        # 1. Top horizontal face (Z = +0.035 m, width = 8 cm, normal +Z upwards)
        bm_curb.faces.new([v_in_top[i], v_in_top[i_next], v_out_top[i_next], v_out_top[i]])

        # 2. Exposed inner vertical face (from Z = +0.035 m to Z = 0.000 m, height = 3.5 cm, casts shadow on paving)
        bm_curb.faces.new([v_in_top[i_next], v_in_top[i], v_in_pav[i], v_in_pav[i_next]])

        # 3. Sub-paving inner vertical face (from Z = 0.000 m to Z = -0.100 m, meets paver slab side)
        bm_curb.faces.new([v_in_pav[i_next], v_in_pav[i], v_in_bot[i], v_in_bot[i_next]])

        # 4. Outer vertical face (from Z = +0.035 m to Z = -0.100 m, height = 13.5 cm)
        bm_curb.faces.new([v_out_top[i], v_out_top[i_next], v_out_bot[i_next], v_out_bot[i]])

        # 5. Bottom horizontal face (Z = -0.100 m)
        bm_curb.faces.new([v_out_bot[i], v_out_bot[i_next], v_in_bot[i_next], v_in_bot[i]])

    bmesh.ops.recalc_face_normals(bm_curb, faces=bm_curb.faces)
    bm_curb.to_mesh(curb_mesh)
    bm_curb.free()

    curb_obj = bpy.data.objects.new(curb_obj_name, curb_mesh)
    bpy.context.scene.collection.objects.link(curb_obj)
    curb_obj.data.materials.append(mat_curb)

    # Add Bevel modifier for realistic concrete chamfer highlights
    mod_bevel = curb_obj.modifiers.new(name="Bevel_Edge", type='BEVEL')
    mod_bevel.width = 0.005  # 5 mm bevel
    mod_bevel.segments = 2
    mod_bevel.limit_method = 'ANGLE'
    mod_bevel.angle_limit = math.radians(40)

    print(f"[OK] Garden_Curbs created with 12 rectilinear segments, height Z in [-0.100, +0.035] m.")

    # Preserve Isometric_Camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # Save blend file
    bpy.ops.wm.save_mainfile()
    print(f"[OK] Saved '{blend_path}'.")

    # Render verification views
    render_curb_views(iso_cam)

def render_curb_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: Isometric close-up of terrace and garden curb showing the raised lip and cast shadow
    cam1_data = bpy.data.cameras.new("Cam_Curbs_IsoZoom")
    cam1 = bpy.data.objects.new("Cam_Curbs_IsoZoom", cam1_data)
    scene.collection.objects.link(cam1)
    cam1.location = Vector((3.5, 14.5, 3.8))
    cam1.rotation_euler = (Vector((7.5, 15.5, 0.0)) - cam1.location).to_track_quat('-Z', 'Y').to_euler()
    cam1_data.type = 'PERSP'
    cam1_data.lens = 40
    scene.camera = cam1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("curbs_terrace_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: curbs_terrace_view.png")

    # View 2: Driveway close-up showing curbs along the driveway edges and corner miters
    cam2_data = bpy.data.cameras.new("Cam_Curbs_Driveway")
    cam2 = bpy.data.objects.new("Cam_Curbs_Driveway", cam2_data)
    scene.collection.objects.link(cam2)
    cam2.location = Vector((0.5, -6.0, 3.5))
    cam2.rotation_euler = (Vector((5.19, -4.5, 0.0)) - cam2.location).to_track_quat('-Z', 'Y').to_euler()
    cam2_data.type = 'PERSP'
    cam2_data.lens = 38
    scene.camera = cam2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("curbs_driveway_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: curbs_driveway_view.png")

    # View 3: Full floor plan overview using user's Isometric_Camera
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # Clean up temporary cameras
    for c in [cam1, cam2]:
        bpy.data.objects.remove(c, do_unlink=True)
    for cd in [cam1_data, cam2_data]:
        bpy.data.cameras.remove(cd)

    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print("Cleaned up temporary cameras and resaved main blend file.")

if __name__ == "__main__":
    main()
