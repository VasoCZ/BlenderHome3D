"""
apply_sokliky_and_bathroom_tiles.py
===================================
Applies:
1. Soklíky (15cm high tile baseboards, Z in [0.000, 0.150]m) in rooms with grey tile floors:
   - 1.01 Zádveří
   - 1.09 Technická místnost
   - 1.11 Chodba
   Material: 'koupelna stena' (grey ceramic concrete tile)

2. WC 1.08 wall tiles up to half height (cca do půlky, Z in [0.000, 1.150]m):
   - All 4 interior faces of WC 1.08 tiled in 'koupelna stena' up to Z = 1.150m.
   - Above Z = 1.150m up to 2.500m: clean white plaster.

3. Bathroom 1.10 full-height wall cladding (Z in [0.000, 2.500]m):
   - Shower area bordering brown/wood floor (X in [0.365, 1.368], Y in [9.900, 10.890]):
     - Left wall (West: X = 0.365, Y in [9.900, 10.890]): 'Plank stena.001' (wood cladding)
     - Opposite wall (South: Y = 9.900, X in [0.365, 1.368]): 'Plank stena.001' (wood cladding)
   - All other bathroom walls: 'koupelna stena' (grey tile)
     - North wall (Y = 11.635, X in [0.365, 2.875] including window reveals)
     - East wall (X = 2.875, Y in [9.900, 11.635])
     - West wall north of shower (X = 0.365, Y in [10.890, 11.635])
     - South wall east of shower (Y = 9.900, X in [1.368, 2.875] including door lintel)

4. Preserves:
   - Window heights aligned at Z_sill = 1.750m for WC, Tech, Bath.
   - Fireplace wall closure at (3.602, 7.100).
   - Obložkové zárubně, sills, floors.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

def assign_uvs(bm, uv_layer):
    for f in bm.faces:
        nx = abs(f.normal.x)
        ny = abs(f.normal.y)
        nz = abs(f.normal.z)
        for loop in f.loops:
            co = loop.vert.co
            if nx > 0.5:
                loop[uv_layer].uv = Vector((co.y, co.z))
            elif ny > 0.5:
                loop[uv_layer].uv = Vector((co.x, co.z))
            else:
                loop[uv_layer].uv = Vector((co.x, co.y))

def update_exterior_walls_tiles():
    print("[1] Updating Exterior_Walls with sokliky, WC half-tile, and Bathroom full cladding...")
    ext = bpy.data.objects.get("Exterior_Walls")
    if not ext:
        print("  ERROR: Exterior_Walls not found!")
        return

    mat_ext = bpy.data.materials.get("Mat_Exterior_Wall")
    mat_koupelna = bpy.data.materials.get("koupelna stena")
    mat_plank = bpy.data.materials.get("Plank stena.001")

    # Ensure material slots:
    # 0: Mat_Exterior_Wall
    # 1: koupelna stena
    # 2: Plank stena.001
    ext.data.materials.clear()
    ext.data.materials.append(mat_ext)
    ext.data.materials.append(mat_koupelna)
    ext.data.materials.append(mat_plank)

    idx_ext = 0
    idx_koupelna = 1
    idx_plank = 2

    bm = bmesh.new()
    bm.from_mesh(ext.data)

    # 1. Horizontal cuts at Z = 0.150 and Z = 1.150
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.150), plane_no=(0, 0, 1))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 1.150), plane_no=(0, 0, 1))

    # 2. Vertical cuts on South wall at X = 3.775 and X = 6.100 (bounding Room 1.01 Zadveri)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(3.775, 0, 0), plane_no=(1, 0, 0))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(6.100, 0, 0), plane_no=(1, 0, 0))

    # 3. Vertical cuts on West wall:
    # Y = 7.100 (South of WC), Y = 8.1625 (WC / Tech partition), Y = 9.900 (Tech / Bath partition), Y = 10.890 (Shower boundary)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 7.100, 0), plane_no=(0, 1, 0))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 8.1625, 0), plane_no=(0, 1, 0))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 9.900, 0), plane_no=(0, 1, 0))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 10.890, 0), plane_no=(0, 1, 0))

    # 4. Vertical cut on North wall at X = 2.875 (East of Bathroom)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(2.875, 0, 0), plane_no=(1, 0, 0))

    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Default all faces to idx_ext
    for f in bm.faces:
        f.material_index = idx_ext

    # Assign materials based on room zones
    for f in bm.faces:
        c = f.calc_center_median()
        n = f.normal

        # A) South wall inner face (Y = 0.365, normal +Y)
        if abs(n.y - 1.0) < 0.1 and abs(c.y - 0.365) < 0.05:
            # 1.01 Zadveri (X in [3.775, 6.100]): soklik at Z < 0.150
            if 3.775 <= c.x <= 6.100 and c.z < 0.150:
                f.material_index = idx_koupelna

        # B) West wall inner face (X = 0.365, normal +X)
        elif abs(n.x - 1.0) < 0.1 and abs(c.x - 0.365) < 0.05:
            # 1.08 WC (Y in [7.100, 8.1625]): half-height tile up to Z = 1.150m
            if 7.100 <= c.y < 8.1625 and c.z < 1.150:
                f.material_index = idx_koupelna

            # 1.09 Tech (Y in [8.1625, 9.900]): soklik at Z < 0.150
            elif 8.1625 <= c.y < 9.900 and c.z < 0.150:
                f.material_index = idx_koupelna

            # 1.10 Bath Shower (Y in [9.900, 10.890]): wooden cladding full height!
            elif 9.900 <= c.y < 10.890:
                f.material_index = idx_plank

            # 1.10 Bath Rest (Y in [10.890, 11.635]): grey tile full height!
            elif 10.890 <= c.y <= 11.640:
                f.material_index = idx_koupelna

        # C) North wall inner face (Y = 11.635, normal -Y)
        elif abs(n.y - (-1.0)) < 0.1 and abs(c.y - 11.635) < 0.05:
            # 1.10 Bath North wall (X in [0.365, 2.875]): grey tile full height!
            if 0.365 <= c.x <= 2.875:
                f.material_index = idx_koupelna

        # D) Bathroom window reveals inside window cutout W5 (X in [1.120, 2.120], Y in [11.635, 11.900])
        elif 1.120 <= c.x <= 2.120 and 11.635 <= c.y <= 11.900:
            if abs(n.x) > 0.5 or (n.y > 0.5 and c.y < 11.850):
                f.material_index = idx_koupelna

    uv_layer = bm.loops.layers.uv.verify()
    assign_uvs(bm, uv_layer)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ext.data)
    bm.free()
    ext.data.update()
    print("  Exterior_Walls completed!")

def update_interior_walls_tiles():
    print("[2] Updating Interior_Walls with sokliky, WC half-tile, and Bathroom full cladding...")
    int_obj = bpy.data.objects.get("Interior_Walls")
    if not int_obj:
        print("  ERROR: Interior_Walls not found!")
        return

    mat_int = bpy.data.materials.get("Mat_Interior_Wall")
    mat_koupelna = bpy.data.materials.get("koupelna stena")
    mat_plank = bpy.data.materials.get("Plank stena.001")

    int_obj.data.materials.clear()
    int_obj.data.materials.append(mat_int)
    int_obj.data.materials.append(mat_koupelna)
    int_obj.data.materials.append(mat_plank)

    idx_int = 0
    idx_koupelna = 1
    idx_plank = 2

    bm = bmesh.new()
    bm.from_mesh(int_obj.data)

    # 1. Horizontal cuts at Z = 0.150 and Z = 1.150
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.150), plane_no=(0, 0, 1))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 1.150), plane_no=(0, 0, 1))

    # 2. Vertical cut on Bathroom South wall at X = 1.368 (Shower boundary)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(1.368, 0, 0), plane_no=(1, 0, 0))

    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Default all faces to idx_int
    for f in bm.faces:
        f.material_index = idx_int

    for f in bm.faces:
        c = f.calc_center_median()
        n = f.normal

        # -------------------------------------------------------------
        # 1. ROOM 1.01 ZÁDVEŘÍ (X in [3.775, 6.100], Y in [0.365, 2.350])
        # -------------------------------------------------------------
        # West wall (X = 3.775, normal +X)
        if abs(n.x - 1.0) < 0.1 and abs(c.x - 3.775) < 0.05 and 0.365 <= c.y <= 2.350:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # East wall (X = 6.100, normal -X)
        elif abs(n.x - (-1.0)) < 0.1 and abs(c.x - 6.100) < 0.05 and 0.365 <= c.y <= 2.350:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # North wall (Y = 2.350, normal -Y)
        elif abs(n.y - (-1.0)) < 0.1 and abs(c.y - 2.350) < 0.05 and 3.775 <= c.x <= 6.100:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # -------------------------------------------------------------
        # 2. ROOM 1.08 WC (X in [0.365, 1.750], Y in [7.100, 8.1625])
        # All walls tiled up to Z = 1.150m
        # -------------------------------------------------------------
        # South wall (Y = 7.100, normal +Y)
        elif abs(n.y - 1.0) < 0.1 and abs(c.y - 7.100) < 0.05 and 0.365 <= c.x <= 1.750:
            if c.z < 1.150:
                f.material_index = idx_koupelna

        # North wall (Y = 8.1625, normal -Y)
        elif abs(n.y - (-1.0)) < 0.1 and abs(c.y - 8.1625) < 0.05 and 0.365 <= c.x <= 1.750:
            if c.z < 1.150:
                f.material_index = idx_koupelna

        # East wall (X = 1.750, normal -X)
        elif abs(n.x - (-1.0)) < 0.1 and abs(c.x - 1.750) < 0.05 and 7.100 <= c.y <= 8.1625:
            if c.z < 1.150:
                f.material_index = idx_koupelna

        # -------------------------------------------------------------
        # 3. ROOM 1.09 TECH (X in [0.365, 1.750], Y in [8.1625, 9.775])
        # Soklik at Z < 0.150m
        # -------------------------------------------------------------
        # South wall (Y = 8.2875, normal +Y)
        elif abs(n.y - 1.0) < 0.1 and abs(c.y - 8.2875) < 0.05 and 0.365 <= c.x <= 1.750:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # North wall (Y = 9.775, normal -Y)
        elif abs(n.y - (-1.0)) < 0.1 and abs(c.y - 9.775) < 0.05 and 0.365 <= c.x <= 1.750:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # East wall (X = 1.750, normal -X)
        elif abs(n.x - (-1.0)) < 0.1 and abs(c.x - 1.750) < 0.05 and 8.1625 <= c.y <= 9.775:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # -------------------------------------------------------------
        # 4. ROOM 1.11 CHODBA (X in [1.875, 2.875], Y in [7.100, 9.775])
        # Soklik at Z < 0.150m
        # -------------------------------------------------------------
        # West wall (X = 1.875, normal +X)
        elif abs(n.x - 1.0) < 0.1 and abs(c.x - 1.875) < 0.05 and 7.100 <= c.y <= 9.775:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # East wall (X = 2.875, normal -X)
        elif abs(n.x - (-1.0)) < 0.1 and abs(c.x - 2.875) < 0.05 and 7.100 <= c.y <= 9.775:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # South wall (Y = 7.100, normal +Y)
        elif abs(n.y - 1.0) < 0.1 and abs(c.y - 7.100) < 0.05 and 1.875 <= c.x <= 2.875:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # North wall (Y = 9.775, normal -Y outside door)
        elif abs(n.y - (-1.0)) < 0.1 and abs(c.y - 9.775) < 0.05 and 1.875 <= c.x <= 2.875:
            if c.z < 0.150:
                f.material_index = idx_koupelna

        # -------------------------------------------------------------
        # 5. ROOM 1.10 BATHROOM (X in [0.365, 2.875], Y in [9.900, 11.635])
        # Full height cladding up to Z = 2.500m!
        # -------------------------------------------------------------
        # South wall (Y = 9.900, normal +Y):
        elif abs(n.y - 1.0) < 0.1 and abs(c.y - 9.900) < 0.05 and 0.365 <= c.x <= 2.875:
            # Shower area opposite wood floor (X in [0.365, 1.368]): Plank stena.001!
            if c.x < 1.368:
                f.material_index = idx_plank
            # Rest of south wall (wall next to shower, door jambs, lintel): koupelna stena!
            else:
                f.material_index = idx_koupelna

        # East wall (X = 2.875, normal -X):
        # Separates bathroom from room 1.03 (hneda dlazba) -> whole wall is grey tile!
        elif abs(n.x - (-1.0)) < 0.1 and abs(c.x - 2.875) < 0.05 and 9.900 <= c.y <= 11.635:
            f.material_index = idx_koupelna

    uv_layer = bm.loops.layers.uv.verify()
    assign_uvs(bm, uv_layer)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(int_obj.data)
    bm.free()
    int_obj.data.update()
    print("  Interior_Walls completed!")

def render_verification():
    print("[3] Rendering verification views...")
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    cam = bpy.data.objects.get("Isometric_Camera")
    if not cam:
        return

    orig_loc = cam.location.copy()
    orig_rot = cam.rotation_euler.copy()
    orig_scale = cam.data.ortho_scale if hasattr(cam.data, 'ortho_scale') else 18.0
    orig_type = cam.data.type

    base_dir = r"C:\Users\Vaso\Antigravity\Project blender"

    # View 1: Bathroom closeup from above
    cam.data.type = 'PERSP'
    cam.data.lens = 32
    cam.location = Vector((3.8, 8.8, 3.8))
    tgt = Vector((1.6, 10.7, 1.0))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "bathroom_closeup.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered bathroom_closeup.png")

    # View 2: Bathroom south wall / shower
    cam.location = Vector((0.6, 12.6, 3.2))
    tgt = Vector((1.6, 10.0, 1.0))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "bathroom_south_wall.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered bathroom_south_wall.png")

    # View 3: WC inspection view
    cam.location = Vector((3.2, 6.2, 2.6))
    tgt = Vector((1.1, 7.6, 0.8))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "inspect_wc_tiles.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered inspect_wc_tiles.png")

    # View 4: Zadveri sokliky view
    cam.location = Vector((3.5, 4.5, 2.5))
    tgt = Vector((4.8, 1.4, 0.5))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "inspect_zadveri_sokliky.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered inspect_zadveri_sokliky.png")

    # View 5: Chodba 1.11 / Tech sokliky view
    cam.location = Vector((4.5, 8.5, 2.8))
    tgt = Vector((2.2, 8.5, 0.8))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "inspect_corridor_sokliky.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered inspect_corridor_sokliky.png")

    # View 6: Full Overview (ORTHO)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 18.0
    target = Vector((5.0, 6.0, 1.25))
    distance = 35.0
    iso_dir = Vector((-1.0, -1.0, math.sqrt(2))).normalized()
    cam.location = target + iso_dir * distance
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "dum_pudorys_overview.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered dum_pudorys_overview.png")

    # Restore camera
    cam.data.type = orig_type
    cam.location = orig_loc
    cam.rotation_euler = orig_rot
    if hasattr(cam.data, 'ortho_scale'):
        cam.data.ortho_scale = orig_scale

def main():
    print("=" * 70)
    print("APPLYING SOKLIKY, WC HALF-TILES, AND BATHROOM FULL CLADDING")
    print("=" * 70)

    update_exterior_walls_tiles()
    update_interior_walls_tiles()

    base_dir = r"C:\Users\Vaso\Antigravity\Project blender"
    out_path = os.path.join(base_dir, "dum_pudorys.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print(f"\n[SUCCESS] Saved updated dum_pudorys.blend to: {out_path}")

    render_verification()
    print("=" * 70)
    print("ALL REQUESTED TILING AND SOKLIKY COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
