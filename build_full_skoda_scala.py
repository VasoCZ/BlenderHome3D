import bpy
import bmesh
import math
import mathutils
import os

def build_skoda_scala(collection_target, car_loc=(0, 0, 0), car_rot_z=0.0):
    print("=== BUILDING 1:1 REALISTIC SKODA SCALA 2025 MONTE CARLO ===")
    
    # ---------------------------------------------------------
    # 1. MATERIALS SETUP
    # ---------------------------------------------------------
    def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.5, clearcoat=0.0, transmission=0.0, ior=1.45, emission_color=None, emission_strength=0.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        bsdf = None
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
        if not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            
        out_node = None
        for n in nodes:
            if n.type == 'OUTPUT_MATERIAL' and n.is_active_output:
                out_node = n
                break
        if not out_node:
            out_node = nodes.new(type='ShaderNodeOutputMaterial')
            links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
            
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = ior
        if 'Coat Weight' in bsdf.inputs:
            bsdf.inputs['Coat Weight'].default_value = clearcoat
            if 'Coat Roughness' in bsdf.inputs:
                bsdf.inputs['Coat Roughness'].default_value = 0.03
        elif 'Clearcoat' in bsdf.inputs:
            bsdf.inputs['Clearcoat'].default_value = clearcoat
            if 'Clearcoat Roughness' in bsdf.inputs:
                bsdf.inputs['Clearcoat Roughness'].default_value = 0.03
                
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
            
        if emission_color and emission_strength > 0:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission_color
                bsdf.inputs['Emission Strength'].default_value = emission_strength
                
        return mat

    mat_velvet_red = get_or_create_mat("Mat_Scala_Velvet_Red", (0.58, 0.022, 0.048, 1.0), metallic=0.45, roughness=0.14, clearcoat=1.0, ior=1.52)
    mat_black_magic = get_or_create_mat("Mat_Scala_Black_Magic", (0.012, 0.012, 0.014, 1.0), metallic=0.1, roughness=0.08, clearcoat=1.0, ior=1.52)
    mat_glass_clear = get_or_create_mat("Mat_Scala_Glass_Clear", (0.96, 0.98, 0.98, 1.0), roughness=0.01, transmission=0.95, ior=1.52)
    mat_glass_privacy = get_or_create_mat("Mat_Scala_Glass_Sunset_Privacy", (0.05, 0.05, 0.06, 1.0), roughness=0.02, transmission=0.80, ior=1.52)
    mat_plastic_matte = get_or_create_mat("Mat_Scala_Plastic_Matte", (0.035, 0.035, 0.038, 1.0), roughness=0.55)
    mat_chrome = get_or_create_mat("Mat_Scala_Chrome", (0.92, 0.93, 0.94, 1.0), metallic=0.98, roughness=0.08)
    mat_tyre_rubber = get_or_create_mat("Mat_Scala_Tyre_Rubber", (0.03, 0.03, 0.032, 1.0), roughness=0.68)
    mat_brake_disc = get_or_create_mat("Mat_Scala_Brake_Disc", (0.75, 0.76, 0.78, 1.0), metallic=0.95, roughness=0.22)
    mat_led_drl = get_or_create_mat("Mat_Scala_LED_DRL", (1.0, 1.0, 1.0, 1.0), roughness=0.1, emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=3.0)
    mat_headlight_chrome = get_or_create_mat("Mat_Scala_Headlight_Chrome", (0.95, 0.95, 0.96, 1.0), metallic=0.98, roughness=0.05)
    mat_taillight_glass = get_or_create_mat("Mat_Scala_Taillight_Glass", (0.75, 0.015, 0.025, 1.0), roughness=0.03, transmission=0.88, ior=1.55)
    mat_interior = get_or_create_mat("Mat_Scala_Interior_Dark", (0.045, 0.045, 0.05, 1.0), roughness=0.75)
    mat_seat_accent_red = get_or_create_mat("Mat_Scala_Seat_Accent_Red", (0.65, 0.03, 0.05, 1.0), roughness=0.60)

    # License Plate material with authentic texture
    plate_tex_path = r"C:\Users\Vaso\Antigravity\Project blender\assets\license_plate_1AH_U743.png"
    mat_plate = bpy.data.materials.get("Mat_Scala_License_Plate")
    if not mat_plate:
        mat_plate = bpy.data.materials.new(name="Mat_Scala_License_Plate")
    mat_plate.use_nodes = True
    nodes = mat_plate.node_tree.nodes
    links = mat_plate.node_tree.links
    nodes.clear()
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_node = nodes.new(type='ShaderNodeTexImage')
    if os.path.exists(plate_tex_path):
        tex_node.image = bpy.data.images.load(plate_tex_path)
    bsdf.inputs['Roughness'].default_value = 0.25
    links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    # Helper function to create an object from bmesh
    def finish_mesh(bm, name, mats_list):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        for m in mats_list:
            obj.data.materials.append(m)
        collection_target.objects.link(obj)
        
        # Smooth shading
        for p in obj.data.polygons:
            p.use_smooth = True
        return obj

    # ---------------------------------------------------------
    # 2. SCALA BODY SHELL (Velvet Red Metallic)
    # ---------------------------------------------------------
    # Exact Dimensions: Length 4.362m, Width 1.793m, Height 1.471m
    # Front axle Y = -1.325, Rear axle Y = +1.324
    # Ground clearance Z = 0.145m, Wheel radius R = 0.317m
    bm_body = bmesh.new()
    
    # We construct cross-sectional rings along the car's length (front to rear)
    # Each cross-section has 18 vertices going from right-bottom rocker -> right shoulder -> hood/roof -> left shoulder -> left-bottom rocker
    # Half-width and Z values defined symmetrically across X:
    # Points per section (right to left):
    # 0: Rocker sill right
    # 1: Lower door right
    # 2: Tornado line right (Z ~ 0.88)
    # 3: Beltline / base of glass right
    # 4: Hood / roof outer right
    # 5: Hood spear / roof center-right
    # 6: Centerline top
    # 7: Hood spear / roof center-left
    # 8: Hood / roof outer left
    # 9: Beltline / base of glass left
    # 10: Tornado line left
    # 11: Lower door left
    # 12: Rocker sill left
    
    # Sections along Y:
    # (Y_pos, width_rocker, width_tornado, width_roof, z_rocker, z_tornado, z_roof, z_center)
    sections_def = [
        # Nose / front bumper tip (Y = -2.181)
        (-2.181, 0.68, 0.64, 0.35, 0.20, 0.45, 0.65, 0.68),
        # Front bumper upper / lower grille split (Y = -2.120)
        (-2.120, 0.74, 0.72, 0.42, 0.20, 0.54, 0.70, 0.73),
        # Grille base / headlights start (Y = -2.050)
        (-2.050, 0.78, 0.76, 0.48, 0.20, 0.62, 0.73, 0.76),
        # Hood nose tip / emblem (Y = -1.950)
        (-1.950, 0.81, 0.80, 0.55, 0.20, 0.68, 0.75, 0.78),
        # Front wheel arch front edge (Y = -1.680)
        (-1.680, 0.85, 0.85, 0.62, 0.20, 0.75, 0.80, 0.82),
        # Front wheel arch peak (front axle Y = -1.325)
        (-1.325, 0.88, 0.88, 0.68, 0.68, 0.80, 0.84, 0.86), # arch cut
        # Front wheel arch rear edge (Y = -0.970)
        (-0.970, 0.86, 0.87, 0.72, 0.20, 0.83, 0.87, 0.89),
        # Windshield cowl / base of A-pillar (Y = -0.850)
        (-0.850, 0.87, 0.88, 0.74, 0.19, 0.86, 0.90, 0.92),
        # Mid A-pillar (Y = -0.400)
        (-0.400, 0.88, 0.89, 0.64, 0.19, 0.87, 1.25, 1.27),
        # Roof peak / B-pillar (Y = 0.100)
        (0.100, 0.89, 0.896, 0.62, 0.19, 0.88, 1.465, 1.471),
        # Rear door / C-pillar start (Y = 0.700)
        (0.700, 0.88, 0.89, 0.61, 0.19, 0.88, 1.460, 1.465),
        # Rear wheel arch front edge (Y = 0.970)
        (0.970, 0.87, 0.89, 0.60, 0.20, 0.87, 1.450, 1.455),
        # Rear wheel arch peak (rear axle Y = 1.324)
        (1.324, 0.88, 0.896, 0.58, 0.68, 0.88, 1.440, 1.445), # arch cut
        # Rear wheel arch rear edge (Y = 1.680)
        (1.680, 0.86, 0.88, 0.55, 0.20, 0.86, 1.425, 1.430),
        # Rear roof spoiler / hatch top (Y = 1.850)
        (1.850, 0.84, 0.86, 0.52, 0.21, 0.84, 1.410, 1.415),
        # Tailgate mid / taillights (Y = 2.050)
        (2.050, 0.80, 0.82, 0.45, 0.22, 0.78, 1.050, 1.060),
        # Rear bumper sill / tailgate base (Y = 2.150)
        (2.150, 0.76, 0.78, 0.38, 0.23, 0.72, 0.750, 0.760),
        # Rear bumper tip (Y = 2.181)
        (2.181, 0.70, 0.72, 0.30, 0.24, 0.55, 0.620, 0.630),
    ]
    
    body_rings = []
    for (y, w_rock, w_torn, w_roof, z_rock, z_torn, z_roof, z_cen) in sections_def:
        ring = []
        # Points along cross-section:
        # Right side:
        p0 = (+w_rock, y, z_rock)                               # Rocker bottom
        p1 = (+w_torn * 0.98, y, z_rock + (z_torn - z_rock)*0.5) # Lower door flare
        p2 = (+w_torn, y, z_torn)                               # Tornado character crease
        p3 = (+w_torn * 0.92, y, z_torn + (z_roof - z_torn)*0.3) # Shoulder / beltline
        p4 = (+w_roof, y, z_roof)                               # Roof / hood edge
        p5 = (+w_roof * 0.40, y, z_roof + (z_cen - z_roof)*0.8)  # Power dome right
        p6 = (0.0, y, z_cen)                                    # Centerline
        # Left side (mirrored):
        p7 = (-w_roof * 0.40, y, z_roof + (z_cen - z_roof)*0.8)  # Power dome left
        p8 = (-w_roof, y, z_roof)                               # Roof / hood edge
        p9 = (-w_torn * 0.92, y, z_torn + (z_roof - z_torn)*0.3) # Shoulder / beltline
        p10 = (-w_torn, y, z_torn)                              # Tornado character crease
        p11 = (-w_torn * 0.98, y, z_rock + (z_torn - z_rock)*0.5)
        p12 = (-w_rock, y, z_rock)                              # Rocker bottom
        
        pts = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]
        ring_verts = [bm_body.verts.new(p) for p in pts]
        body_rings.append(ring_verts)
        
    # Connect rings with quads
    for s_idx in range(len(sections_def) - 1):
        r1 = body_rings[s_idx]
        r2 = body_rings[s_idx + 1]
        for v_idx in range(len(r1) - 1):
            bm_body.faces.new([r1[v_idx], r1[v_idx + 1], r2[v_idx + 1], r2[v_idx]])
            
    # Front nose cap
    front_center = bm_body.verts.new((0.0, -2.181, 0.45))
    r_front = body_rings[0]
    for v_idx in range(len(r_front) - 1):
        bm_body.faces.new([r_front[v_idx], front_center, r_front[v_idx + 1]])
        
    # Rear bumper cap
    rear_center = bm_body.verts.new((0.0, 2.181, 0.45))
    r_rear = body_rings[-1]
    for v_idx in range(len(r_rear) - 1):
        bm_body.faces.new([r_rear[v_idx], r_rear[v_idx + 1], rear_center])
        
    obj_body = finish_mesh(bm_body, "Scala_Body_Shell", [mat_velvet_red])
    
    # Add subtle Bevel modifier for sharp automotive edge highlights
    bev = obj_body.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.008
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)

    # ---------------------------------------------------------
    # 3. MONTE CARLO BLACK MAGIC TRIM & GLASSHOUSE
    # ---------------------------------------------------------
    bm_trim = bmesh.new()
    
    # A. Panoramic Black Roof & Pillars
    # Covers upper canopy from cowl (Y = -0.85) to rear spoiler (Y = 1.95)
    roof_y = [-0.85, -0.40, 0.10, 0.70, 1.20, 1.65, 1.88, 1.98]
    roof_w = [0.74, 0.64, 0.62, 0.61, 0.58, 0.54, 0.53, 0.54]
    roof_z = [0.91, 1.26, 1.475, 1.470, 1.450, 1.435, 1.425, 1.435] # slightly above body
    
    roof_rings = []
    for y, w, z in zip(roof_y, roof_w, roof_z):
        pts = [
            (+w, y, z - 0.01),
            (+w * 0.5, y, z),
            (0.0, y, z + 0.005),
            (-w * 0.5, y, z),
            (-w, y, z - 0.01)
        ]
        roof_rings.append([bm_trim.verts.new(p) for p in pts])
        
    for i in range(len(roof_rings) - 1):
        r1 = roof_rings[i]
        r2 = roof_rings[i + 1]
        for j in range(len(r1) - 1):
            bm_trim.faces.new([r1[j], r1[j + 1], r2[j + 1], r2[j]])
            
    # Rear Roof Spoiler extension with side fins
    # Spoiler lip extends over the rear window
    sp_verts = [
        bm_trim.verts.new((+0.54, 1.88, 1.425)),
        bm_trim.verts.new((+0.54, 2.02, 1.435)),
        bm_trim.verts.new((0.0, 2.00, 1.440)),
        bm_trim.verts.new((-0.54, 2.02, 1.435)),
        bm_trim.verts.new((-0.54, 1.88, 1.425)),
    ]
    bm_trim.faces.new([sp_verts[0], sp_verts[1], sp_verts[2], roof_rings[-1][2], roof_rings[-1][1], roof_rings[-1][0]])
    bm_trim.faces.new([sp_verts[2], sp_verts[3], sp_verts[4], roof_rings[-1][4], roof_rings[-1][3]])
    
    # B. Shark-fin Antenna on rear roof (Y = 1.62, Z = 1.44)
    antenna_pts = [
        (0.0, 1.55, 1.44),
        (+0.025, 1.68, 1.44),
        (0.0, 1.72, 1.44),
        (-0.025, 1.68, 1.44),
        (0.0, 1.66, 1.51) # tip
    ]
    av = [bm_trim.verts.new(p) for p in antenna_pts]
    bm_trim.faces.new([av[0], av[1], av[2], av[3]])
    bm_trim.faces.new([av[0], av[4], av[1]])
    bm_trim.faces.new([av[1], av[4], av[2]])
    bm_trim.faces.new([av[2], av[4], av[3]])
    bm_trim.faces.new([av[3], av[4], av[0]])
    
    # C. Front Facelift Hexagonal Grille Frame & Slat Assembly
    # Octagonal upright grille surround at Y = -2.06..-2.02, Z = 0.55..0.74
    grille_outer = [
        (+0.46, -2.03, 0.73),
        (+0.48, -2.05, 0.64),
        (+0.38, -2.07, 0.55),
        (-0.38, -2.07, 0.55),
        (-0.48, -2.05, 0.64),
        (-0.46, -2.03, 0.73),
        (0.0, -2.02, 0.75) # center chevron peak
    ]
    grille_inner = [
        (+0.42, -2.04, 0.71),
        (+0.44, -2.06, 0.64),
        (+0.35, -2.08, 0.57),
        (-0.35, -2.08, 0.57),
        (-0.44, -2.06, 0.64),
        (-0.42, -2.04, 0.71),
        (0.0, -2.03, 0.73)
    ]
    gov = [bm_trim.verts.new(p) for p in grille_outer]
    giv = [bm_trim.verts.new(p) for p in grille_inner]
    for i in range(len(gov)):
        i_next = (i + 1) % len(gov)
        bm_trim.faces.new([gov[i], gov[i_next], giv[i_next], giv[i]])
        
    # Vertical grille twin slats (14 slats)
    for slat_i in range(-6, 7):
        slat_x = slat_i * 0.055
        slat_top_z = 0.72 - abs(slat_i)*0.015
        slat_bot_z = 0.57
        if abs(slat_x) < 0.08:
            # Skip center for radar block
            continue
        v_s1 = bm_trim.verts.new((slat_x - 0.006, -2.04, slat_bot_z))
        v_s2 = bm_trim.verts.new((slat_x + 0.006, -2.04, slat_bot_z))
        v_s3 = bm_trim.verts.new((slat_x + 0.006, -2.02, slat_top_z))
        v_s4 = bm_trim.verts.new((slat_x - 0.006, -2.02, slat_top_z))
        bm_trim.faces.new([v_s1, v_s2, v_s3, v_s4])
        
    # Center Radar Sensor Box (gloss black plate)
    radar_box = [
        (+0.065, -2.04, 0.60),
        (+0.065, -2.04, 0.70),
        (-0.065, -2.04, 0.70),
        (-0.065, -2.04, 0.60)
    ]
    rbv = [bm_trim.verts.new(p) for p in radar_box]
    bm_trim.faces.new(rbv)
    
    # D. Front Bumper Aerodynamic Chin Splitter Spoiler
    # Extends along bottom edge at Y = -2.181 with side winglets
    spl_pts_outer = [
        (+0.80, -2.10, 0.25), # Right winglet
        (+0.76, -2.18, 0.20),
        (+0.40, -2.20, 0.19),
        (0.00, -2.21, 0.19),
        (-0.40, -2.20, 0.19),
        (-0.76, -2.18, 0.20),
        (-0.80, -2.10, 0.25)  # Left winglet
    ]
    spl_pts_inner = [
        (+0.76, -2.08, 0.22),
        (+0.72, -2.15, 0.21),
        (+0.38, -2.17, 0.20),
        (0.00, -2.18, 0.20),
        (-0.38, -2.17, 0.20),
        (-0.72, -2.15, 0.21),
        (-0.76, -2.08, 0.22)
    ]
    sov = [bm_trim.verts.new(p) for p in spl_pts_outer]
    siv = [bm_trim.verts.new(p) for p in spl_pts_inner]
    for i in range(len(sov) - 1):
        bm_trim.faces.new([sov[i], sov[i + 1], siv[i + 1], siv[i]])
        
    # E. Monte Carlo Side Skirt Blades (along lower rockers)
    for sign in [+1, -1]:
        skirt_pts = [
            (sign * 0.88, -0.95, 0.19),
            (sign * 0.90, -0.95, 0.18),
            (sign * 0.90, +0.95, 0.18),
            (sign * 0.88, +0.95, 0.19)
        ]
        skv = [bm_trim.verts.new(p) for p in skirt_pts]
        bm_trim.faces.new(skv if sign > 0 else skv[::-1])
        
    # F. Rear Bumper Aerodynamic Diffuser with Fins
    diff_pts_top = [
        (+0.65, 2.14, 0.35),
        (+0.35, 2.16, 0.35),
        (-0.35, 2.16, 0.35),
        (-0.65, 2.14, 0.35)
    ]
    diff_pts_bot = [
        (+0.62, 2.06, 0.22),
        (+0.35, 2.05, 0.22),
        (-0.35, 2.05, 0.22),
        (-0.62, 2.06, 0.22)
    ]
    dtv = [bm_trim.verts.new(p) for p in diff_pts_top]
    dbv = [bm_trim.verts.new(p) for p in diff_pts_bot]
    for i in range(len(dtv) - 1):
        bm_trim.faces.new([dtv[i], dtv[i + 1], dbv[i + 1], dbv[i]])
    # 4 vertical fins
    for fin_x in [-0.25, -0.08, 0.08, 0.25]:
        fv = [
            bm_trim.verts.new((fin_x, 2.16, 0.35)),
            bm_trim.verts.new((fin_x, 2.05, 0.22)),
            bm_trim.verts.new((fin_x, 2.03, 0.20)),
            bm_trim.verts.new((fin_x, 2.14, 0.33))
        ]
        bm_trim.faces.new(fv)
        
    # G. Side Mirrors (Aerodynamic Monte Carlo black caps)
    for sign in [+1, -1]:
        m_arm = [
            (sign * 0.87, -0.90, 0.92),
            (sign * 0.92, -0.91, 0.94),
            (sign * 0.92, -0.87, 0.94),
            (sign * 0.87, -0.86, 0.92)
        ]
        mav = [bm_trim.verts.new(p) for p in m_arm]
        bm_trim.faces.new(mav if sign > 0 else mav[::-1])
        
        # Mirror cap shell
        m_box = [
            (sign * 0.92, -0.93, 0.91),
            (sign * 1.01, -0.95, 0.92),
            (sign * 1.02, -0.84, 0.94),
            (sign * 0.92, -0.84, 0.93),
            (sign * 0.92, -0.93, 0.99),
            (sign * 1.01, -0.95, 1.00),
            (sign * 1.02, -0.84, 1.01),
            (sign * 0.92, -0.84, 1.00)
        ]
        mbv = [bm_trim.verts.new(p) for p in m_box]
        # 6 faces of mirror cap
        m_cap_faces = [
            [mbv[0], mbv[1], mbv[2], mbv[3]],
            [mbv[4], mbv[7], mbv[6], mbv[5]],
            [mbv[0], mbv[4], mbv[5], mbv[1]],
            [mbv[2], mbv[6], mbv[7], mbv[3]],
            [mbv[1], mbv[5], mbv[6], mbv[2]], # outer face
            [mbv[0], mbv[3], mbv[7], mbv[4]]  # mirror glass side
        ]
        for cf in m_cap_faces:
            bm_trim.faces.new(cf if sign > 0 else cf[::-1])

    obj_trim = finish_mesh(bm_trim, "Scala_Monte_Carlo_Trim", [mat_black_magic])

    # ---------------------------------------------------------
    # 4. WINDOWS & GLASS (Clear & Sunset Privacy Glass)
    # ---------------------------------------------------------
    bm_glass = bmesh.new()
    uv_glass = bm_glass.loops.layers.uv.verify()
    
    # A. Front Windshield (Clear Glass)
    # Slopes from cowl (Y = -0.85, Z = 0.91) to header (Y = -0.40, Z = 1.26)
    ws_pts = [
        (+0.72, -0.85, 0.91),
        (+0.62, -0.40, 1.26),
        (-0.62, -0.40, 1.26),
        (-0.72, -0.85, 0.91)
    ]
    wsv = [bm_glass.verts.new(p) for p in ws_pts]
    f_ws = bm_glass.faces.new(wsv)
    f_ws.material_index = 0 # Glass Clear
    
    # B. Front Side Windows (Clear Glass)
    for sign in [+1, -1]:
        fsw_pts = [
            (sign * 0.86, -0.82, 0.90),
            (sign * 0.63, -0.38, 1.25),
            (sign * 0.61, +0.10, 1.45),
            (sign * 0.88, +0.10, 0.89)
        ]
        fsw_v = [bm_glass.verts.new(p) for p in fsw_pts]
        f = bm_glass.faces.new(fsw_v if sign > 0 else fsw_v[::-1])
        f.material_index = 0 # Glass Clear
        
    # C. Rear Side Windows (Sunset Privacy Dark Glass)
    for sign in [+1, -1]:
        rsw_pts = [
            (sign * 0.88, +0.10, 0.89),
            (sign * 0.61, +0.10, 1.45),
            (sign * 0.58, +0.85, 1.44),
            (sign * 0.53, +1.45, 1.35),
            (sign * 0.86, +1.40, 0.88)
        ]
        rsw_v = [bm_glass.verts.new(p) for p in rsw_pts]
        f = bm_glass.faces.new(rsw_v if sign > 0 else rsw_v[::-1])
        f.material_index = 1 # Privacy Glass
        
    # D. Extended Glass Tailgate (Sunset Privacy Glass - Signature Scala Feature!)
    # Slopes down from spoiler (Y = 1.88, Z = 1.41) to tailgate mid (Y = 2.08, Z = 0.85)
    hatch_pts = [
        (+0.52, 1.88, 1.41),
        (+0.42, 2.08, 0.85),
        (-0.42, 2.08, 0.85),
        (-0.52, 1.88, 1.41)
    ]
    hv = [bm_glass.verts.new(p) for p in hatch_pts]
    f_hatch = bm_glass.faces.new(hv)
    f_hatch.material_index = 1 # Privacy Glass
    
    obj_glass = finish_mesh(bm_glass, "Scala_Windows_Glass", [mat_glass_clear, mat_glass_privacy])

    # ---------------------------------------------------------
    # 5. MATRIX LED HEADLIGHTS & TAILLIGHTS
    # ---------------------------------------------------------
    bm_lights = bmesh.new()
    
    # Headlights: Facelift crystalline Matrix LED
    for sign in [+1, -1]:
        # Headlight lens wedge: X in [0.46, 0.82], Y in [-2.04, -1.88], Z in [0.63, 0.74]
        hl_lens = [
            (sign * 0.46, -2.03, 0.72),
            (sign * 0.82, -1.86, 0.76),
            (sign * 0.80, -1.90, 0.65),
            (sign * 0.47, -2.04, 0.63)
        ]
        hlv = [bm_lights.verts.new(p) for p in hl_lens]
        f_hl = bm_lights.faces.new(hlv if sign > 0 else hlv[::-1])
        f_hl.material_index = 0 # Headlight Glass / Chrome
        
        # Upper LED DRL light guide brow (emissive crisp white)
        drl_pts = [
            (sign * 0.47, -2.03, 0.715),
            (sign * 0.81, -1.86, 0.755),
            (sign * 0.80, -1.87, 0.735),
            (sign * 0.48, -2.03, 0.700)
        ]
        drl_v = [bm_lights.verts.new(p) for p in drl_pts]
        f_drl = bm_lights.faces.new(drl_v if sign > 0 else drl_v[::-1])
        f_drl.material_index = 1 # LED DRL emission
        
        # Dual Bi-LED projection lenses inside
        for p_offset in [0.0, 0.12]:
            lens_x = sign * (0.58 + p_offset)
            lens_y = -1.95 + p_offset * 0.35
            lens_v = [
                (lens_x - sign*0.035, lens_y, 0.66),
                (lens_x + sign*0.035, lens_y, 0.66),
                (lens_x + sign*0.035, lens_y, 0.70),
                (lens_x - sign*0.035, lens_y, 0.70)
            ]
            lv = [bm_lights.verts.new(p) for p in lens_v]
            f_proj = bm_lights.faces.new(lv if sign > 0 else lv[::-1])
            f_proj.material_index = 2 # Chrome projector bezel
            
    # Taillights: C-shaped crystalline LED
    for sign in [+1, -1]:
        tl_pts = [
            (sign * 0.45, 2.06, 0.88),
            (sign * 0.82, 1.95, 0.86),
            (sign * 0.84, 1.96, 0.76),
            (sign * 0.50, 2.08, 0.75),
            (sign * 0.50, 2.07, 0.82),
            (sign * 0.76, 1.98, 0.82)
        ]
        # C-shape outer quad
        tv = [bm_lights.verts.new(p) for p in tl_pts]
        f_tl1 = bm_lights.faces.new([tv[0], tv[1], tv[5], tv[4]] if sign > 0 else [tv[4], tv[5], tv[1], tv[0]])
        f_tl2 = bm_lights.faces.new([tv[4], tv[5], tv[2], tv[3]] if sign > 0 else [tv[3], tv[2], tv[5], tv[4]])
        f_tl1.material_index = 3 # Red Taillight Glass
        f_tl2.material_index = 3
        
    obj_lights = finish_mesh(bm_lights, "Scala_Lights_LED", [mat_glass_clear, mat_led_drl, mat_headlight_chrome, mat_taillight_glass])

    # ---------------------------------------------------------
    # 6. AUTHENTIC CZECH LICENSE PLATES (1AH U743)
    # ---------------------------------------------------------
    bm_plates = bmesh.new()
    uv_plate = bm_plates.loops.layers.uv.verify()
    
    # Plate dimensions: 520mm x 110mm (plus mounting frame)
    plate_w = 0.52
    plate_h = 0.115
    
    # A. Front Plate (mounted on bumper at Y = -2.16, Z = 0.42)
    fp_v = [
        bm_plates.verts.new((+plate_w * 0.5, -2.16, 0.42 - plate_h * 0.5)),
        bm_plates.verts.new((-plate_w * 0.5, -2.16, 0.42 - plate_h * 0.5)),
        bm_plates.verts.new((-plate_w * 0.5, -2.15, 0.42 + plate_h * 0.5)),
        bm_plates.verts.new((+plate_w * 0.5, -2.15, 0.42 + plate_h * 0.5))
    ]
    f_fp = bm_plates.faces.new(fp_v)
    f_fp.loops[0][uv_plate].uv = (0.0, 0.0)
    f_fp.loops[1][uv_plate].uv = (1.0, 0.0)
    f_fp.loops[2][uv_plate].uv = (1.0, 1.0)
    f_fp.loops[3][uv_plate].uv = (0.0, 1.0)
    f_fp.material_index = 0
    
    # B. Rear Plate (mounted on tailgate recess at Y = 2.16, Z = 0.58)
    rp_v = [
        bm_plates.verts.new((-plate_w * 0.5, 2.16, 0.58 - plate_h * 0.5)),
        bm_plates.verts.new((+plate_w * 0.5, 2.16, 0.58 - plate_h * 0.5)),
        bm_plates.verts.new((+plate_w * 0.5, 2.15, 0.58 + plate_h * 0.5)),
        bm_plates.verts.new((-plate_w * 0.5, 2.15, 0.58 + plate_h * 0.5))
    ]
    f_rp = bm_plates.faces.new(rp_v)
    f_rp.loops[0][uv_plate].uv = (0.0, 0.0)
    f_rp.loops[1][uv_plate].uv = (1.0, 0.0)
    f_rp.loops[2][uv_plate].uv = (1.0, 1.0)
    f_rp.loops[3][uv_plate].uv = (0.0, 1.0)
    f_rp.material_index = 0
    
    obj_plates = finish_mesh(bm_plates, "Scala_License_Plates", [mat_plate])

    # ---------------------------------------------------------
    # 7. ŠKODA ROUNDEL EMBLEM & LETTERING
    # ---------------------------------------------------------
    bm_emblem = bmesh.new()
    
    # Front Hood Nose Emblem (radius 45mm, at Y = -1.96, Z = 0.775)
    R_emb = 0.045
    emb_cen = mathutils.Vector((0.0, -1.96, 0.775))
    emb_norm = mathutils.Vector((0.0, -0.6, 0.8)).normalized()
    
    emb_ring = []
    for i in range(16):
        ang = 2.0 * math.pi * i / 16
        dx = R_emb * math.cos(ang)
        dz = R_emb * math.sin(ang) * 0.6
        dy = dz * 0.7
        emb_ring.append(bm_emblem.verts.new((emb_cen.x + dx, emb_cen.y - dy, emb_cen.z + dz)))
        
    emb_cen_v = bm_emblem.verts.new(emb_cen)
    for i in range(16):
        i_next = (i + 1) % 16
        f = bm_emblem.faces.new([emb_ring[i], emb_ring[i_next], emb_cen_v])
        f.material_index = 0 # Chrome
        
    # Winged Arrow 3D relief
    arrow_v = [
        bm_emblem.verts.new((0.0, emb_cen.y - 0.005, emb_cen.z + 0.025)),
        bm_emblem.verts.new((0.02, emb_cen.y - 0.004, emb_cen.z - 0.015)),
        bm_emblem.verts.new((-0.02, emb_cen.y - 0.004, emb_cen.z - 0.015)),
    ]
    f_arr = bm_emblem.faces.new(arrow_v)
    f_arr.material_index = 0 # Chrome
    
    obj_emblem = finish_mesh(bm_emblem, "Scala_Emblem_Front", [mat_chrome, mat_black_magic])

    # ---------------------------------------------------------
    # 8. VISIBLE INTERIOR COCKPIT (Dashboard & Sports Seats)
    # ---------------------------------------------------------
    bm_int = bmesh.new()
    
    # Dashboard Cowl
    dash_box = [
        (+0.65, -0.75, 0.88),
        (+0.65, -0.55, 0.88),
        (-0.65, -0.55, 0.88),
        (-0.65, -0.75, 0.88),
        (+0.62, -0.75, 0.94),
        (+0.62, -0.55, 0.93),
        (-0.62, -0.55, 0.93),
        (-0.62, -0.75, 0.94),
    ]
    dv = [bm_int.verts.new(p) for p in dash_box]
    for face_idx in [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [2, 6, 7, 3], [1, 5, 6, 2], [0, 3, 7, 4]]:
        f = bm_int.faces.new([dv[i] for i in face_idx])
        f.material_index = 0 # Dark interior
        
    # 9.2" Central Infotainment Tablet Display standing proud
    screen_pts = [
        (+0.12, -0.62, 0.94),
        (+0.12, -0.62, 1.04),
        (-0.12, -0.62, 1.04),
        (-0.12, -0.62, 0.94)
    ]
    sv = [bm_int.verts.new(p) for p in screen_pts]
    f_screen = bm_int.faces.new(sv)
    f_screen.material_index = 0
    
    # Sports 3-Spoke Steering Wheel at Driver side (X = -0.38, Y = -0.48, Z = 0.95)
    sw_cen = (-0.38, -0.48, 0.95)
    sw_ring = []
    R_sw = 0.17
    for i in range(16):
        ang = 2.0 * math.pi * i / 16
        dx = R_sw * math.cos(ang)
        dz = R_sw * math.sin(ang) * 0.7
        dy = dz * 0.7
        sw_ring.append(bm_int.verts.new((sw_cen[0] + dx, sw_cen[1] - dy, sw_cen[2] + dz)))
    for i in range(16):
        i_next = (i + 1) % 16
        f = bm_int.faces.new([sw_ring[i], sw_ring[i_next], bm_int.verts.new((sw_cen[0], sw_cen[1], sw_cen[2]))])
        f.material_index = 0
        
    # Monte Carlo Sports Bucket Seats (Driver & Passenger)
    # With integrated high headrest and red/white vertical center stripe!
    for seat_x in [-0.38, +0.38]:
        # Seat backrest
        sb_pts = [
            (seat_x - 0.22, -0.15, 0.50),
            (seat_x + 0.22, -0.15, 0.50),
            (seat_x + 0.18, +0.10, 1.15),
            (seat_x - 0.18, +0.10, 1.15)
        ]
        sb_v = [bm_int.verts.new(p) for p in sb_pts]
        f_sb = bm_int.faces.new(sb_v)
        f_sb.material_index = 0 # Dark interior
        
        # Center vertical racing stripe (Monte Carlo Red)
        stripe_pts = [
            (seat_x - 0.04, -0.148, 0.50),
            (seat_x + 0.04, -0.148, 0.50),
            (seat_x + 0.03, +0.102, 1.15),
            (seat_x - 0.03, +0.102, 1.15)
        ]
        stv = [bm_int.verts.new(p) for p in stripe_pts]
        f_stripe = bm_int.faces.new(stv)
        f_stripe.material_index = 1 # Red accent stripe
        
    obj_interior = finish_mesh(bm_int, "Scala_Interior", [mat_interior, mat_seat_accent_red])

    # ---------------------------------------------------------
    # 9. 4x COMPLETE WHEELS (Monte Carlo 17" Kajam Aero)
    # ---------------------------------------------------------
    def build_wheel_mesh(name, is_left=True):
        bm = bmesh.new()
        
        R_outer = 0.317  # 634mm tyre diameter
        R_rim = 0.216    # 17" rim (432mm)
        R_hub = 0.055
        tyre_width = 0.215
        
        # 1. Tyre
        num_radial = 36
        profile = [
            (R_rim, -tyre_width * 0.5),
            (R_rim + 0.015, -tyre_width * 0.52),
            (R_outer - 0.025, -tyre_width * 0.51),
            (R_outer - 0.008, -tyre_width * 0.45),
            (R_outer, -tyre_width * 0.30),
            (R_outer, tyre_width * 0.30),
            (R_outer - 0.008, tyre_width * 0.45),
            (R_outer - 0.025, tyre_width * 0.51),
            (R_rim + 0.015, tyre_width * 0.52),
            (R_rim, tyre_width * 0.5),
        ]
        
        tyre_ring_verts = []
        for r, w in profile:
            ring = []
            for i in range(num_radial):
                theta = 2.0 * math.pi * i / num_radial
                y = w
                z = r * math.cos(theta)
                x = r * math.sin(theta)
                ring.append(bm.verts.new((x, y, z)))
            tyre_ring_verts.append(ring)
            
        for p_idx in range(len(profile) - 1):
            for i in range(num_radial):
                i_next = (i + 1) % num_radial
                bm.faces.new([
                    tyre_ring_verts[p_idx][i],
                    tyre_ring_verts[p_idx][i_next],
                    tyre_ring_verts[p_idx + 1][i_next],
                    tyre_ring_verts[p_idx + 1][i]
                ])
                
        for f in bm.faces:
            f.material_index = 0 # Tyre Rubber
            
        # 2. Rim Outer Polished Lip (Diamond Cut)
        rim_outer_ring = []
        rim_inner_ring = []
        for i in range(num_radial):
            theta = 2.0 * math.pi * i / num_radial
            z_out = R_rim * math.cos(theta)
            x_out = R_rim * math.sin(theta)
            z_in = (R_rim - 0.018) * math.cos(theta)
            x_in = (R_rim - 0.018) * math.sin(theta)
            y_face = -tyre_width * 0.48 if is_left else tyre_width * 0.48
            y_lip = -tyre_width * 0.45 if is_left else tyre_width * 0.45
            rim_outer_ring.append(bm.verts.new((x_out, y_face, z_out)))
            rim_inner_ring.append(bm.verts.new((x_in, y_lip, z_in)))
            
        for i in range(num_radial):
            i_next = (i + 1) % num_radial
            f = bm.faces.new([rim_outer_ring[i], rim_outer_ring[i_next], rim_inner_ring[i_next], rim_inner_ring[i]])
            f.material_index = 1 # Chrome / Diamond cut silver
            
        # 3. Five Turbine Blades / Spokes (Monte Carlo Aero Kajam)
        hub_verts = []
        for i in range(num_radial):
            theta = 2.0 * math.pi * i / num_radial
            z_hub = R_hub * math.cos(theta)
            x_hub = R_hub * math.sin(theta)
            y_hub = -tyre_width * 0.42 if is_left else tyre_width * 0.42
            hub_verts.append(bm.verts.new((x_hub, y_hub, z_hub)))
            
        hub_center = bm.verts.new((0.0, -tyre_width * 0.43 if is_left else tyre_width * 0.43, 0.0))
        for i in range(num_radial):
            i_next = (i + 1) % num_radial
            f = bm.faces.new([hub_verts[i], hub_verts[i_next], hub_center])
            f.material_index = 2 # Black Magic hub cap
            
        for s in range(5):
            idx_rim_start = int((s / 5.0) * num_radial)
            idx_rim_end = int(((s + 0.6) / 5.0) * num_radial) % num_radial
            idx_hub_start = int((s / 5.0) * num_radial)
            idx_hub_end = int(((s + 0.6) / 5.0) * num_radial) % num_radial
            
            f_spoke = bm.faces.new([
                rim_inner_ring[idx_rim_start],
                rim_inner_ring[idx_rim_end],
                hub_verts[idx_hub_end],
                hub_verts[idx_hub_start]
            ])
            f_spoke.material_index = 2 # Black Magic
            
            idx_aero_end = int(((s + 1.0) / 5.0) * num_radial) % num_radial
            f_aero = bm.faces.new([
                rim_inner_ring[idx_rim_end],
                rim_inner_ring[idx_aero_end],
                hub_verts[idx_aero_end],
                hub_verts[idx_hub_end]
            ])
            f_aero.material_index = 3 # Plastic Matte (Aero insert)
            
        # 4. Brake Disc inside
        R_disc = 0.165
        R_disc_in = 0.08
        disc_y = -tyre_width * 0.25 if is_left else tyre_width * 0.25
        disc_outer = []
        disc_inner = []
        for i in range(24):
            theta = 2.0 * math.pi * i / 24
            disc_outer.append(bm.verts.new((R_disc * math.sin(theta), disc_y, R_disc * math.cos(theta))))
            disc_inner.append(bm.verts.new((R_disc_in * math.sin(theta), disc_y, R_disc_in * math.cos(theta))))
        for i in range(24):
            i_next = (i + 1) % 24
            f = bm.faces.new([disc_outer[i], disc_outer[i_next], disc_inner[i_next], disc_inner[i]])
            f.material_index = 4 # Brake Disc steel
            
        # Brake caliper
        caliper_y = -tyre_width * 0.28 if is_left else tyre_width * 0.28
        caliper_box = [
            (0.12, caliper_y - 0.02, 0.10),
            (0.18, caliper_y - 0.02, 0.10),
            (0.18, caliper_y + 0.02, 0.10),
            (0.12, caliper_y + 0.02, 0.10),
            (0.12, caliper_y - 0.02, 0.18),
            (0.18, caliper_y - 0.02, 0.18),
            (0.18, caliper_y + 0.02, 0.18),
            (0.12, caliper_y + 0.02, 0.18),
        ]
        cv = [bm.verts.new(p) for p in caliper_box]
        for cf in [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]]:
            f = bm.faces.new([cv[idx] for idx in cf])
            f.material_index = 2 # Black Magic caliper
            
        obj_w = finish_mesh(bm, name, [mat_tyre_rubber, mat_chrome, mat_black_magic, mat_plastic_matte, mat_brake_disc])
        return obj_w

    wheel_FL = build_wheel_mesh("Scala_Wheel_FL", is_left=True)
    wheel_FL.location = (-0.765, -1.325, 0.317)
    
    wheel_FR = build_wheel_mesh("Scala_Wheel_FR", is_left=False)
    wheel_FR.location = (+0.765, -1.325, 0.317)
    
    wheel_RL = build_wheel_mesh("Scala_Wheel_RL", is_left=True)
    wheel_RL.location = (-0.758, +1.324, 0.317)
    
    wheel_RR = build_wheel_mesh("Scala_Wheel_RR", is_left=False)
    wheel_RR.location = (+0.758, +1.324, 0.317)

    # ---------------------------------------------------------
    # 10. ROOT EMPTY HIERARCHY & POSITIONING
    # ---------------------------------------------------------
    empty_car = bpy.data.objects.new("Skoda_Scala_Monte_Carlo_Root", None)
    empty_car.empty_display_type = 'ARROWS'
    empty_car.empty_display_size = 1.0
    collection_target.objects.link(empty_car)
    
    car_children = [
        obj_body, obj_trim, obj_glass, obj_lights, obj_plates, obj_emblem, obj_interior,
        wheel_FL, wheel_FR, wheel_RL, wheel_RR
    ]
    for child in car_children:
        child.parent = empty_car
        
    # Set final world placement
    empty_car.location = car_loc
    empty_car.rotation_euler.z = car_rot_z
    
    print(f"Skoda Scala Monte Carlo assembled successfully with {len(car_children)} component objects!")
    return empty_car

if __name__ == "__main__":
    build_skoda_scala(bpy.context.scene.collection)
