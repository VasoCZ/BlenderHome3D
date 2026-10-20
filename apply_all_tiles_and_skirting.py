import bpy
import bmesh
from mathutils import Vector
import shutil
import os

print("=" * 70)
print("COMPREHENSIVE TILING & SKIRTING SCRIPT STARTING")
print("=" * 70)

# 1. Restore from clean backup dum_pudorys_before_tiling.blend
base_dir = r"C:\Users\Vaso\Antigravity\Project blender"
backup_path = os.path.join(base_dir, "dum_pudorys_before_tiling.blend")
target_path = os.path.join(base_dir, "dum_pudorys.blend")

if os.path.exists(backup_path):
    print(f"Restoring clean geometry from {backup_path}...")
    shutil.copy2(backup_path, target_path)
    bpy.ops.wm.open_mainfile(filepath=target_path)
else:
    print(f"Working on current file: {target_path}")

# 2. Ensure materials exist and have accurate object-aligned mapping
zaloha_path = os.path.join(base_dir, "dum_pudorys_zaloha1.blend")
for mname in ["sokl chodba", "sokl chodba.001"]:
    if mname not in bpy.data.materials:
        print(f"Importing {mname} from {zaloha_path}...")
        with bpy.data.libraries.load(zaloha_path) as (df, dt):
            dt.materials = [mname]

mat_sokl_x = bpy.data.materials.get("sokl chodba")
mat_sokl_y = bpy.data.materials.get("sokl chodba.001")
mat_koupelna = bpy.data.materials.get("koupelna")
mat_plank_stena = bpy.data.materials.get("Plank stena.001")
mat_ext_wall = bpy.data.materials.get("Mat_Exterior_Wall")
mat_int_wall = bpy.data.materials.get("Mat_Interior_Wall")

assert mat_sokl_x, "Material 'sokl chodba' not found!"
assert mat_sokl_y, "Material 'sokl chodba.001' not found!"
assert mat_koupelna, "Material 'koupelna' not found!"
assert mat_plank_stena, "Material 'Plank stena.001' not found!"

# Verify shader nodes for sokl chodba and sokl chodba.001
for m, expected_rot in [(mat_sokl_x, (0.0, 1.570796, 0.0)), (mat_sokl_y, (1.570796, 0.0, 0.0))]:
    mapping = [n for n in m.node_tree.nodes if n.type == 'MAPPING'][0]
    mapping.inputs['Location'].default_value = (0.20, -0.18, 0.0)
    mapping.inputs['Rotation'].default_value = expected_rot
    mapping.inputs['Scale'].default_value = (0.85, 0.85, 0.85)
    tex_coord = [n for n in m.node_tree.nodes if n.type == 'TEX_COORD'][0]
    m.node_tree.links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Verify shader nodes for koupelna (floor tiles)
k_mapping = [n for n in mat_koupelna.node_tree.nodes if n.type == 'MAPPING'][0]
k_mapping.inputs['Location'].default_value = (0.20, -0.18, 0.0)
k_mapping.inputs['Rotation'].default_value = (0.0, 0.0, 0.0)
k_mapping.inputs['Scale'].default_value = (0.85, 0.85, 1.0)
k_tex_coord = [n for n in mat_koupelna.node_tree.nodes if n.type == 'TEX_COORD'][0]
mat_koupelna.node_tree.links.new(k_tex_coord.outputs['Object'], k_mapping.inputs['Vector'])

def ensure_material_in_obj(obj, mat):
    for i, m in enumerate(obj.data.materials):
        if m == mat:
            return i
    obj.data.materials.append(mat)
    return len(obj.data.materials) - 1

