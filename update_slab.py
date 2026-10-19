"""
update_slab.py
Updates the 'Foundation_Slab' object in 'dum_pudorys.blend':
1. Replaces 'Foundation_Slab' with a strictly rectilinear, all-quad paved area:
   - All junctions between the perimeter walkway, driveway, and terrace are 100% perpendicular (kolmé).
   - Zero diagonal / slanted edges anywhere in the mesh.
   - Okapový chodník (perimeter walkway): 1.2 m around house (10.0 x 12.0 m) -> X in [-1.2, 11.2], Y in [-1.2, 13.2]
   - Zadní terasa (rear terrace): connects to Living Room 1.04 in +Y -> X in [5.0, 10.0] (width 5.0 m), Y in [12.0, 18.0] (depth 6.0 m)
   - Přední příjezdová plocha (front driveway): in front of 1.01 in -Y -> X in [2.19, 8.19] (width 6.0 m), Y in [-9.0, 0.0] (length 9.0 m)
   - Paved surface at height Z = 0.0 m (slab thickness 0.20 m down to Z = -0.20 m)
2. Assigns uniform outdoor concrete paving material (Mat_Outdoor_Concrete_Paving):
   - Base Color: #2B2D31
   - Roughness: 0.45
3. Preserves user modifications:
   - Ceiling remains removed (no Ceiling_Main).
   - Camera view (location, rotation, ortho_scale) remains untouched.
4. Saves to 'dum_pudorys.blend' and renders preview image.
"""

import sys
import os
import bpy
import bmesh

def hex_to_linear(hex_str):
    """Converts a hex color string (e.g. '#2B2D31') to Blender linear RGB tuple."""
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    to_lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (to_lin(r), to_lin(g), to_lin(b), 1.0)

