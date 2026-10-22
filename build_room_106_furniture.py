import bpy
import bmesh
import math
import mathutils

def run():
    print("=== BUILDING FINAL PRODUCTION ROOM 1.06 FURNITURE ===")

    # ---------------------------------------------------------
    # 1. MATERIALS SETUP
    # ---------------------------------------------------------
    def get_or_create_material(name, base_color=(0.8, 0.8, 0.8, 1.0), roughness=0.4, metallic=0.0):
        mat = bpy.data.materials.get(name)
        if mat:
            return mat
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = base_color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
        return mat

    mat_oak = bpy.data.materials.get("Mat_Kronospan_K003_Gold_Craft_Oak")
    if not mat_oak:
        raise RuntimeError("Mat_Kronospan_K003_Gold_Craft_Oak not found!")

    mat_white_chair = get_or_create_material("Mat_Plastic_White_Matte", base_color=(0.94, 0.94, 0.93, 1.0), roughness=0.30, metallic=0.0)
    mat_cabinet_grey = get_or_create_material("Mat_Cabinet_Light_Grey", base_color=(0.54, 0.54, 0.51, 1.0), roughness=0.38, metallic=0.0)
    mat_chrome = bpy.data.materials.get("Mat_Kitchen_Chrome") or get_or_create_material("Mat_Silver_Metal", base_color=(0.88, 0.88, 0.90, 1.0), roughness=0.15, metallic=0.98)
    mat_dark_plastic = get_or_create_material("Mat_Plastic_Dark_Grey", base_color=(0.14, 0.14, 0.15, 1.0), roughness=0.5, metallic=0.0)

    # Box fabrics
    mat_fabric_anthracite = get_or_create_material("Mat_Fabric_Anthracite", base_color=(0.14, 0.14, 0.15, 1.0), roughness=0.92, metallic=0.0)
    mat_fabric_light_grey = get_or_create_material("Mat_Fabric_Light_Grey", base_color=(0.70, 0.70, 0.68, 1.0), roughness=0.90, metallic=0.0)
    mat_fabric_green = get_or_create_material("Mat_Fabric_Green", base_color=(0.28, 0.68, 0.16, 1.0), roughness=0.88, metallic=0.0)
    mat_fabric_pattern = get_or_create_material("Mat_Fabric_Bin_Pattern", base_color=(0.84, 0.82, 0.78, 1.0), roughness=0.92, metallic=0.0)

    # Toys & details
    mat_toy_red = get_or_create_material("Mat_Toy_Red", base_color=(0.85, 0.10, 0.10, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_blue = get_or_create_material("Mat_Toy_Blue", base_color=(0.10, 0.38, 0.88, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_yellow = get_or_create_material("Mat_Toy_Yellow", base_color=(0.95, 0.82, 0.10, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_purple = get_or_create_material("Mat_Toy_Purple", base_color=(0.58, 0.22, 0.72, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_green_lego = get_or_create_material("Mat_Lego_Dark_Green", base_color=(0.08, 0.40, 0.12, 1.0), roughness=0.35, metallic=0.0)

    # Collection setup
    col_name = "Room_1.06_Furniture"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    def add_obj_to_collection(obj):
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)

    def add_cylinder(bm, radius, depth, segments=16, matrix=mathutils.Matrix.Identity(4)):
        return bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, radius1=radius, radius2=radius,
            depth=depth, segments=segments, matrix=matrix
        )

    def add_box(bm, min_pt, max_pt):
        x0, y0, z0 = min_pt
        x1, y1, z1 = max_pt
        v = [
            bm.verts.new((x0, y0, z0)),
            bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)),
            bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)),
            bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)),
            bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]]) # -Z
        bm.faces.new([v[4], v[7], v[6], v[5]]) # +Z
        bm.faces.new([v[0], v[4], v[5], v[1]]) # -Y
        bm.faces.new([v[2], v[6], v[7], v[3]]) # +Y
        bm.faces.new([v[0], v[3], v[7], v[4]]) # -X
        bm.faces.new([v[1], v[5], v[6], v[2]]) # +X

    def apply_bevel_and_uv(obj, bevel_width=0.002, uv_scale=1.0):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cube_project(cube_size=uv_scale, correct_aspect=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(40)
        bev.use_clamp_overlap = True
        obj.select_set(False)

    # ---------------------------------------------------------
    # 2. REMOVE OLD OBJECTS & PRIOR GENERATIONS
    # ---------------------------------------------------------
    old_kallax = bpy.data.objects.get("Ikea Kallax 147x147cm")
    if old_kallax:
        print("Removing old Kallax in room 1.06...")
        old_mesh = old_kallax.data
        bpy.data.objects.remove(old_kallax, do_unlink=True)
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)

    prior_names = [
        "Kallax_Stepped_1.06", "Box_Col1_Row2_Anthracite", "Box_Col2_Row2_Anthracite",
        "Box_Col3_Row2_Green", "Bin_Col1_Row1_Pattern", "Box_Col2_Row1_Grey",
        "Puzzle_Tile_1", "Puzzle_Tile_2", "Puzzle_Tile_3", "Puzzle_Tile_4",
        "Game_Box_The_Farm", "Game_Gravitrax", "Toy_Red_Box", "Lego_Baseplate_Green",
        "Toy_Truck_Step3", "Toy_Mini_Hockey_Step1",
        "Cabinet_Carcass_Mod_1", "Cabinet_Carcass_Mod_2", "Cabinet_Legs_Mod_1", "Cabinet_Legs_Mod_2",
        "Cabinet_Door_Mod_1", "Cabinet_Door_Mod_2", "Cabinet_Knob_Mod_1", "Cabinet_Knob_Mod_2",
        "Cabinet_Decor_Robot", "Desk_1.06", "Desk_Accessories_1.06", "Desk_Trash_Bin_1.06",
        "Chair_Lattice_1.06", "Chair_Lattice_Base", "Chair_Backrest_Curve",
        "Toy_Paw_Patrol_Tower", "Toy_Track_Segment"
    ]
    for p_name in prior_names:
        o = bpy.data.objects.get(p_name)
        if o:
            m = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if m and m.users == 0:
                if isinstance(m, bpy.types.Mesh):
                    bpy.data.meshes.remove(m)
                elif isinstance(m, bpy.types.Curve):
                    bpy.data.curves.remove(m)

    # ---------------------------------------------------------
    # 3. BUILD STEPPED KALLAX (4-3-2-1 CASCADING)
    # ---------------------------------------------------------
    print("Building Stepped Kallax...")
    k_mesh = bpy.data.meshes.new("Kallax_Stepped_1.06")
    k_bm = bmesh.new()

    x0 = 0.385
    depth = 0.390
    x1 = x0 + depth # 0.775
    y_start = 0.400
    
    t_out = 0.030 # outer board thickness (30mm)
    t_in = 0.016  # inner shelf thickness (16mm)
    cw = 0.336    # cube width
    ch = 0.336    # cube height
    z_floor = 0.015

    # 4 Columns:
    y_col0 = y_start
    y_col1 = y_col0 + t_out + cw # 0.766
    y_col2 = y_col1 + t_in + cw  # 1.118
    y_col3 = y_col2 + t_in + cw  # 1.470
    y_col4 = y_col3 + t_in + cw + t_out # 1.852

    # Bottom full-width base board:
    add_box(k_bm, (x0, y_col0, z_floor), (x1, y_col4, z_floor + t_out))

    # Outer vertical panels & dividers:
    z_top_col1 = z_floor + t_out + 4*ch + 3*t_in + t_out # ~ 1.467
    z_top_col2 = z_floor + t_out + 3*ch + 2*t_in + t_out # ~ 1.115
    z_top_col3 = z_floor + t_out + 2*ch + 1*t_in + t_out # ~ 0.763
    z_top_col4 = z_floor + t_out + 1*ch + t_out          # ~ 0.411

    # Col 1 Left outer:
    add_box(k_bm, (x0, y_col0, z_floor), (x1, y_col0 + t_out, z_top_col1))
    # Divider 1 (Col 1/2):
    add_box(k_bm, (x0, y_col1, z_floor + t_out), (x1, y_col1 + t_in, z_top_col1 - t_out))
    # Divider 2 (Col 2/3):
    add_box(k_bm, (x0, y_col2, z_floor + t_out), (x1, y_col2 + t_in, z_top_col2 - t_out))
    # Divider 3 (Col 3/4):
    add_box(k_bm, (x0, y_col3, z_floor + t_out), (x1, y_col3 + t_in, z_top_col3 - t_out))
    # Col 4 Right outer:
    add_box(k_bm, (x0, y_col4 - t_out, z_floor), (x1, y_col4, z_top_col4))

    # Outer stepped top panels:
    add_box(k_bm, (x0, y_col0, z_top_col1 - t_out), (x1, y_col1 + t_in, z_top_col1))
    add_box(k_bm, (x0, y_col1 + t_in, z_top_col2 - t_out), (x1, y_col2 + t_in, z_top_col2))
    add_box(k_bm, (x0, y_col2 + t_in, z_top_col3 - t_out), (x1, y_col3 + t_in, z_top_col3))
    add_box(k_bm, (x0, y_col3 + t_in, z_top_col4 - t_out), (x1, y_col4, z_top_col4))

    # Inner horizontal shelves:
    y_c1_min = y_col0 + t_out
    y_c1_max = y_col1
    for k in range(1, 4):
        z_sh = z_floor + t_out + k*(ch + t_in) - t_in
        add_box(k_bm, (x0, y_c1_min, z_sh), (x1, y_c1_max, z_sh + t_in))

    y_c2_min = y_col1 + t_in
    y_c2_max = y_col2
    for k in range(1, 3):
        z_sh = z_floor + t_out + k*(ch + t_in) - t_in
        add_box(k_bm, (x0, y_c2_min, z_sh), (x1, y_c2_max, z_sh + t_in))

    y_c3_min = y_col2 + t_in
    y_c3_max = y_col3
    z_sh = z_floor + t_out + 1*(ch + t_in) - t_in
    add_box(k_bm, (x0, y_c3_min, z_sh), (x1, y_c3_max, z_sh + t_in))

    k_bm.to_mesh(k_mesh)
    k_bm.free()

    k_obj = bpy.data.objects.new("Kallax_Stepped_1.06", k_mesh)
    add_obj_to_collection(k_obj)
    k_obj.data.materials.append(mat_oak)
    apply_bevel_and_uv(k_obj, bevel_width=0.002, uv_scale=1.0)

    # ---------------------------------------------------------
    # 4. KALLAX STORAGE BOXES & INSERTS
    # ---------------------------------------------------------
    print("Building Kallax inserts & boxes...")
    def create_insert_box(name, center_pt, size, mat, has_handle=True):
        b_mesh = bpy.data.meshes.new(name)
        b_bm = bmesh.new()
        sx, sy, sz = size
        cx, cy, cz = center_pt
        min_pt = (cx - sx/2, cy - sy/2, cz - sz/2)
        max_pt = (cx + sx/2, cy + sy/2, cz + sz/2)
        add_box(b_bm, min_pt, max_pt)

        if has_handle:
            hx0 = max_pt[0] + 0.001
            hx1 = max_pt[0] + 0.006
            hy0 = cy - 0.040
            hy1 = cy + 0.040
            hz0 = cz - 0.008
            hz1 = cz + 0.008
            add_box(b_bm, (hx0, hy0, hz0), (hx1, hy1, hz1))

        b_bm.to_mesh(b_mesh)
        b_bm.free()
        b_obj = bpy.data.objects.new(name, b_mesh)
        add_obj_to_collection(b_obj)
        b_obj.data.materials.append(mat)
        apply_bevel_and_uv(b_obj, bevel_width=0.003, uv_scale=0.5)
        return b_obj

    box_w = 0.320
    box_d = 0.370
    box_h = 0.320
    box_cx = x0 + depth/2 + 0.005

    cy_col1 = (y_c1_min + y_c1_max) / 2
    cy_col2 = (y_c2_min + y_c2_max) / 2
    cy_col3 = (y_c3_min + y_c3_max) / 2
    cy_col4 = (y_col3 + t_in + y_col4 - t_out) / 2

    z_r1 = 0.213
    z_r2 = 0.565
    z_r3 = 0.917
    z_r4 = 1.269

    # Insert Boxes:
    create_insert_box("Box_Col1_Row2_Anthracite", (box_cx, cy_col1, z_r2), (box_d, box_w, box_h), mat_fabric_anthracite)
    create_insert_box("Box_Col2_Row2_Anthracite", (box_cx, cy_col2, z_r2), (box_d, box_w, box_h), mat_fabric_anthracite)
    create_insert_box("Box_Col3_Row2_Green", (box_cx, cy_col3, z_r2), (box_d, box_w, box_h), mat_fabric_green)
    create_insert_box("Bin_Col1_Row1_Pattern", (box_cx, cy_col1, z_r1), (box_d, box_w, box_h), mat_fabric_pattern)
    create_insert_box("Box_Col2_Row1_Grey", (box_cx, cy_col2, z_r1), (box_d, box_w, box_h), mat_fabric_light_grey)

    # Stacked foam puzzle tiles in Col 3, Row 1
    puzzle_colors = [mat_toy_yellow, mat_toy_purple, mat_white_chair, mat_toy_blue]
    for idx, p_mat in enumerate(puzzle_colors):
        p_mesh = bpy.data.meshes.new(f"Puzzle_Tile_{idx+1}")
        p_bm = bmesh.new()
        pz0 = z_floor + t_out + idx * 0.024
        pz1 = pz0 + 0.020
        add_box(p_bm, (x0 + 0.03, cy_col3 - 0.14, pz0), (x1 - 0.03, cy_col3 + 0.14, pz1))
        p_bm.to_mesh(p_mesh)
        p_bm.free()
        p_obj = bpy.data.objects.new(f"Puzzle_Tile_{idx+1}", p_mesh)
        add_obj_to_collection(p_obj)
        p_obj.data.materials.append(p_mat)
        apply_bevel_and_uv(p_obj, bevel_width=0.002)

    # Board games on shelves
    create_insert_box("Game_Box_The_Farm", (box_cx, cy_col1, z_r3 - 0.10), (0.34, 0.28, 0.08), mat_white_chair, has_handle=False)
    create_insert_box("Game_Gravitrax", (box_cx, cy_col2, z_r3 - 0.08), (0.34, 0.30, 0.12), mat_toy_blue, has_handle=False)
    create_insert_box("Toy_Red_Box", (box_cx, cy_col1, z_r4 - 0.06), (0.24, 0.26, 0.18), mat_toy_red, has_handle=False)

    # Lego baseplate standing vertically on top of Col 3 against wall
    lego_mesh = bpy.data.meshes.new("Lego_Baseplate_Green")
    lego_bm = bmesh.new()
    add_box(lego_bm, (x0 + 0.010, y_c3_min + 0.02, z_top_col3), (x0 + 0.016, y_c3_max - 0.02, z_top_col3 + 0.280))
    lego_bm.to_mesh(lego_mesh)
    lego_bm.free()
    lego_obj = bpy.data.objects.new("Lego_Baseplate_Green", lego_mesh)
    add_obj_to_collection(lego_obj)
    lego_obj.data.materials.append(mat_toy_green_lego)

    # Toy truck on Step 3
    truck_mesh = bpy.data.meshes.new("Toy_Truck_Step3")
    truck_bm = bmesh.new()
    add_box(truck_bm, (x0 + 0.12, cy_col3 - 0.12, z_top_col3), (x1 - 0.08, cy_col3 + 0.12, z_top_col3 + 0.14))
    truck_bm.to_mesh(truck_mesh)
    truck_bm.free()
    truck_obj = bpy.data.objects.new("Toy_Truck_Step3", truck_mesh)
    add_obj_to_collection(truck_obj)
    truck_obj.data.materials.append(mat_dark_plastic)
    apply_bevel_and_uv(truck_obj, bevel_width=0.003)

    # Mini hockey / game on Step 1
    hock_mesh = bpy.data.meshes.new("Toy_Mini_Hockey_Step1")
    hock_bm = bmesh.new()
    add_box(hock_bm, (x0 + 0.04, cy_col1 - 0.15, z_top_col1), (x1 - 0.04, cy_col1 + 0.15, z_top_col1 + 0.035))
    hock_bm.to_mesh(hock_mesh)
    hock_bm.free()
    hock_obj = bpy.data.objects.new("Toy_Mini_Hockey_Step1", hock_mesh)
    add_obj_to_collection(hock_obj)
    hock_obj.data.materials.append(mat_white_chair)
    apply_bevel_and_uv(hock_obj, bevel_width=0.002)

    # ---------------------------------------------------------
    # 5. MODULAR LOW CABINETS (MALÉ SKŘÍŇKY)
    # ---------------------------------------------------------
    print("Building Modular Low Cabinets...")
    cab_y_start = y_col4 + 0.010 # tightly adjacent
    cab_w = 0.390
    cab_depth = 0.380
    cab_x0 = 0.385
    cab_x1 = cab_x0 + cab_depth # 0.765
    leg_h = 0.060
    cab_h = 0.620 # total height with legs = 0.680m
    
    # 2 Modules touching seamlessly side-by-side
    for mod_idx in range(2):
        my0 = cab_y_start + mod_idx * cab_w
        my1 = my0 + cab_w
        
        # Carcass mesh
        c_mesh = bpy.data.meshes.new(f"Cabinet_Carcass_Mod_{mod_idx+1}")
        c_bm = bmesh.new()

        c_z0 = z_floor + leg_h # 0.075
        c_z1 = c_z0 + cab_h    # 0.695
        t_c = 0.018

        # Bottom panel
        add_box(c_bm, (cab_x0, my0, c_z0), (cab_x1, my1, c_z0 + t_c))
        # Top panel
        add_box(c_bm, (cab_x0, my0, c_z1 - t_c), (cab_x1, my1, c_z1))
        # Left side panel
        add_box(c_bm, (cab_x0, my0, c_z0 + t_c), (cab_x1, my0 + t_c, c_z1 - t_c))
        # Right side panel
        add_box(c_bm, (cab_x0, my1 - t_c, c_z0 + t_c), (cab_x1, my1, c_z1 - t_c))
        # Back panel
        add_box(c_bm, (cab_x0, my0 + t_c, c_z0 + t_c), (cab_x0 + 0.008, my1 - t_c, c_z1 - t_c))

        c_bm.to_mesh(c_mesh)
        c_bm.free()
        c_obj = bpy.data.objects.new(f"Cabinet_Carcass_Mod_{mod_idx+1}", c_mesh)
        add_obj_to_collection(c_obj)
        c_obj.data.materials.append(mat_oak)
        apply_bevel_and_uv(c_obj, bevel_width=0.002, uv_scale=1.0)

        # 4 Cylindrical Chrome Legs
        leg_mesh = bpy.data.meshes.new(f"Cabinet_Legs_Mod_{mod_idx+1}")
        leg_bm = bmesh.new()
        leg_r = 0.015
        leg_pts = [
            (cab_x0 + 0.045, my0 + 0.045),
            (cab_x1 - 0.045, my0 + 0.045),
            (cab_x0 + 0.045, my1 - 0.045),
            (cab_x1 - 0.045, my1 - 0.045),
        ]
        for lx, ly in leg_pts:
            add_cylinder(
                leg_bm, radius=leg_r, depth=leg_h, segments=16,
                matrix=mathutils.Matrix.Translation((lx, ly, z_floor + leg_h/2))
            )
            # Dark foot pad
            add_cylinder(
                leg_bm, radius=leg_r + 0.002, depth=0.006, segments=16,
                matrix=mathutils.Matrix.Translation((lx, ly, z_floor + 0.003))
            )
        leg_bm.to_mesh(leg_mesh)
        leg_bm.free()
        leg_obj = bpy.data.objects.new(f"Cabinet_Legs_Mod_{mod_idx+1}", leg_mesh)
        add_obj_to_collection(leg_obj)
        leg_obj.data.materials.append(mat_chrome)
        bpy.context.view_layer.objects.active = leg_obj
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

        # Front Door (Light grey matte)
        d_mesh = bpy.data.meshes.new(f"Cabinet_Door_Mod_{mod_idx+1}")
        d_bm = bmesh.new()
        gap = 0.003
        door_x0 = cab_x1 - 0.004
        door_x1 = door_x0 + 0.018
        door_y0 = my0 + t_c + gap
        door_y1 = my1 - t_c - gap
        door_z0 = c_z0 + t_c + gap
        door_z1 = c_z1 - t_c - gap
        add_box(d_bm, (door_x0, door_y0, door_z0), (door_x1, door_y1, door_z1))
        d_bm.to_mesh(d_mesh)
        d_bm.free()
        d_obj = bpy.data.objects.new(f"Cabinet_Door_Mod_{mod_idx+1}", d_mesh)
        add_obj_to_collection(d_obj)
        d_obj.data.materials.append(mat_cabinet_grey)
        apply_bevel_and_uv(d_obj, bevel_width=0.002, uv_scale=0.5)

        # Round Silver Mushroom Knob Handle
        # In photo: Mod 1 knob is at upper right; Mod 2 knob is at upper left (meeting in the middle)
        knob_mesh = bpy.data.meshes.new(f"Cabinet_Knob_Mod_{mod_idx+1}")
        knob_bm = bmesh.new()
        knob_z = door_z1 - 0.065
        knob_y = door_y1 - 0.038 if mod_idx == 0 else door_y0 + 0.038
        # Stem
        add_cylinder(
            knob_bm, radius=0.005, depth=0.016, segments=12,
            matrix=mathutils.Matrix.Translation((door_x1 + 0.008, knob_y, knob_z)) @ mathutils.Euler((0, math.pi/2, 0)).to_matrix().to_4x4()
        )
        # Mushroom Head
        add_cylinder(
            knob_bm, radius=0.013, depth=0.010, segments=16,
            matrix=mathutils.Matrix.Translation((door_x1 + 0.018, knob_y, knob_z)) @ mathutils.Euler((0, math.pi/2, 0)).to_matrix().to_4x4()
        )
        knob_bm.to_mesh(knob_mesh)
        knob_bm.free()
        knob_obj = bpy.data.objects.new(f"Cabinet_Knob_Mod_{mod_idx+1}", knob_mesh)
        add_obj_to_collection(knob_obj)
        knob_obj.data.materials.append(mat_chrome)
        bpy.context.view_layer.objects.active = knob_obj
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

    # Decor on top of cabinet (Blue spherical toy / robot)
    robot_mesh = bpy.data.meshes.new("Cabinet_Decor_Robot")
    robot_bm = bmesh.new()
    bmesh.ops.create_icosphere(
        robot_bm, subdivisions=3, radius=0.055,
        matrix=mathutils.Matrix.Translation((cab_x0 + 0.18, cab_y_start + 0.22, z_floor + leg_h + cab_h + 0.055))
    )
    robot_bm.to_mesh(robot_mesh)
    robot_bm.free()
    robot_obj = bpy.data.objects.new("Cabinet_Decor_Robot", robot_mesh)
    add_obj_to_collection(robot_obj)
    robot_obj.data.materials.append(mat_toy_blue)
    bpy.context.view_layer.objects.active = robot_obj
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

    # ---------------------------------------------------------
    # 6. STUDY DESK (STŮL)
    # ---------------------------------------------------------
    print("Building Study Desk...")
    desk_mesh = bpy.data.meshes.new("Desk_1.06")
    desk_bm = bmesh.new()

    desk_y0 = 0.385
    desk_depth = 0.600
    desk_y1 = desk_y0 + desk_depth # 0.985
    desk_x0 = 0.880
    desk_w = 1.200
    desk_x1 = desk_x0 + desk_w # 2.080
    desk_h = 0.745
    t_desk = 0.032

    # Top board
    add_box(desk_bm, (desk_x0, desk_y0, desk_h - t_desk), (desk_x1, desk_y1, desk_h))

    # Left solid side leg panel
    t_leg = 0.028
    leg_inset_y = 0.010
    add_box(desk_bm, (desk_x0, desk_y0 + leg_inset_y, z_floor), (desk_x0 + t_leg, desk_y1 - leg_inset_y, desk_h - t_desk))

    # Right solid side leg panel
    add_box(desk_bm, (desk_x1 - t_leg, desk_y0 + leg_inset_y, z_floor), (desk_x1, desk_y1 - leg_inset_y, desk_h - t_desk))

    # Rear modesty panel
    modesty_h = 0.200
    modesty_y0 = desk_y0 + 0.055
    modesty_y1 = modesty_y0 + 0.018
    add_box(desk_bm, (desk_x0 + t_leg, modesty_y0, desk_h - t_desk - modesty_h), (desk_x1 - t_leg, modesty_y1, desk_h - t_desk))

    desk_bm.to_mesh(desk_mesh)
    desk_bm.free()
    desk_obj = bpy.data.objects.new("Desk_1.06", desk_mesh)
    add_obj_to_collection(desk_obj)
    desk_obj.data.materials.append(mat_oak)
    apply_bevel_and_uv(desk_obj, bevel_width=0.002, uv_scale=1.0)

    # Desk Accessories (Realism from photo)
    acc_mesh = bpy.data.meshes.new("Desk_Accessories_1.06")
    acc_bm = bmesh.new()
    # Pen cup
    add_cylinder(
        acc_bm, radius=0.038, depth=0.100, segments=16,
        matrix=mathutils.Matrix.Translation((desk_x0 + 0.15, desk_y0 + 0.15, desk_h + 0.050))
    )
    # Pop-it sensory toy
    add_box(acc_bm, (desk_x0 + 0.26, desk_y0 + 0.10, desk_h), (desk_x0 + 0.42, desk_y0 + 0.26, desk_h + 0.015))
    acc_bm.to_mesh(acc_mesh)
    acc_bm.free()
    acc_obj = bpy.data.objects.new("Desk_Accessories_1.06", acc_mesh)
    add_obj_to_collection(acc_obj)
    acc_obj.data.materials.append(mat_toy_yellow)
    bpy.context.view_layer.objects.active = acc_obj
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

    # Under-desk waste basket
    bin_mesh = bpy.data.meshes.new("Desk_Trash_Bin_1.06")
    bin_bm = bmesh.new()
    bmesh.ops.create_cone(
        bin_bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.110, radius2=0.090, depth=0.280,
        matrix=mathutils.Matrix.Translation((desk_x0 + 0.160, desk_y0 + 0.300, z_floor + 0.140))
    )
    bin_bm.to_mesh(bin_mesh)
    bin_bm.free()
    bin_obj = bpy.data.objects.new("Desk_Trash_Bin_1.06", bin_mesh)
    add_obj_to_collection(bin_obj)
    bin_obj.data.materials.append(mat_dark_plastic)
    bpy.context.view_layer.objects.active = bin_obj
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

    # Toys next to desk & Kallax (Paw patrol tower & curved car track)
    paw_mesh = bpy.data.meshes.new("Toy_Paw_Patrol_Tower")
    paw_bm = bmesh.new()
    # Tower base
    bmesh.ops.create_cone(
        paw_bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.080, radius2=0.060, depth=0.350,
        matrix=mathutils.Matrix.Translation((0.820, 0.550, z_floor + 0.175))
    )
    # Red roof
    bmesh.ops.create_cone(
        paw_bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.100, radius2=0.010, depth=0.080,
        matrix=mathutils.Matrix.Translation((0.820, 0.550, z_floor + 0.390))
    )
    paw_bm.to_mesh(paw_mesh)
    paw_bm.free()
    paw_obj = bpy.data.objects.new("Toy_Paw_Patrol_Tower", paw_mesh)
    add_obj_to_collection(paw_obj)
    paw_obj.data.materials.append(mat_toy_red)
    bpy.context.view_layer.objects.active = paw_obj
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

    # ---------------------------------------------------------
    # 7. WHITE DESIGNER LATTICE CHAIR (ŽIDLE)
    # ---------------------------------------------------------
    print("Building White Designer Lattice Chair...")
    cx = 1.480
    cy = 1.120
    rot_rad = math.radians(-10) # facing desk

    def l2w(lx, ly, lz):
        rx = lx * math.cos(rot_rad) - ly * math.sin(rot_rad)
        ry = lx * math.sin(rot_rad) + ly * math.cos(rot_rad)
        return mathutils.Vector((cx + rx, cy + ry, z_floor + lz))

    seat_h = 0.450
    crest_z = 0.380 # relative to seat_h -> total 0.830m
    sw = 0.440
    sd = 0.410

    # Seat & Legs Mesh
    chair_mesh = bpy.data.meshes.new("Chair_Lattice_Base")
    ch_bm = bmesh.new()

    # 4 Tapered Legs
    leg_coords = [
        (-0.19,  0.15, -0.21,  0.18),  # Front left
        ( 0.19,  0.15,  0.21,  0.18),  # Front right
        (-0.17, -0.16, -0.20, -0.22),  # Rear left
        ( 0.17, -0.16,  0.20, -0.22),  # Rear right
    ]
    for tx, ty, bx, by in leg_coords:
        p_top = l2w(tx, ty, seat_h)
        p_bot = l2w(bx, by, 0.0)
        v_dir = p_top - p_bot
        v_mid = (p_bot + p_top) / 2
        quat = v_dir.to_track_quat('Z', 'Y')
        bmesh.ops.create_cone(
            ch_bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.010, radius2=0.015, depth=v_dir.length,
            matrix=mathutils.Matrix.Translation(v_mid) @ quat.to_matrix().to_4x4()
        )

    # Seat Shell (quad grid)
    nx = 14
    ny = 14
    grid = []
    for iy in range(ny + 1):
        row = []
        fy = iy / ny
        ly = -sd/2 + fy * sd
        waterfall = -0.026 * (fy ** 3)
        for ix in range(nx + 1):
            fx = ix / nx
            lx = -sw/2 + fx * sw
            dish = -0.018 * (1.0 - (2*lx/sw)**2) * math.sin(fy * math.pi)
            side_lip = 0.014 * ((2*lx/sw)**2)
            lz = seat_h + dish + waterfall + side_lip
            row.append(ch_bm.verts.new(l2w(lx, ly, lz)))
        grid.append(row)

    for iy in range(ny):
        for ix in range(nx):
            ch_bm.faces.new([grid[iy][ix], grid[iy][ix+1], grid[iy+1][ix+1], grid[iy+1][ix]])

    ch_bm.to_mesh(chair_mesh)
    ch_bm.free()

    chair_obj = bpy.data.objects.new("Chair_Lattice_1.06", chair_mesh)
    add_obj_to_collection(chair_obj)
    chair_obj.data.materials.append(mat_white_chair)

    sol = chair_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol.thickness = 0.010
    sol.offset = -1.0
    bev = chair_obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.003
    bev.segments = 2
    sub = chair_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = 1

    # 2. Backrest Curve System (Smooth tubular lattice framework)
    c_data = bpy.data.curves.new("Chair_Backrest_Curve", type='CURVE')
    c_data.dimensions = '3D'
    c_data.bevel_depth = 0.010 # 20mm round tube
    c_data.bevel_resolution = 4
    c_data.resolution_u = 16

    def add_spline(pts):
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(len(pts) - 1)
        for idx, (pt, h_l, h_r) in enumerate(pts):
            bp = spline.bezier_points[idx]
            bp.co = l2w(pt[0], pt[1], seat_h + pt[2])
            bp.handle_left = l2w(h_l[0], h_l[1], seat_h + h_l[2])
            bp.handle_right = l2w(h_r[0], h_r[1], seat_h + h_r[2])
            bp.handle_left_type = 'FREE'
            bp.handle_right_type = 'FREE'

    # Spline 1: Outer Perimeter Frame (Symmetrical Arch)
    outer_pts = [
        ((-sw/2,  0.04, 0.01), (-sw/2,  0.06, 0.00), (-sw/2, -0.04, 0.10)),
        ((-sw/2, -0.08, 0.16), (-sw/2, -0.04, 0.11), (-sw/2 + 0.03, -0.14, 0.22)),
        ((-sw/2 + 0.07, -0.17, 0.29), (-sw/2 + 0.04, -0.15, 0.24), (-0.10, -0.20, crest_z)),
        (( 0.00, -0.20, crest_z), (-0.06, -0.20, crest_z), ( 0.06, -0.20, crest_z)),
        (( sw/2 - 0.07, -0.17, 0.29), ( 0.10, -0.20, crest_z), ( sw/2 - 0.04, -0.15, 0.24)),
        (( sw/2, -0.08, 0.16), ( sw/2 - 0.03, -0.14, 0.22), ( sw/2, -0.04, 0.11)),
        (( sw/2,  0.04, 0.01), ( sw/2, -0.04, 0.10), ( sw/2,  0.06, 0.00)),
    ]
    add_spline(outer_pts)

    # Spline 2: Middle Arch looping through crest
    arch_left = [
        ((-0.18, -sd/2 + 0.02, 0.01), (-0.18, -sd/2 + 0.05, 0.00), (-0.16, -sd/2 - 0.02, 0.10)),
        ((-0.10, -sd/2 - 0.06, 0.20), (-0.14, -sd/2 - 0.04, 0.14), (-0.05, -sd/2 - 0.08, 0.26)),
        (( 0.00, -sd/2 - 0.08, 0.33), (-0.04, -sd/2 - 0.08, 0.31), ( 0.04, -sd/2 - 0.08, 0.31)),
        (( 0.10, -sd/2 - 0.06, 0.20), ( 0.05, -sd/2 - 0.08, 0.26), ( 0.14, -sd/2 - 0.04, 0.14)),
        (( 0.18, -sd/2 + 0.02, 0.01), ( 0.16, -sd/2 - 0.02, 0.10), ( 0.18, -sd/2 + 0.05, 0.00)),
    ]
    add_spline(arch_left)

    # Spline 3: Interlacing Central Loops (Masters kidney ribbons)
    loop_1 = [
        ((-0.07, -sd/2 + 0.02, 0.01), (-0.07, -sd/2 + 0.04, 0.00), (-0.06, -sd/2 - 0.02, 0.10)),
        ((-0.08, -sd/2 - 0.05, 0.18), (-0.08, -sd/2 - 0.03, 0.13), (-0.04, -sd/2 - 0.07, 0.24)),
        (( 0.05, -sd/2 - 0.07, 0.26), ( 0.00, -sd/2 - 0.07, 0.26), ( 0.08, -sd/2 - 0.05, 0.22)),
        (( 0.07, -sd/2 - 0.03, 0.15), ( 0.08, -sd/2 - 0.05, 0.20), ( 0.06, -sd/2 - 0.01, 0.08)),
        (( 0.00, -sd/2 + 0.02, 0.01), ( 0.04, -sd/2 + 0.01, 0.04), ( 0.00, -sd/2 + 0.04, 0.00)),
    ]
    add_spline(loop_1)

    loop_2 = [
        (( 0.07, -sd/2 + 0.02, 0.01), ( 0.07, -sd/2 + 0.04, 0.00), ( 0.06, -sd/2 - 0.02, 0.10)),
        (( 0.08, -sd/2 - 0.05, 0.18), ( 0.08, -sd/2 - 0.03, 0.13), ( 0.04, -sd/2 - 0.07, 0.24)),
        ((-0.05, -sd/2 - 0.07, 0.26), ( 0.00, -sd/2 - 0.07, 0.26), (-0.08, -sd/2 - 0.05, 0.22)),
        ((-0.07, -sd/2 - 0.03, 0.15), (-0.08, -sd/2 - 0.05, 0.20), (-0.06, -sd/2 - 0.01, 0.08)),
        (( 0.00, -sd/2 + 0.02, 0.01), (-0.04, -sd/2 + 0.01, 0.04), ( 0.00, -sd/2 + 0.04, 0.00)),
    ]
    add_spline(loop_2)

    c_obj = bpy.data.objects.new("Chair_Backrest_Curve", c_data)
    add_obj_to_collection(c_obj)
    c_obj.data.materials.append(mat_white_chair)

    # Convert curve to mesh and join with chair_obj
    bpy.context.view_layer.objects.active = c_obj
    c_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    c_obj.select_set(False)

    bpy.context.view_layer.objects.active = chair_obj
    chair_obj.select_set(True)
    c_obj.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()

    print("=== ROOM 1.06 FURNITURE BUILD FINISHED SUCCESSFULLY ===")

run()