# ======================================================================
# PROCESS EXTERIOR WALLS
# ======================================================================
def process_exterior_walls():
    print("\n--- Processing Exterior_Walls ---")
    obj = bpy.data.objects.get("Exterior_Walls")
    if not obj:
        print("Exterior_Walls not found!")
        return

    idx_sokl_x = ensure_material_in_obj(obj, mat_sokl_x)
    idx_sokl_y = ensure_material_in_obj(obj, mat_sokl_y)
    idx_koupelna = ensure_material_in_obj(obj, mat_koupelna)
    idx_plank = ensure_material_in_obj(obj, mat_plank_stena)
    idx_ext = ensure_material_in_obj(obj, mat_ext_wall)

    def get_tile_idx(norm):
        if abs(norm.x) > abs(norm.y) and abs(norm.x) > abs(norm.z):
            return idx_sokl_x
        elif abs(norm.y) > abs(norm.x) and abs(norm.y) > abs(norm.z):
            return idx_sokl_y
        else:
            return idx_koupelna

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Horizontal cuts
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                           plane_co=Vector((0, 0, 0.150)), plane_no=Vector((0, 0, 1)),
                           clear_inner=False, clear_outer=False)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                           plane_co=Vector((0, 0, 1.150)), plane_no=Vector((0, 0, 1)),
                           clear_inner=False, clear_outer=False)

    # Vertical cuts
    for y_cut in [7.100, 8.1625, 8.2875, 9.775, 9.900, 10.890]:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((0, y_cut, 0)), plane_no=Vector((0, 1, 0)),
                               clear_inner=False, clear_outer=False)

    for x_cut in [0.365, 2.875, 3.775, 6.100]:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((x_cut, 0, 0)), plane_no=Vector((1, 0, 0)),
                               clear_inner=False, clear_outer=False)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    uv_lay = bm.loops.layers.uv.verify()
    assigned_counts = {}

    for f in bm.faces:
        cx = sum(v.co.x for v in f.verts) / len(f.verts)
        cy = sum(v.co.y for v in f.verts) / len(f.verts)
        cz = sum(v.co.z for v in f.verts) / len(f.verts)
        norm = f.normal

        # Skip horizontal surfaces that are ceiling (Z=2.50) or floor bottom (Z=0.00)
        if abs(norm.z) > 0.8 and (cz > 2.45 or cz < 0.05):
            continue

        new_mat_idx = None

        # 1. Bathroom (Room 1.10) Exterior Walls:
        # West exterior wall facing east (norm.x > 0.7, cx ~ 0.365, Y in [9.900, 11.635])
        if abs(cx - 0.365) < 0.05 and norm.x > 0.7 and (9.900 - 0.02 <= cy <= 11.635 + 0.02):
            if cy <= 10.890 + 0.01:
                # Shower west wall -> wood planks full height
                new_mat_idx = idx_plank
            else:
                # West wall north of shower -> grey tile full height (aligned with floor)
                new_mat_idx = get_tile_idx(norm)

        # North exterior wall facing south (norm.y < -0.7, cy ~ 11.635, X in [0.365, 2.875])
        elif abs(cy - 11.635) < 0.05 and norm.y < -0.7 and (0.365 - 0.02 <= cx <= 2.875 + 0.02):
            new_mat_idx = get_tile_idx(norm)

        # Window reveals in bathroom north wall: X in [1.12, 2.12], Y in [11.635, 12.00]
        elif (1.10 <= cx <= 2.14) and (11.635 <= cy <= 12.02) and (norm.y < -0.2 or abs(norm.x) > 0.7 or (abs(norm.z) > 0.7 and cz < 2.45)):
            new_mat_idx = get_tile_idx(norm)

        # 2. WC (Room 1.08) Exterior Wall:
        # West exterior wall facing east (norm.x > 0.7, cx ~ 0.365, Y in [7.100, 8.1625])
        elif abs(cx - 0.365) < 0.05 and norm.x > 0.7 and (7.100 - 0.02 <= cy <= 8.1625 + 0.02):
            if cz <= 1.150:
                new_mat_idx = get_tile_idx(norm)
            else:
                new_mat_idx = idx_ext

        # 3. Tech (Room 1.09) Exterior Wall:
        # West exterior wall facing east (norm.x > 0.7, cx ~ 0.365, Y in [8.2875, 9.775])
        elif abs(cx - 0.365) < 0.05 and norm.x > 0.7 and (8.2875 - 0.02 <= cy <= 9.775 + 0.02):
            if cz <= 0.150:
                new_mat_idx = get_tile_idx(norm)
            else:
                new_mat_idx = idx_ext

        # 4. Zadveri (Room 1.01) Exterior Wall:
        # South exterior wall facing north (norm.y > 0.7, cy ~ 0.365, X in [3.775, 6.100])
        elif abs(cy - 0.365) < 0.05 and norm.y > 0.7 and (3.775 - 0.02 <= cx <= 6.100 + 0.02):
            if cz <= 0.150:
                new_mat_idx = get_tile_idx(norm)
            else:
                new_mat_idx = idx_ext

        if new_mat_idx is not None:
            f.material_index = new_mat_idx
            mname = obj.data.materials[new_mat_idx].name
            assigned_counts[mname] = assigned_counts.get(mname, 0) + 1

            # Set planar UVs for wood plank cladding in shower
            if new_mat_idx == idx_plank:
                for l in f.loops:
                    vco = l.vert.co
                    if abs(norm.y) > abs(norm.x) and abs(norm.y) > abs(norm.z):
                        l[uv_lay].uv = Vector((vco.x, vco.z))
                    elif abs(norm.x) > abs(norm.y) and abs(norm.x) > abs(norm.z):
                        l[uv_lay].uv = Vector((vco.y, vco.z))
                    else:
                        l[uv_lay].uv = Vector((vco.x, vco.y))

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    print("Exterior_Walls assignments:", assigned_counts)

