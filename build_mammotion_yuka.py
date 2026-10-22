import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix, Euler
import math

def build_mammotion_yuka_system():
    print("=== BUILDING CAD-PERFECT MAMMOTION YUKA 2000 SYSTEM ===")

    # 1. Collection management
    coll_name = "Garden_Mammotion_Yuka"
    old_coll = bpy.data.collections.get(coll_name)
    if old_coll:
        for o in list(old_coll.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old_coll)

    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)

    # 2. PBR Materials Creation
    def get_or_create_mat(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        out = nodes.new(type='ShaderNodeOutputMaterial')
        out.location = (400, 0)
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return mat, bsdf

    # Mat 1: Light Architectural Concrete Slab
    mat_concrete, bsdf_concrete = get_or_create_mat("Mat_Yuka_Concrete_Pad")
    nodes = mat_concrete.node_tree.nodes
    links = mat_concrete.node_tree.links
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.65
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.52, 0.51, 0.48, 1.0) # weathered stone
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.64, 0.63, 0.60, 1.0) # light stone grey
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf_concrete.inputs['Base Color'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-100, -200)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf_concrete.inputs['Normal'])
    bsdf_concrete.inputs['Roughness'].default_value = 0.82

    # Mat 2: Dark Anthracite Steel Post (Powder-coated metal)
    mat_post, bsdf_post = get_or_create_mat("Mat_Yuka_Post_Anthracite")
    bsdf_post.inputs['Base Color'].default_value = (0.05, 0.055, 0.065, 1.0)
    bsdf_post.inputs['Metallic'].default_value = 0.90
    bsdf_post.inputs['Roughness'].default_value = 0.28

    # Mat 3: Dark Textured Station Plastic (Dock base & ramp)
    mat_station, bsdf_station = get_or_create_mat("Mat_Yuka_Station_Dark")
    bsdf_station.inputs['Base Color'].default_value = (0.08, 0.085, 0.095, 1.0)
    bsdf_station.inputs['Roughness'].default_value = 0.55

    # Mat 4: Canopy Roof Dark Graphite (Mammotion official shelter shell)
    mat_canopy, bsdf_canopy = get_or_create_mat("Mat_Yuka_Canopy_Graphite")
    bsdf_canopy.inputs['Base Color'].default_value = (0.055, 0.060, 0.068, 1.0) # deep graphite
    bsdf_canopy.inputs['Roughness'].default_value = 0.42

    # Mat 5: Mower Body White Satin (Automotive weatherproof polymer)
    mat_white, bsdf_white = get_or_create_mat("Mat_Yuka_Body_White")
    bsdf_white.inputs['Base Color'].default_value = (0.94, 0.95, 0.95, 1.0)
    bsdf_white.inputs['Roughness'].default_value = 0.18

    # Mat 6: Mower Undercarriage / Bumper Matte Black
    mat_chassis, bsdf_chassis = get_or_create_mat("Mat_Yuka_Chassis_Black")
    bsdf_chassis.inputs['Base Color'].default_value = (0.06, 0.065, 0.075, 1.0)
    bsdf_chassis.inputs['Roughness'].default_value = 0.50

    # Mat 7: Off-Road Tire Rubber (Dark charcoal black rubber)
    mat_rubber, bsdf_rubber = get_or_create_mat("Mat_Yuka_Tire_Rubber")
    bsdf_rubber.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
    bsdf_rubber.inputs['Roughness'].default_value = 0.65

    # Mat 8: White Wheel Rim Accent Ring
    mat_rim_white, bsdf_rim_white = get_or_create_mat("Mat_Yuka_Rim_White")
    bsdf_rim_white.inputs['Base Color'].default_value = (0.95, 0.96, 0.96, 1.0)
    bsdf_rim_white.inputs['Roughness'].default_value = 0.22

    # Mat 9: Active Green LED Status Bar
    mat_led_green, bsdf_led_green = get_or_create_mat("Mat_Yuka_LED_Green")
    bsdf_led_green.inputs['Base Color'].default_value = (0.12, 1.0, 0.22, 1.0)
    bsdf_led_green.inputs['Emission Color'].default_value = (0.12, 1.0, 0.22, 1.0)
    bsdf_led_green.inputs['Emission Strength'].default_value = 10.0
    bsdf_led_green.inputs['Roughness'].default_value = 0.15

    # Mat 10: Yellow Caution Stripe
    mat_caution, bsdf_caution = get_or_create_mat("Mat_Yuka_Caution_Stripe")
    bsdf_caution.inputs['Base Color'].default_value = (0.95, 0.75, 0.05, 1.0)
    bsdf_caution.inputs['Roughness'].default_value = 0.30

    # Mat 11: Technical Spec Label Sticker (Rear)
    mat_spec, bsdf_spec = get_or_create_mat("Mat_Yuka_Spec_Label")
    bsdf_spec.inputs['Base Color'].default_value = (0.88, 0.89, 0.89, 1.0)
    bsdf_spec.inputs['Roughness'].default_value = 0.25

    # Mat 12: Emergency STOP Red
    mat_stop_red, bsdf_stop_red = get_or_create_mat("Mat_Yuka_Stop_Red")
    bsdf_stop_red.inputs['Base Color'].default_value = (0.85, 0.05, 0.05, 1.0)
    bsdf_stop_red.inputs['Roughness'].default_value = 0.28

    # Mat 13: Sensor Glass / Camera Aperture
    mat_glass, bsdf_glass = get_or_create_mat("Mat_Yuka_Sensor_Glass")
    bsdf_glass.inputs['Base Color'].default_value = (0.02, 0.03, 0.04, 1.0)
    bsdf_glass.inputs['Roughness'].default_value = 0.04
    if 'Transmission Weight' in bsdf_glass.inputs:
        bsdf_glass.inputs['Transmission Weight'].default_value = 0.88

    # Mat 14: Gold Charging Contacts
    mat_gold, bsdf_gold = get_or_create_mat("Mat_Yuka_Charging_Gold")
    bsdf_gold.inputs['Base Color'].default_value = (0.95, 0.75, 0.25, 1.0)
    bsdf_gold.inputs['Metallic'].default_value = 0.95
    bsdf_gold.inputs['Roughness'].default_value = 0.20

    # Mat 15: Black Molded Rubber / Socket Plastic
    mat_socket, bsdf_socket = get_or_create_mat("Mat_Yuka_Socket_Black")
    bsdf_socket.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bsdf_socket.inputs['Roughness'].default_value = 0.40

    def create_obj(name, bm, mat=None, smooth=True, bevel_width=None):
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        if smooth:
            for p in mesh.polygons:
                p.use_smooth = True
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        if mat:
            obj.data.materials.append(mat)
        if bevel_width:
            mod = obj.modifiers.new("Bevel", 'BEVEL')
            mod.width = bevel_width
            mod.segments = 2
            mod.limit_method = 'ANGLE'
        coll.objects.link(obj)
        return obj

    def add_box(bm, center, size, rot=(0, 0, 0)):
        mat = Matrix.LocRotScale(
            Vector(center),
            Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))),
            Vector(size)
        )
        return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

    def add_cylinder(bm, center, radius, depth, rot=(0, 0, 0), segments=24, cap_ends=True):
        mat = Matrix.LocRotScale(
            Vector(center),
            Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))),
            Vector((1, 1, 1))
        )
        return bmesh.ops.create_cone(bm, cap_ends=cap_ends, segments=segments,
                                     radius1=radius, radius2=radius, depth=depth,
                                     matrix=mat)

    root = bpy.data.objects.new("Mammotion_Yuka_System", None)
    root.location = Vector((0, 0, 0))
    coll.objects.link(root)

    center_y = 11.45
    pad_z_top = -0.018

    # =========================================================================
    # PART 1: CONCRETE PAD (Betonové stání)
    # =========================================================================
    print("Building Concrete Pad...")
    bm_pad = bmesh.new()
    add_box(bm_pad, center=(-1.15, center_y, -0.045), size=(0.76, 0.86, 0.055))
    top_edges = [e for e in bm_pad.edges if all(v.co.z > -0.025 for v in e.verts)]
    bmesh.ops.bevel(bm_pad, geom=top_edges, offset=0.010, segments=3, profile=0.5)
    obj_pad = create_obj("Yuka_Concrete_Pad", bm_pad, mat_concrete, smooth=True)
    obj_pad.parent = root

    # =========================================================================
    # PART 2: ELECTRICAL POWER POST (Černý sloupek se zásuvkou)
    # =========================================================================
    print("Building Electrical Post...")
    post_x = -0.86
    post_y = 11.78
    post_z_base = pad_z_top
    post_h = 0.58

    # A. Flange base plate
    bm_flange = bmesh.new()
    add_box(bm_flange, center=(post_x, post_y, post_z_base + 0.004), size=(0.10, 0.10, 0.008))
    for dx in [-0.038, 0.038]:
        for dy in [-0.038, 0.038]:
            add_cylinder(bm_flange, center=(post_x + dx, post_y + dy, post_z_base + 0.010),
                         radius=0.005, depth=0.008, segments=6)
    obj_flange = create_obj("Yuka_Electrical_Post_Base", bm_flange, mat_post, smooth=False)
    obj_flange.parent = root

    # B. Post Column & Top Cap
    bm_col = bmesh.new()
    add_box(bm_col, center=(post_x, post_y, post_z_base + post_h * 0.5), size=(0.06, 0.06, post_h))
    vert_edges = [e for e in bm_col.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.4]
    bmesh.ops.bevel(bm_col, geom=vert_edges, offset=0.004, segments=2)
    # Top pyramid cap
    add_cylinder(bm_col, center=(post_x, post_y, post_z_base + post_h + 0.008),
                 radius=0.046, depth=0.016, rot=(0, 0, 45), segments=4)
    obj_col = create_obj("Yuka_Electrical_Post_Column", bm_col, mat_post, smooth=True)
    obj_col.parent = root

    # C. Outdoor Weatherproof Socket Box
    bm_sock = bmesh.new()
    sock_z = post_z_base + 0.44
    add_box(bm_sock, center=(post_x, post_y - 0.035, sock_z), size=(0.038, 0.016, 0.055))
    # Hinged cover
    add_box(bm_sock, center=(post_x, post_y - 0.046, sock_z + 0.005), size=(0.040, 0.006, 0.054), rot=(12, 0, 0))
    obj_sock = create_obj("Yuka_Electrical_Socket", bm_sock, mat_socket, smooth=True)
    obj_sock.parent = root

    # D. Power Cable Curve
    curve_data = bpy.data.curves.new("Yuka_Power_Cable", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.0045
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(4)
    pts = [
        (post_x, post_y - 0.050, sock_z - 0.020),
        (post_x, post_y - 0.042, sock_z - 0.15),
        (post_x, post_y - 0.035, post_z_base + 0.12),
        (post_x - 0.015, post_y - 0.045, post_z_base + 0.03),
        (post_x - 0.050, post_y - 0.08, post_z_base + 0.01)
    ]
    for i, pt in enumerate(pts):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj_cable = bpy.data.objects.new("Yuka_Power_Cable", curve_data)
    obj_cable.data.materials.append(mat_socket)
    coll.objects.link(obj_cable)
    obj_cable.parent = root

    # =========================================================================
    # PART 3: CHARGING STATION BASE (Dokovací základna)
    # =========================================================================
    print("Building Charging Base Station...")
    dock_z = pad_z_top

    bm_dock = bmesh.new()
    add_box(bm_dock, center=(-1.15, center_y, dock_z + 0.007), size=(0.62, 0.50, 0.014))
    # Wheel Guide Ribs
    for gy in [-0.205, 0.205]:
        add_box(bm_dock, center=(-1.15, center_y + gy, dock_z + 0.018), size=(0.52, 0.024, 0.018))
    # Front Docking Head Tower
    add_box(bm_dock, center=(-0.88, center_y, dock_z + 0.06), size=(0.10, 0.20, 0.12))

    # Gold Charging Contact Prongs
    bm_gold = bmesh.new()
    for cy in [-0.045, 0.045]:
        add_box(bm_gold, center=(-0.935, center_y + cy, dock_z + 0.075), size=(0.020, 0.015, 0.030))
    obj_gold = create_obj("Yuka_Station_Gold_Contacts", bm_gold, mat_gold, smooth=False)
    obj_gold.parent = root

    obj_dock = create_obj("Yuka_Charging_Base_Plate", bm_dock, mat_station, smooth=True)
    obj_dock.parent = root

    # =========================================================================
    # PART 4: GARAGE CANOPY / SHELTER (Stříška Mammotion Yuka)
    # =========================================================================
    print("Building Garage Canopy Shelter...")
    # Two arched side support legs (Left at +Y, Right at -Y)
    bm_legs = bmesh.new()
    for side_sign, leg_y in [(1.0, center_y + 0.28), (-1.0, center_y - 0.28)]:
        steps = 6
        prev_ring = None
        for s in range(steps):
            t = s / (steps - 1)
            px = -0.88 - 0.14 * (t**1.4)
            pz = dock_z + 0.01 + 0.37 * (t**0.8)
            py = leg_y - side_sign * (0.012 * t)
            
            w_x = 0.065 * (1.0 - 0.25 * t)
            w_y = 0.032 * (1.0 - 0.15 * t)
            
            p1 = bm_legs.verts.new(Vector((px - w_x*0.5, py - w_y*0.5, pz)))
            p2 = bm_legs.verts.new(Vector((px + w_x*0.5, py - w_y*0.5, pz)))
            p3 = bm_legs.verts.new(Vector((px + w_x*0.5, py + w_y*0.5, pz)))
            p4 = bm_legs.verts.new(Vector((px - w_x*0.5, py + w_y*0.5, pz)))
            ring = [p1, p2, p3, p4]
            if prev_ring is not None:
                bm_legs.faces.new([prev_ring[0], prev_ring[1], ring[1], ring[0]])
                bm_legs.faces.new([prev_ring[1], prev_ring[2], ring[2], ring[1]])
                bm_legs.faces.new([prev_ring[2], prev_ring[3], ring[3], ring[2]])
                bm_legs.faces.new([prev_ring[3], prev_ring[0], ring[0], ring[3]])
            else:
                bm_legs.faces.new([p4, p3, p2, p1])
            prev_ring = ring
        bm_legs.faces.new(prev_ring)
        
        # Base foot
        add_box(bm_legs, center=(-0.88, leg_y, dock_z + 0.015), size=(0.12, 0.055, 0.020))

    obj_legs = create_obj("Yuka_Garage_Support_Legs", bm_legs, mat_canopy, smooth=True, bevel_width=0.004)
    obj_legs.parent = root

    # Aerodynamic Roof Canopy (Stříška)
    bm_canopy = bmesh.new()
    bmesh.ops.create_cube(bm_canopy, size=1.0)
    bmesh.ops.subdivide_edges(bm_canopy, edges=bm_canopy.edges[:], cuts=12, use_grid_fill=True)
    
    canopy_len = 0.72 # X from -0.80 to -1.52
    canopy_wid = 0.62 # Y from 11.14 to 11.76
    canopy_th = 0.014
    
    for v in bm_canopy.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        u = nx + 0.5
        v_norm = ny * 2.0
        
        rx = -0.80 - u * canopy_len
        ry = center_y + ny * canopy_wid
        
        parabolic_drop = -0.045 * (abs(v_norm)**1.8)
        valley_scoop = -0.008 * math.exp(-((v_norm / 0.25)**2))
        shoulder_ridge = 0.010 * math.exp(-(((abs(v_norm) - 0.52) / 0.18)**2))
        longitudinal_slope = -0.030 * u - 0.020 * (u**3)
        
        base_z = dock_z + 0.415 + parabolic_drop + valley_scoop + shoulder_ridge + longitudinal_slope
        rz = base_z + nz * canopy_th
        v.co = Vector((rx, ry, rz))

    # Sleek low-profile embossed MAMMOTION logo bar on central ridge
    add_box(bm_canopy, center=(-1.15, center_y, dock_z + 0.432), size=(0.28, 0.065, 0.003))

    obj_canopy = create_obj("Yuka_Garage_Canopy_Roof", bm_canopy, mat_canopy, smooth=True, bevel_width=0.003)
    obj_canopy.parent = root

    # =========================================================================
    # PART 5: MAMMOTION YUKA 2000 ROBOT MOWER (Samotná sekačka)
    # =========================================================================
    print("Building Mammotion Yuka 2000 Mower...")
    mower_x = -1.14
    mower_y = center_y
    mower_z = dock_z + 0.012

    # A. Upper Body (White sculpted automotive shell)
    bm_mower_white = bmesh.new()
    bmesh.ops.create_cube(bm_mower_white, size=1.0)
    bmesh.ops.subdivide_edges(bm_mower_white, edges=bm_mower_white.edges[:], cuts=6, use_grid_fill=True)
    
    wx, wy, wz = 0.52, 0.34, 0.12
    for v in bm_mower_white.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        u = nx + 0.5 # 0 (rear -X) to 1 (front +X)
        
        width_mod = 1.0 - 0.24 * (u**1.5)
        height_drop = -0.025 * (u**2)
        side_drop = -0.020 * (abs(ny*2.0)**2)
        
        rx = mower_x + (u - 0.5) * wx
        ry = mower_y + ny * wy * width_mod
        rz = (mower_z + 0.14) + nz * wz + height_drop + side_drop
        v.co = Vector((rx, ry, rz))

    obj_mower_white = create_obj("Yuka_Mower_Upper_White", bm_mower_white, mat_white, smooth=True, bevel_width=0.006)
    obj_mower_white.parent = root

    # B. Lower Chassis / Bumper (Matte Black)
    bm_chassis = bmesh.new()
    add_box(bm_chassis, center=(mower_x, mower_y, mower_z + 0.060), size=(0.52, 0.30, 0.07))
    # Front Bumper (+X)
    add_box(bm_chassis, center=(mower_x + 0.27, mower_y, mower_z + 0.070), size=(0.05, 0.25, 0.08))
    # Rear Spec Housing (-X)
    add_box(bm_chassis, center=(mower_x - 0.26, mower_y, mower_z + 0.065), size=(0.03, 0.16, 0.06))
    # Rear Tubular Grab Handle
    add_box(bm_chassis, center=(mower_x - 0.28, mower_y, mower_z + 0.115), size=(0.020, 0.18, 0.020))

    obj_chassis = create_obj("Yuka_Mower_Chassis_Black", bm_chassis, mat_chassis, smooth=True, bevel_width=0.006)
    obj_chassis.parent = root

    # Technical Spec Label Sticker on rear face (matching inspect_yuka2.png)
    bm_spec = bmesh.new()
    add_box(bm_spec, center=(mower_x - 0.276, mower_y, mower_z + 0.065), size=(0.002, 0.085, 0.038))
    obj_spec = create_obj("Yuka_Mower_Spec_Label", bm_spec, mat_spec, smooth=False)
    obj_spec.parent = root

    # C. Active Green LED Status Light Bar & Yellow Caution Stripe
    bm_led = bmesh.new()
    bm_caution = bmesh.new()
    for ly in [mower_y + 0.155, mower_y - 0.155]:
        add_box(bm_led, center=(mower_x + 0.07, ly, mower_z + 0.168), size=(0.08, 0.008, 0.012))
        add_box(bm_caution, center=(mower_x + 0.07, ly, mower_z + 0.158), size=(0.08, 0.006, 0.005))
    obj_led = create_obj("Yuka_Mower_LED_Status_Bars", bm_led, mat_led_green, smooth=False)
    obj_led.parent = root
    obj_caution = create_obj("Yuka_Mower_Caution_Stripes", bm_caution, mat_caution, smooth=False)
    obj_caution.parent = root

    # D. Rear Operator Console (STOP Button, Dial & Sensor Glass)
    bm_console = bmesh.new()
    console_x = mower_x - 0.12
    add_box(bm_console, center=(console_x, mower_y, mower_z + 0.205), size=(0.14, 0.12, 0.025))
    add_cylinder(bm_console, center=(console_x + 0.035, mower_y, mower_z + 0.222), radius=0.016, depth=0.010)
    obj_console = create_obj("Yuka_Mower_Console_Housing", bm_console, mat_chassis, smooth=True, bevel_width=0.004)
    obj_console.parent = root

    # Red Emergency STOP Button
    bm_stop = bmesh.new()
    add_cylinder(bm_stop, center=(console_x - 0.025, mower_y, mower_z + 0.226), radius=0.026, depth=0.014)
    obj_stop = create_obj("Yuka_Mower_Stop_Button", bm_stop, mat_stop_red, smooth=True, bevel_width=0.003)
    obj_stop.parent = root

    # Sensor Glass / Camera Aperture
    bm_glass = bmesh.new()
    add_cylinder(bm_glass, center=(mower_x - 0.24, mower_y, mower_z + 0.185), radius=0.014, depth=0.008)
    obj_glass = create_obj("Yuka_Mower_Sensor_Glass", bm_glass, mat_glass, smooth=True)
    obj_glass.parent = root

    # E. Massive Rear Off-Road Drive Wheels with Cleats & White Rim Accent
    wheel_r = 0.095
    wheel_w = 0.055
    wheel_x = mower_x - 0.18

    bm_tires = bmesh.new()
    bm_rims = bmesh.new()

    for side_sign, wy in [(1.0, mower_y + 0.190), (-1.0, mower_y - 0.190)]:
        wheel_center = (wheel_x, wy, mower_z + wheel_r)
        
        # 1. Main Wheel Core Cylinder
        add_cylinder(bm_tires, center=wheel_center, radius=wheel_r * 0.94, depth=wheel_w,
                     rot=(90, 0, 0), segments=28)
        
        # 2. Aggressive Chevron / Tractor Tread Cleats (14 cleats per wheel)
        num_cleats = 14
        for i in range(num_cleats):
            ang = (i / num_cleats) * 2.0 * math.pi
            cx = wheel_center[0] + math.sin(ang) * (wheel_r * 0.96)
            cz = wheel_center[2] + math.cos(ang) * (wheel_r * 0.96)
            add_box(bm_tires, center=(cx, wy, cz), size=(0.016, wheel_w * 0.92, 0.018),
                    rot=(0, math.degrees(-ang), 0))

        # 3. White Outer Rim Ring (Bílý lem ráfku)
        rim_y = wy + side_sign * (wheel_w * 0.5 + 0.002)
        add_cylinder(bm_rims, center=(wheel_center[0], rim_y, wheel_center[2]),
                     radius=wheel_r * 0.78, depth=0.006, rot=(90, 0, 0), segments=28)

        # 4. Textured Hub Cap
        add_cylinder(bm_tires, center=(wheel_center[0], rim_y + side_sign * 0.002, wheel_center[2]),
                     radius=wheel_r * 0.48, depth=0.008, rot=(90, 0, 0), segments=16)

    obj_tires = create_obj("Yuka_Mower_Rear_Tires", bm_tires, mat_rubber, smooth=True)
    obj_tires.parent = root

    obj_rims = create_obj("Yuka_Mower_Wheel_White_Rims", bm_rims, mat_rim_white, smooth=True)
    obj_rims.parent = root

    # F. Front Omnidirectional Caster Wheels
    bm_front_wheels = bmesh.new()
    front_x = mower_x + 0.18
    front_r = 0.038
    for wy in [mower_y + 0.10, mower_y - 0.10]:
        add_cylinder(bm_front_wheels, center=(front_x, wy, mower_z + front_r),
                     radius=front_r, depth=0.030, rot=(90, 0, 0), segments=16)
        add_box(bm_front_wheels, center=(front_x, wy, mower_z + front_r + 0.030),
                size=(0.025, 0.040, 0.035))
    obj_front_wheels = create_obj("Yuka_Mower_Front_Casters", bm_front_wheels, mat_chassis, smooth=True)
    obj_front_wheels.parent = root

    print("=== MAMMOTION YUKA 2000 SYSTEM BUILT SUCCESSFULLY ===")
    return root

if __name__ == "__main__":
    build_mammotion_yuka_system()