def main():
    print("=" * 60)
    print("UPDATING FOUNDATION SLAB (RECTILINEAR ALL-QUAD TOPOLOGY)")
    print("=" * 60)

    # 1. Load dum_pudorys.blend
    blend_path = os.path.abspath("dum_pudorys.blend")
    if not bpy.data.filepath or os.path.abspath(bpy.data.filepath) != blend_path:
        bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 2. Ensure ceiling remains removed per user instruction
    ceil = bpy.data.objects.get("Ceiling_Main")
    if ceil:
        bpy.data.objects.remove(ceil, do_unlink=True)
        print("[OK] Preserved user edit: 'Ceiling_Main' removed.")
    if "Ceiling_Main" in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes["Ceiling_Main"])

    # 3. Construct strictly orthogonal rectilinear mesh
    # Unified X cuts:
    # x0 = -1.2 (west edge of walkway)
    # x1 =  2.19 (west edge of driveway)
    # x2 =  5.00 (west edge of terrace)
    # x3 =  8.19 (east edge of driveway)
    # x4 = 10.00 (east edge of terrace)
    # x5 = 11.20 (east edge of walkway)
    x_cuts = [-1.2, 2.19, 5.0, 8.19, 10.0, 11.2]

    # Unified Y cuts:
    # y0 = -9.0 (south edge of driveway)
    # y1 = -1.2 (south edge of walkway)
    # y2 =  0.0 (south wall of house)
    # y3 = 12.0 (north wall of house)
    # y4 = 13.2 (north edge of walkway)
    # y5 = 18.0 (north edge of terrace)
    y_cuts = [-9.0, -1.2, 0.0, 12.0, 13.2, 18.0]

    # Active grid cells: (col_idx, row_idx)
    # Row 0 (Y: [-9.0, -1.2]): cols 1, 2 (Driveway)
    # Row 1 (Y: [-1.2, 0.0]): cols 0..4 (South walkway + driveway connection)
    # Row 2 (Y: [0.0, 12.0]): cols 0..4 (House base + side walkways)
    # Row 3 (Y: [12.0, 13.2]): cols 0..4 (North walkway + terrace connection)
    # Row 4 (Y: [13.2, 18.0]): cols 2, 3 (Terrace)
    active_cells = []
    active_cells.extend([(1, 0), (2, 0)])
    for r in [1, 2, 3]:
        for c in range(5):
            active_cells.append((c, r))
    active_cells.extend([(2, 4), (3, 4)])

    z_top = 0.0
    z_bot = -0.20

    mesh_name = "Foundation_Slab_Mesh"
    if mesh_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[mesh_name])

    slab_mesh = bpy.data.meshes.new(mesh_name)
    bm = bmesh.new()

    verts_dict = {}
    def get_vert(c, r, z):
        key = (c, r, z)
        if key not in verts_dict:
            verts_dict[key] = bm.verts.new((x_cuts[c], y_cuts[r], z))
        return verts_dict[key]

    cell_set = set(active_cells)

    for c, r in active_cells:
        v_b_sw = get_vert(c, r, z_bot)
        v_b_se = get_vert(c+1, r, z_bot)
        v_b_ne = get_vert(c+1, r+1, z_bot)
        v_b_nw = get_vert(c, r+1, z_bot)

        v_t_sw = get_vert(c, r, z_top)
        v_t_se = get_vert(c+1, r, z_top)
        v_t_ne = get_vert(c+1, r+1, z_top)
        v_t_nw = get_vert(c, r+1, z_top)

        # Top quad face (normal pointing +Z upwards)
        bm.faces.new([v_t_sw, v_t_se, v_t_ne, v_t_nw])
        # Bottom quad face (normal pointing -Z downwards)
        bm.faces.new([v_b_sw, v_b_nw, v_b_ne, v_b_se])

        # Vertical side quad faces on boundary edges:
        # South edge: (c, r) -> (c+1, r)
        if (c, r-1) not in cell_set:
            bm.faces.new([v_b_sw, v_b_se, v_t_se, v_t_sw])
        # North edge: (c+1, r+1) -> (c, r+1)
        if (c, r+1) not in cell_set:
            bm.faces.new([v_b_ne, v_b_nw, v_t_nw, v_t_ne])
        # West edge: (c, r+1) -> (c, r)
        if (c-1, r) not in cell_set:
            bm.faces.new([v_b_nw, v_b_sw, v_t_sw, v_t_nw])
        # East edge: (c+1, r) -> (c+1, r+1)
        if (c+1, r) not in cell_set:
            bm.faces.new([v_b_se, v_b_ne, v_t_ne, v_t_se])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(slab_mesh)
    bm.free()

    # Assign mesh to Foundation_Slab
    slab_obj = bpy.data.objects.get("Foundation_Slab")
    if not slab_obj:
        slab_obj = bpy.data.objects.new("Foundation_Slab", slab_mesh)
        bpy.context.scene.collection.objects.link(slab_obj)
    else:
        old_mesh = slab_obj.data
        slab_obj.data = slab_mesh
        if old_mesh and old_mesh != slab_mesh and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)

    slab_obj.location = (0.0, 0.0, 0.0)
    print(f"[OK] Foundation_Slab replaced with 100% rectilinear all-quad mesh (zero diagonal edges).")

    # 4. Material: tmavší šedá venkovní betonová dlažba (#2B2D31, Roughness 0.45)
    mat_name = "Mat_Outdoor_Concrete_Paving"
    mat_paving = bpy.data.materials.get(mat_name)
    if not mat_paving:
        mat_paving = bpy.data.materials.new(name=mat_name)

    if mat_paving.node_tree is None and hasattr(mat_paving, "use_nodes"):
        mat_paving.use_nodes = True

    bsdf = mat_paving.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = hex_to_linear("2B2D31")
        bsdf.inputs["Roughness"].default_value = 0.45
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.35

    slab_obj.data.materials.clear()
    slab_obj.data.materials.append(mat_paving)
    print(f"[OK] Material '{mat_name}' (#2B2D31, Roughness 0.45) assigned.")

    # 5. User camera: untouched!
    cam = bpy.data.objects.get("Isometric_Camera")
    if cam:
        print(f"[INFO] Preserved user camera settings: loc={tuple(round(v, 2) for v in cam.location)}, ortho_scale={cam.data.ortho_scale:.2f}")

    # 6. Save changes
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved scene to {blend_path}")

    # 7. Render preview image
    try:
        preview_path = os.path.abspath("dum_pudorys_preview.png")
        bpy.context.scene.render.filepath = preview_path
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered preview image to: {preview_path}")
    except Exception as e:
        print(f"[NOTE] Render notice: {e}")

    print("=" * 60)
    print("UPDATE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