# ======================================================================
# PROCESS INTERIOR WALLS
# ======================================================================
def process_interior_walls():
    print("\n--- Processing Interior_Walls ---")
    obj = bpy.data.objects.get("Interior_Walls")
    if not obj:
        print("Interior_Walls not found!")
        return

    idx_sokl_x = ensure_material_in_obj(obj, mat_sokl_x)
    idx_sokl_y = ensure_material_in_obj(obj, mat_sokl_y)
    idx_koupelna = ensure_material_in_obj(obj, mat_koupelna)
    idx_plank = ensure_material_in_obj(obj, mat_plank_stena)
    idx_int = ensure_material_in_obj(obj, mat_int_wall)

    def get_tile_idx(norm):
        if abs(norm.x) > abs(norm.y) and abs(norm.x) > abs(norm.z):
            return idx_sokl_x
        elif abs(norm.y) > abs(norm.x) and abs(norm.y) > abs(norm.z):
            return idx_sokl_y
        else:
            return idx_koupelna

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Horizontal cuts
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                           plane_co=Vector((0, 0, 0.150)), plane_no=Vector((0, 0, 1)),
                           clear_inner=False, clear_outer=False)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                           plane_co=Vector((0, 0, 1.150)), plane_no=Vector((0, 0, 1)),
                           clear_inner=False, clear_outer=False)

    # Vertical cuts
    for y_cut in [2.350, 7.100, 8.1625, 8.2875, 9.775, 9.900, 10.890]:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((0, y_cut, 0)), plane_no=Vector((0, 1, 0)),
                               clear_inner=False, clear_outer=False)

    for x_cut in [1.368, 1.750, 1.875, 2.875, 3.775, 6.100]:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector((x_cut, 0, 0)), plane_no=Vector((1, 0, 0)),
                               clear_inner=False, clear_outer=False)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    uv_lay = bm.loops.layers.uv.verify()
    assigned_counts = {}

    for f in bm.faces:
        cx = sum(v.co.x for v in f.verts) / len(f.verts)
        cy = sum(v.co.y for v in f.verts) / len(f.verts)
        cz = sum(v.co.z for v in f.verts) / len(f.verts)
        norm = f.normal

        # Skip horizontal surfaces that are ceiling (Z=2.50) or floor bottom (Z=0.00)
        if abs(norm.z) > 0.8 and (cz > 2.45 or cz < 0.05):
            continue

        new_mat_idx = None

        # --------------------------------------------------------------
        # 1. ROOM 1.10 KOUPELNA (Bathroom)
        # --------------------------------------------------------------
        # South wall of bathroom (facing North, norm.y > 0.7, Y ~ 9.900, X in [0.365, 2.875])
        if abs(cy - 9.900) < 0.08 and norm.y > 0.7 and (0.35 <= cx <= 2.90):
            if cx <= 1.368 + 0.01:
                # Shower south wall -> wood plank full height
                new_mat_idx = idx_plank
            else:
                # Rest of south wall -> grey tile full height (aligned with floor)
                new_mat_idx = get_tile_idx(norm)

        # East wall of bathroom (facing West, norm.x < -0.7, X ~ 2.875, Y in [9.900, 11.635])
        elif abs(cx - 2.875) < 0.08 and norm.x < -0.7 and (9.900 - 0.02 <= cy <= 11.65):
            new_mat_idx = get_tile_idx(norm)

        # Door opening into bathroom (jambs and lintel around X in [2.05, 2.75], Y ~ 9.900)
        elif (2.00 <= cx <= 2.80) and (9.75 <= cy <= 9.95) and (abs(norm.x) > 0.7 or norm.z < -0.7):
            new_mat_idx = get_tile_idx(norm)

        # --------------------------------------------------------------
        # 2. ROOM 1.08 WC (Záchod) - Half-height grey tile (Z <= 1.150)
        # Bounds: X in [0.365, 1.750], Y in [7.100, 8.1625]
        # --------------------------------------------------------------
        # South wall facing North into WC (norm.y > 0.7, cy ~ 7.100, X in [0.365, 1.750])
        elif abs(cy - 7.100) < 0.08 and norm.y > 0.7 and (0.35 <= cx <= 1.76):
            new_mat_idx = get_tile_idx(norm) if cz <= 1.150 else idx_int

        # North wall facing South into WC (norm.y < -0.7, cy ~ 8.1625, X in [0.365, 1.750])
        elif abs(cy - 8.1625) < 0.08 and norm.y < -0.7 and (0.35 <= cx <= 1.76):
            new_mat_idx = get_tile_idx(norm) if cz <= 1.150 else idx_int

        # East wall facing West into WC (norm.x < -0.7, cx ~ 1.750, Y in [7.100, 8.1625])
        elif abs(cx - 1.750) < 0.08 and norm.x < -0.7 and (7.100 - 0.02 <= cy <= 8.1625 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 1.150 else idx_int

        # WC door jambs (at X ~ 1.750, Y ~ 7.25-7.95)
        elif abs(cx - 1.750) < 0.08 and (7.20 <= cy <= 8.00) and abs(norm.y) > 0.7:
            new_mat_idx = get_tile_idx(norm) if cz <= 1.150 else idx_int

        # --------------------------------------------------------------
        # 3. ROOM 1.09 TECHNICKÁ MÍSTNOST - 15cm Soklík (Z <= 0.150)
        # Bounds: X in [0.365, 1.750], Y in [8.2875, 9.775]
        # --------------------------------------------------------------
        # South wall facing North into Tech (norm.y > 0.7, cy ~ 8.2875, X in [0.365, 1.750])
        elif abs(cy - 8.2875) < 0.08 and norm.y > 0.7 and (0.35 <= cx <= 1.76):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # North wall facing South into Tech (norm.y < -0.7, cy ~ 9.775, X in [0.365, 1.750])
        elif abs(cy - 9.775) < 0.08 and norm.y < -0.7 and (0.35 <= cx <= 1.76):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # East wall facing West into Tech (norm.x < -0.7, cx ~ 1.750, Y in [8.2875, 9.775])
        elif abs(cx - 1.750) < 0.08 and norm.x < -0.7 and (8.2875 - 0.02 <= cy <= 9.775 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # Tech door jambs
        elif abs(cx - 1.750) < 0.08 and (8.20 <= cy <= 9.70) and abs(norm.y) > 0.7:
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # --------------------------------------------------------------
        # 4. ROOM 1.11 CHODBA - 15cm Soklík (Z <= 0.150)
        # Bounds: X in [1.750, 2.875], Y in [7.100, 9.900]
        # --------------------------------------------------------------
        # South wall facing North into Chodba 1.11 (norm.y > 0.7, cy ~ 7.100, X in [1.750, 2.875])
        elif abs(cy - 7.100) < 0.08 and norm.y > 0.7 and (1.75 - 0.02 <= cx <= 2.875 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # East wall facing West into Chodba 1.11 (norm.x < -0.7, cx ~ 2.875, Y in [7.100, 9.900])
        elif abs(cx - 2.875) < 0.08 and norm.x < -0.7 and (7.100 - 0.02 <= cy <= 9.900 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # West wall facing East into Chodba 1.11 (norm.x > 0.7, cx ~ 1.75-1.88, Y in [7.100, 9.900])
        elif (1.70 <= cx <= 1.90) and norm.x > 0.7 and (7.100 - 0.02 <= cy <= 9.900 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # North wall facing South into Chodba 1.11 (norm.y < -0.7, cy ~ 9.775-9.900, X in [1.750, 2.875])
        elif (9.75 <= cy <= 9.95) and norm.y < -0.7 and (1.75 - 0.02 <= cx <= 2.875 + 0.02):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # --------------------------------------------------------------
        # 5. ROOM 1.01 ZÁDVEŘÍ - 15cm Soklík (Z <= 0.150)
        # Bounds: X in [3.775, 6.100], Y in [0.365, 2.350]
        # --------------------------------------------------------------
        # West wall facing East into Zádveří (norm.x > 0.7, cx ~ 3.775, Y in [0.365, 2.350])
        elif abs(cx - 3.775) < 0.08 and norm.x > 0.7 and (0.35 <= cy <= 2.45):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # East wall facing West into Zádveří (norm.x < -0.7, cx ~ 6.100, Y in [0.365, 2.350])
        elif abs(cx - 6.100) < 0.08 and norm.x < -0.7 and (0.35 <= cy <= 2.45):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # North wall facing South into Zádveří (norm.y < -0.7, cy ~ 2.350, X in [3.775, 6.100])
        elif abs(cy - 2.350) < 0.08 and norm.y < -0.7 and (3.75 <= cx <= 6.15):
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        # Door jambs in Zádveří north door (X ~ 4.70 to 5.50, Y ~ 2.35 to 2.47)
        elif (4.60 <= cx <= 5.60) and (2.30 <= cy <= 2.50) and abs(norm.x) > 0.7:
            new_mat_idx = get_tile_idx(norm) if cz <= 0.150 else idx_int

        if new_mat_idx is not None:
            f.material_index = new_mat_idx
            mname = obj.data.materials[new_mat_idx].name
            assigned_counts[mname] = assigned_counts.get(mname, 0) + 1

            # Set planar UVs for wood plank cladding in shower
            if new_mat_idx == idx_plank:
                for l in f.loops:
                    vco = l.vert.co
                    if abs(norm.y) > abs(norm.x) and abs(norm.y) > abs(norm.z):
                        l[uv_lay].uv = Vector((vco.x, vco.z))
                    elif abs(norm.x) > abs(norm.y) and abs(norm.x) > abs(norm.z):
                        l[uv_lay].uv = Vector((vco.y, vco.z))
                    else:
                        l[uv_lay].uv = Vector((vco.x, vco.y))

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    print("Interior_Walls assignments:", assigned_counts)

# ======================================================================
# FIX FLOOR GEOMETRIES, THRESHOLDS & PATIO SLAB
# ======================================================================
def fix_floor_geometry():
    print("\n--- Fixing Floor Geometries, Thresholds & Patio Slab ---")
    
    # 1. WC floor gap fix
    wc_floor = bpy.data.objects.get("Floor_1.08_WC")
    if wc_floor:
        for v in wc_floor.data.vertices:
            if abs(v.co.y - 8.1000) < 0.01:
                v.co.y = 8.1625
        wc_floor.data.update()
        print("Floor_1.08_WC north edge extended to Y=8.1625")

    tech_floor = bpy.data.objects.get("Floor_1.09_Technicka_mistnost")
    if tech_floor:
        for v in tech_floor.data.vertices:
            if abs(v.co.y - 8.2250) < 0.01:
                v.co.y = 8.2875
        tech_floor.data.update()
        print("Floor_1.09_Technicka_mistnost south edge aligned to Y=8.2875")

    # 2. Rebuild thresholds as solid single-material boxes with ONLY koupelna
    def make_solid_threshold(obj_name, x_min, x_max, y_min, y_max, z_min=0.000, z_max=0.015):
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            mesh = bpy.data.meshes.new(obj_name)
            obj = bpy.data.objects.new(obj_name, mesh)
            bpy.context.scene.collection.objects.link(obj)
        mesh = obj.data
        bm = bmesh.new()
        v0 = bm.verts.new((x_min, y_min, z_min))
        v1 = bm.verts.new((x_max, y_min, z_min))
        v2 = bm.verts.new((x_max, y_max, z_min))
        v3 = bm.verts.new((x_min, y_max, z_min))
        v4 = bm.verts.new((x_min, y_min, z_max))
        v5 = bm.verts.new((x_max, y_min, z_max))
        v6 = bm.verts.new((x_max, y_max, z_max))
        v7 = bm.verts.new((x_min, y_max, z_max))
        bm.faces.new([v0, v3, v2, v1])
        bm.faces.new([v4, v5, v6, v7])
        bm.faces.new([v0, v1, v5, v4])
        bm.faces.new([v1, v2, v6, v5])
        bm.faces.new([v2, v3, v7, v6])
        bm.faces.new([v3, v0, v4, v7])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        obj.data.materials.clear()
        obj.data.materials.append(mat_koupelna)
        print(f"Rebuilt solid threshold {obj_name} with ONLY koupelna material.")

    make_solid_threshold("Floor_Threshold_104_111", 2.875, 3.000, 7.200, 8.000)
    make_solid_threshold("Floor_Threshold_101_102", 4.700, 5.500, 2.350, 2.475)

    # 3. Assign koupelna material to all grey-tiled floors
    for fl_name in ["Floor_1.08_WC", "Floor_1.09_Technicka_mistnost", "Floor_1.11_Chodba", "Floor_1.01_Zadveri",
                    "Floor_Threshold_111_108", "Floor_Threshold_111_109", "Floor_Threshold_111_110", "Floor_Threshold_Front_Entrance"]:
        fl = bpy.data.objects.get(fl_name)
        if fl:
            fl.data.materials.clear()
            fl.data.materials.append(mat_koupelna)

    # 4. Foundation_Slab under patio door track (lower to Z=-0.070 to prevent zamkovka clipping)
    slab = bpy.data.objects.get("Foundation_Slab")
    if slab:
        bm = bmesh.new()
        bm.from_mesh(slab.data)
        for x in [7.125, 8.925]:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                   plane_co=Vector((x, 0, 0)), plane_no=Vector((1, 0, 0)),
                                   clear_inner=False, clear_outer=False)
        for y in [11.635, 11.850]:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                   plane_co=Vector((0, y, 0)), plane_no=Vector((0, 1, 0)),
                                   clear_inner=False, clear_outer=False)
        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            if 7.124 <= v.co.x <= 8.926 and 11.634 <= v.co.y <= 11.851:
                if v.co.z >= -0.001:
                    v.co.z = -0.070
        bm.to_mesh(slab.data)
        bm.free()
        slab.data.update()
        print("Lowered Foundation_Slab under patio door track to Z=-0.070.")

# Execute operations
process_exterior_walls()
process_interior_walls()
fix_floor_geometry()

# Save updated blend file
bpy.ops.wm.save_mainfile(filepath=target_path)
print(f"\n[SUCCESS] Successfully saved {target_path}")

# ======================================================================
# RENDERING CAMERA VIEWS FOR VERIFICATION
# ======================================================================
print("\n--- Setting up verification cameras and rendering ---")

def setup_camera_lookat(name, loc, target, focal_length=20):
    cam = bpy.data.objects.get(name)
    if not cam:
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = focal_length
    cam.data.clip_start = 0.05
    return cam

views = [
    # 1. Bathroom full interior view (looking from entrance towards window and shower)
    ("bathroom_full_view.png", (2.40, 9.80, 2.20), (1.30, 10.80, 1.10), 20),
    # 2. Bathroom shower corner view (showing wood plank walls on west & south next to wood floor)
    ("bathroom_shower_view.png", (2.30, 10.30, 1.60), (0.85, 10.40, 0.60), 19),
    # 3. Bathroom east wall view (verifying the east wall grout lines continue from the floor)
    ("bathroom_east_wall_view.png", (0.80, 10.20, 1.60), (2.875, 10.80, 0.90), 22),
    # 3b. Bathroom north wall top cap view (verifying the top of the wall at Z=2.50 is clean white plaster)
    ("bathroom_wall_top_view.png", (1.62, 8.80, 3.80), (1.62, 11.80, 2.30), 22),
    # 4. WC interior view (looking inside Room 1.08 showing half-height tiles & grout alignment)
    ("wc_interior_view.png", (1.45, 7.30, 1.45), (0.365, 7.90, 0.50), 18),
    # 5. Tech room interior view (showing 15cm soklik)
    ("tech_interior_view.png", (1.45, 8.40, 1.40), (0.365, 9.40, 0.60), 18),
    # 5b. Tech room south wall view (specifically showing south wall 15cm soklik)
    ("tech_south_wall_view.png", (1.05, 9.55, 1.30), (1.05, 8.288, 0.20), 18),
    # 6. Corridor 1.11 and Tech room view (showing 15cm sokliky)
    ("corridor_tech_soklik_view.png", (2.35, 7.30, 1.80), (2.35, 9.90, 1.20), 22),
    # 7. Zadveri view (showing 15cm sokliky)
    ("zadveri_soklik_view.png", (5.70, 0.70, 1.40), (3.775, 2.00, 0.50), 20),
    # 8. Threshold 104_111 view (grey tile only, transition between kitchen 1.03 and hallway 1.11)
    ("threshold_104_111_view.png", (2.30, 7.60, 1.40), (3.20, 7.60, 0.00), 24),
    # 9. Threshold 101_102 view (grey tile only, transition between zadveri 1.01 and corridor 1.02)
    ("threshold_101_102_view.png", (5.10, 1.60, 1.40), (5.10, 2.80, 0.00), 24),
    # 10. Patio threshold view (no zamkovka under track, clean threshold)
    ("patio_threshold_view.png", (8.00, 11.20, 0.50), (8.00, 11.75, 0.00), 28),
    # 11. Floorplan overview
    ("dum_pudorys_overview.png", None, None, None),
]

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'

iso_cam = bpy.data.objects.get("Isometric_Camera")

for filename, loc, target, focal in views:
    out_file = os.path.join(base_dir, filename)
    if loc is None:
        if iso_cam:
            scene.camera = iso_cam
    else:
        cam_obj = setup_camera_lookat("Temp_Render_Cam", loc, target, focal)
        scene.camera = cam_obj

    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {filename}")

print("\n" + "=" * 70)
print("ALL TASKS COMPLETED SUCCESSFULLY!")
print("=" * 70)
