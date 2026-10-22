import bpy
import bmesh
import math
import mathutils

def create_designer_chair(cx, cy, z_floor, rot_deg=0.0):
    mat_white = bpy.data.materials.get("Mat_Plastic_White_Matte")
    rot_rad = math.radians(rot_deg)

    def l2w(x, y, z):
        rx = x * math.cos(rot_rad) - y * math.sin(rot_rad)
        ry = x * math.sin(rot_rad) + y * math.cos(rot_rad)
        return mathutils.Vector((cx + rx, cy + ry, z_floor + z))

    seat_h = 0.450
    crest_z = seat_h + 0.380 # 0.830m
    sw = 0.430 # seat width
    sd = 0.410 # seat depth

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
        p_top = l2w(tx, ty, seat_h - 0.01)
        p_bot = l2w(bx, by, 0.0)
        v_dir = p_top - p_bot
        v_mid = (p_bot + p_top) / 2
        quat = v_dir.to_track_quat('Z', 'Y')
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.010, radius2=0.016, depth=v_dir.length,
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
        # Front waterfall
        waterfall = -0.028 * (fy ** 3)
        for ix in range(nx + 1):
            fx = ix / nx
            lx = -sw/2 + fx * sw
            # Ergonomic saddle dish
            dish = -0.018 * (1.0 - (2*lx/sw)**2) * math.sin(fy * math.pi)
            side_lip = 0.014 * ((2*lx/sw)**2)
            lz = seat_h + dish + waterfall + side_lip
            row.append(bm.verts.new(l2w(lx, ly, lz)))
        grid.append(row)

    for iy in range(ny):
        for ix in range(nx):
            bm.faces.new([grid[iy][ix], grid[iy][ix+1], grid[iy+1][ix+1], grid[iy+1][ix]])

    # Extrude / solidify seat
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
    c_data.bevel_depth = 0.011 # 22mm tubular ribbon
    c_data.bevel_resolution = 4
    c_data.resolution_u = 16

    def add_bezier_spline(pts):
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(len(pts) - 1)
        for idx, (pt, h_l, h_r) in enumerate(pts):
            bp = spline.bezier_points[idx]
            bp.co = l2w(*pt)
            bp.handle_left = l2w(*h_l)
            bp.handle_right = l2w(*h_r)
            bp.handle_left_type = 'FREE'
            bp.handle_right_type = 'FREE'

    # Spline 1: Outer Perimeter Frame (Chair Crest + Armrests)
    outer_pts = [
        # (pt, handle_left, handle_right)
        ((-sw/2,  0.02, seat_h + 0.01), (-sw/2,  0.05, seat_h), (-sw/2, -0.05, seat_h + 0.10)),  # Left seat base
        ((-sw/2, -0.10, seat_h + 0.16), (-sw/2, -0.06, seat_h + 0.12), (-sw/2 + 0.02, -0.15, seat_h + 0.22)), # Left armrest
        ((-sw/2 + 0.06, -0.18, seat_h + 0.28), (-sw/2 + 0.04, -0.16, seat_h + 0.24), (-0.12, -0.22, crest_z)), # Left shoulder
        (( 0.00, -0.22, crest_z), (-0.06, -0.22, crest_z), ( 0.06, -0.22, crest_z)),              # Top crest
        (( sw/2 - 0.06, -0.18, seat_h + 0.28), ( 0.12, -0.22, crest_z), ( sw/2 - 0.04, -0.16, seat_h + 0.24)), # Right shoulder
        (( sw/2, -0.10, seat_h + 0.16), ( sw/2 - 0.02, -0.15, seat_h + 0.22), ( sw/2, -0.06, seat_h + 0.12)), # Right armrest
        (( sw/2,  0.02, seat_h + 0.01), ( sw/2, -0.05, seat_h + 0.10), ( sw/2,  0.05, seat_h)),  # Right seat base
    ]
    add_bezier_spline(outer_pts)

    # Spline 2: Inner Arch 1 (Left base curving to right crest)
    arch1_pts = [
        ((-sw/2 + 0.04, -sd/2 + 0.02, seat_h + 0.01), (-sw/2 + 0.04, -sd/2 + 0.05, seat_h), (-sw/2 + 0.06, -sd/2, seat_h + 0.10)),
        ((-0.08, -sd/2 - 0.06, seat_h + 0.22), (-0.14, -sd/2 - 0.04, seat_h + 0.16), (-0.02, -sd/2 - 0.08, seat_h + 0.28)),
        (( 0.08, -sd/2 - 0.06, crest_z - 0.03), ( 0.02, -sd/2 - 0.07, seat_h + 0.32), ( 0.12, -sd/2 - 0.04, crest_z - 0.01)),
        (( sw/2 - 0.04, -sd/2 + 0.02, seat_h + 0.01), ( sw/2 - 0.06, -sd/2, seat_h + 0.10), ( sw/2 - 0.04, -sd/2 + 0.05, seat_h)),
    ]
    add_bezier_spline(arch1_pts)

    # Spline 3: Inner Arch 2 (Mirrored cross loop)
    arch2_pts = [
        (( sw/2 - 0.04, -sd/2 + 0.02, seat_h + 0.01), ( sw/2 - 0.04, -sd/2 + 0.05, seat_h), ( sw/2 - 0.06, -sd/2, seat_h + 0.10)),
        (( 0.08, -sd/2 - 0.06, seat_h + 0.22), ( 0.14, -sd/2 - 0.04, seat_h + 0.16), ( 0.02, -sd/2 - 0.08, seat_h + 0.28)),
        ((-0.08, -sd/2 - 0.06, crest_z - 0.03), (-0.02, -sd/2 - 0.07, seat_h + 0.32), (-0.12, -sd/2 - 0.04, crest_z - 0.01)),
        ((-sw/2 + 0.04, -sd/2 + 0.02, seat_h + 0.01), (-sw/2 + 0.06, -sd/2, seat_h + 0.10), (-sw/2 + 0.04, -sd/2 + 0.05, seat_h)),
    ]
    add_bezier_spline(arch2_pts)

    # Spline 4: Central loop (Iconic Kartell Masters silhouette)
    loop_pts = [
        (( 0.00, -sd/2 + 0.01, seat_h + 0.01), ( 0.00, -sd/2 + 0.03, seat_h), ( 0.00, -sd/2 - 0.02, seat_h + 0.10)),
        ((-0.07, -sd/2 - 0.05, seat_h + 0.18), (-0.05, -sd/2 - 0.03, seat_h + 0.14), (-0.06, -sd/2 - 0.07, seat_h + 0.24)),
        (( 0.00, -sd/2 - 0.08, seat_h + 0.30), (-0.04, -sd/2 - 0.08, seat_h + 0.28), ( 0.04, -sd/2 - 0.08, seat_h + 0.28)),
        (( 0.07, -sd/2 - 0.05, seat_h + 0.18), ( 0.06, -sd/2 - 0.07, seat_h + 0.24), ( 0.05, -sd/2 - 0.03, seat_h + 0.14)),
        (( 0.00, -sd/2 + 0.01, seat_h + 0.01), ( 0.00, -sd/2 - 0.02, seat_h + 0.10), ( 0.00, -sd/2 + 0.03, seat_h)),
    ]
    add_bezier_spline(loop_pts)

    c_obj = bpy.data.objects.new("Chair_Backrest_Curve", c_data)
    bpy.context.scene.collection.objects.link(c_obj)
    c_obj.data.materials.append(mat_white)

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

    return chair_obj

print("Designer chair generator ready.")
