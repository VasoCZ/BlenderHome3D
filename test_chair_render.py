import bpy
import bmesh
import math
import mathutils

def build_masters_chair(cx, cy, z_floor, rot_deg=0.0):
    mat_white = bpy.data.materials.get("Mat_Plastic_White_Matte")
    rot_rad = math.radians(rot_deg)

    def l2w(lx, ly, lz):
        rx = lx * math.cos(rot_rad) - ly * math.sin(rot_rad)
        ry = lx * math.sin(rot_rad) + ly * math.cos(rot_rad)
        return mathutils.Vector((cx + rx, cy + ry, z_floor + lz))

    seat_h = 0.450
    crest_z = 0.380 # relative to seat_h -> total 0.830m
    sw = 0.440
    sd = 0.410

    # 1. Base & Legs Mesh
    mesh = bpy.data.meshes.new("Chair_Lattice_Base")
    bm = bmesh.new()

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
            bm, cap_ends=True, cap_tris=False, segments=16,
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
            row.append(bm.verts.new(l2w(lx, ly, lz)))
        grid.append(row)

    for iy in range(ny):
        for ix in range(nx):
            bm.faces.new([grid[iy][ix], grid[iy][ix+1], grid[iy+1][ix+1], grid[iy+1][ix]])

    bm.to_mesh(mesh)
    bm.free()

    chair_obj = bpy.data.objects.new("Chair_Lattice_1.06", mesh)
    bpy.context.scene.collection.objects.link(chair_obj)
    chair_obj.data.materials.append(mat_white)

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

    # Spline 2: Left Arch looping through crest
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
    bpy.context.scene.collection.objects.link(c_obj)
    c_obj.data.materials.append(mat_white)

    # Convert curve to mesh and join
    bpy.context.view_layer.objects.active = c_obj
    c_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    c_obj.select_set(False)

    bpy.context.view_layer.objects.active = chair_obj
    chair_obj.select_set(True)
    c_obj.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()

    return chair_obj

print("build_masters_chair function ready.")
