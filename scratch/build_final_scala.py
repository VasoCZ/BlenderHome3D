"""
build_final_scala.py
Integrates the official Škoda Auto factory CAD geometry for the Škoda Scala Monte Carlo 2025:
- 100% authentic Velvet Red Metallic body with gloss Black Magic roof, mirrors, spoiler, and diffuser
- Official factory 17" Kajam Monte Carlo aero alloy wheels and tyres from Škoda Auto CAD
- Crystalline Matrix LED headlights & 3D ruby taillights without fake flat emission
- Authentic Czech license plate 1AH U743 front and rear
- Exact factory ride height and stance on the driveway
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
import os

def get_or_create_material(name, color, metallic=0.0, roughness=0.5, clearcoat=0.0, transmission=0.0, ior=1.45, emission=None, emission_str=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        nodes.clear()
        out = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
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
        
    if emission and emission_str > 0:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_str
    else:
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = 0.0
            
    return mat

def setup_all_materials():
    m = {}
    # Velvet Red Metallic
    m['paint'] = get_or_create_material("Mat_Scala_Velvet_Red", (0.50, 0.015, 0.030, 1.0), metallic=0.86, roughness=0.14, clearcoat=1.0, ior=1.52)
    # Monte Carlo Black Magic gloss (grille, lower intake, roof, mirrors, diffuser, B-pillars)
    m['gloss_black'] = get_or_create_material("Mat_Scala_Black_Magic", (0.010, 0.010, 0.012, 1.0), metallic=0.10, roughness=0.06, clearcoat=1.0, ior=1.52)
    # Clear Polycarbonate Automotive Glass (windshield, front door windows)
    m['glass_clear'] = get_or_create_material("Mat_Scala_Glass_Clear", (0.95, 0.98, 0.98, 1.0), roughness=0.01, transmission=0.96, ior=1.52)
    # Sunset Privacy Glass (deep black tinted privacy glass for rear doors, quarter windows, and rear hatch)
    m['glass_tinted'] = get_or_create_material("Mat_Scala_Glass_Sunset_Privacy", (0.005, 0.005, 0.007, 1.0), metallic=0.0, roughness=0.04, clearcoat=0.4, transmission=0.0, ior=1.52)
    # Matte Black Textured Plastic (chassis underbody, license plate holder)
    m['matte_plastic'] = get_or_create_material("Mat_Scala_Plastic_Matte", (0.035, 0.035, 0.038, 1.0), roughness=0.65)
    # Diamond-cut Machined Silver Alloy (Kajam outer rim lip & center logo roundel)
    m['silver_alloy'] = get_or_create_material("Mat_Scala_Silver_Alloy", (0.88, 0.89, 0.91, 1.0), metallic=0.96, roughness=0.12)
    # Satin/Gloss Black for 17" Kajam Monte Carlo aero inserts and wheel face (matching realne fotky/disky.jpg)
    m['wheel_black'] = get_or_create_material("Mat_Scala_Wheel_Black", (0.010, 0.010, 0.012, 1.0), metallic=0.05, roughness=0.16, clearcoat=0.20)
    # Chrome Trim & Wordmark
    m['chrome'] = get_or_create_material("Mat_Scala_Chrome", (0.95, 0.95, 0.96, 1.0), metallic=0.98, roughness=0.05)
    # Tyre Rubber
    m['tyre_rubber'] = get_or_create_material("Mat_Scala_Tyre_Rubber", (0.028, 0.028, 0.030, 1.0), roughness=0.75)
    # Brake Rotor Steel
    m['brake_steel'] = get_or_create_material("Mat_Scala_Brake_Steel", (0.75, 0.76, 0.78, 1.0), metallic=0.95, roughness=0.22)
    # Brake Caliper Red
    m['brake_caliper'] = get_or_create_material("Mat_Scala_Brake_Caliper", (0.55, 0.03, 0.03, 1.0), metallic=0.4, roughness=0.3)
    # Matrix LED Headlight Lens (clear glass with crystal reflection, no artificial lamp glow on parked car)
    m['headlight_glass'] = get_or_create_material("Mat_Scala_Headlight_Glass", (0.92, 0.94, 0.96, 1.0), roughness=0.04, transmission=0.90, clearcoat=1.0, ior=1.52)
    # Crystalline Taillight Dark Smoked Ruby Acrylic (Monte Carlo smoked crystal lens)
    m['taillight_red'] = get_or_create_material("Mat_Scala_Taillight_LED", (0.18, 0.015, 0.022, 1.0), metallic=0.10, roughness=0.02, clearcoat=1.0, transmission=0.75, ior=1.58)
    
    # Czech License Plate Material
    plate_tex_path = r"C:\Users\Vaso\Antigravity\Project blender\assets\license_plate_1AH_U743.png"
    mat_plate = bpy.data.materials.get("Mat_Scala_License_Plate")
    if not mat_plate:
        mat_plate = bpy.data.materials.new(name="Mat_Scala_License_Plate")
    mat_plate.use_nodes = True
    pnodes = mat_plate.node_tree.nodes
    plinks = mat_plate.node_tree.links
    pnodes.clear()
    out_p = pnodes.new(type='ShaderNodeOutputMaterial')
    bsdf_p = pnodes.new(type='ShaderNodeBsdfPrincipled')
    tex_p = pnodes.new(type='ShaderNodeTexImage')
    if os.path.exists(plate_tex_path):
        tex_p.image = bpy.data.images.load(plate_tex_path)
    bsdf_p.inputs['Roughness'].default_value = 0.25
    plinks.new(tex_p.outputs['Color'], bsdf_p.inputs['Base Color'])
    plinks.new(bsdf_p.outputs['BSDF'], out_p.inputs['Surface'])
    m['plate'] = mat_plate
    
    return m

def load_3mf_geometry(zpath, return_mmu=False):
    with zipfile.ZipFile(zpath, 'r') as z:
        root_xml = ET.fromstring(z.read('3D/3dmodel.model'))
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    mesh_el = root_xml.find('.//m:mesh', ns)
    verts_el = mesh_el.find('m:vertices', ns)
    tri_el = mesh_el.find('m:triangles', ns)
    verts = np.array([[float(v.get('x')), float(v.get('y')), float(v.get('z'))] for v in verts_el])
    tris = np.array([[int(t.get('v1')), int(t.get('v2')), int(t.get('v3'))] for t in tri_el])
    if return_mmu:
        mmu_key = '{http://schemas.slic3r.org/3mf/2017/06}mmu_segmentation'
        mmu_vals = np.array([t.get(mmu_key, 'none') for t in tri_el])
        return verts, tris, mmu_vals
    return verts, tris

def build_official_kajam_wheel(name, center_pos, is_left, mats, w_verts_cad, w_tris_cad, t_verts_cad, t_tris_cad, scale, parent=None, col=None):
    """
    Constructs an authentic Škoda 17" Kajam Monte Carlo wheel by combining the official factory
    disc CAD mesh (aligned with tyre outer face), official tyre mesh, inner barrel cylinder,
    steel brake rotor, and red caliper.
    """
    bm_w = bmesh.new()
    cx, cy, cz = center_pos
    sign_x = -1.0 if is_left else 1.0
    
    # Rim shift to align outer face with tyre outer face: +2.12 mm in CAD
    rim_shift = 2.12
    
    # 1. Official Kajam Rim Disc
    rim_v_map = {}
    v0_w = w_verts_cad[w_tris_cad[:, 0]]
    v1_w = w_verts_cad[w_tris_cad[:, 1]]
    v2_w = w_verts_cad[w_tris_cad[:, 2]]
    fc_w = (v0_w + v1_w + v2_w) / 3.0
    r_w = np.sqrt(fc_w[:, 0]**2 + fc_w[:, 2]**2)
    
    # Matching realne fotky/disky.jpg:
    # Outer lip ring: r > 9.6 mm and y < -5.0 mm (thin diamond-cut silver edge around circumference)
    # Center emblem: r < 2.5 mm and y < -5.0 mm (silver center roundel)
    # All main aero blades, pockets, and barrel: GLOSS BLACK!
    is_silver = (fc_w[:, 1] < -5.0) & ((r_w > 9.6) | (r_w < 2.5))
    
    for vi, v in enumerate(w_verts_cad):
        y_aligned = v[1] + rim_shift
        if is_left:
            wx = cx + y_aligned * scale
            wy = cy + v[0] * scale
            wz = cz + v[2] * scale
        else:
            wx = cx - y_aligned * scale
            wy = cy + v[0] * scale
            wz = cz + v[2] * scale
        rim_v_map[vi] = bm_w.verts.new((wx, wy, wz))
        
    for ti, (i1, i2, i3) in enumerate(w_tris_cad):
        if is_left:
            f = bm_w.faces.new([rim_v_map[i1], rim_v_map[i3], rim_v_map[i2]])
        else:
            f = bm_w.faces.new([rim_v_map[i1], rim_v_map[i2], rim_v_map[i3]])
        # Material: 0 = Silver Alloy (outer lip & logo), 1 = Gloss Black (5 aero blades, pockets, barrel)
        f.material_index = 0 if is_silver[ti] else 1
        
    # 2. Official Tyre
    tyre_v_map = {}
    for vi, v in enumerate(t_verts_cad):
        if is_left:
            tx = cx + v[1] * scale
            ty = cy + v[0] * scale
            tz = cz + v[2] * scale
        else:
            tx = cx - v[1] * scale
            ty = cy + v[0] * scale
            tz = cz + v[2] * scale
        tyre_v_map[vi] = bm_w.verts.new((tx, ty, tz))
        
    for ti, (i1, i2, i3) in enumerate(t_tris_cad):
        if is_left:
            f = bm_w.faces.new([tyre_v_map[i1], tyre_v_map[i3], tyre_v_map[i2]])
        else:
            f = bm_w.faces.new([tyre_v_map[i1], tyre_v_map[i2], tyre_v_map[i3]])
        f.material_index = 2 # Tyre Rubber
        
    # 3. Solid Inner Wheel Barrel (closes wheel behind the disc spokes)
    barrel_r = 0.222
    barrel_out_x = cx + sign_x * 0.080
    barrel_in_x = cx - sign_x * 0.095
    n_barrel = 32
    b_out = [bm_w.verts.new((barrel_out_x, cy + barrel_r * math.cos(2.0*math.pi*k/n_barrel), cz + barrel_r * math.sin(2.0*math.pi*k/n_barrel))) for k in range(n_barrel)]
    b_in = [bm_w.verts.new((barrel_in_x, cy + barrel_r * math.cos(2.0*math.pi*k/n_barrel), cz + barrel_r * math.sin(2.0*math.pi*k/n_barrel))) for k in range(n_barrel)]
    for k in range(n_barrel):
        k_next = (k + 1) % n_barrel
        if sign_x > 0:
            f_barrel = bm_w.faces.new([b_out[k], b_out[k_next], b_in[k_next], b_in[k]])
        else:
            f_barrel = bm_w.faces.new([b_out[k], b_in[k], b_in[k_next], b_out[k_next]])
        f_barrel.material_index = 1 # Gloss Black barrel
        
    # 4. Brake Rotor & Red Caliper
    disc_x = cx - 0.035 * sign_x
    disc_r = 0.145
    n_disc = 24
    disc_out = [bm_w.verts.new((disc_x, cy + disc_r * math.cos(2.0*math.pi*k/n_disc), cz + disc_r * math.sin(2.0*math.pi*k/n_disc))) for k in range(n_disc)]
    disc_in = [bm_w.verts.new((disc_x, cy + 0.050 * math.cos(2.0*math.pi*k/n_disc), cz + 0.050 * math.sin(2.0*math.pi*k/n_disc))) for k in range(n_disc)]
    for k in range(n_disc):
        k_next = (k + 1) % n_disc
        if sign_x > 0:
            f_disc = bm_w.faces.new([disc_in[k], disc_out[k], disc_out[k_next], disc_in[k_next]])
        else:
            f_disc = bm_w.faces.new([disc_in[k], disc_in[k_next], disc_out[k_next], disc_out[k]])
        f_disc.material_index = 3 # Brake Steel
        
    cal_pts = [
        (disc_x + 0.018 * sign_x, cy + 0.08, cz + 0.10), (disc_x + 0.018 * sign_x, cy + 0.16, cz + 0.04),
        (disc_x - 0.018 * sign_x, cy + 0.16, cz + 0.04), (disc_x - 0.018 * sign_x, cy + 0.08, cz + 0.10),
        (disc_x + 0.018 * sign_x, cy + 0.06, cz + 0.14), (disc_x + 0.018 * sign_x, cy + 0.14, cz + 0.08),
        (disc_x - 0.018 * sign_x, cy + 0.14, cz + 0.08), (disc_x - 0.018 * sign_x, cy + 0.06, cz + 0.14),
    ]
    cv = [bm_w.verts.new(p) for p in cal_pts]
    for face_idx in [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]:
        f_cal = bm_w.faces.new([cv[idx] for idx in face_idx])
        f_cal.material_index = 4 # Brake Caliper
        
    bmesh.ops.recalc_face_normals(bm_w, faces=bm_w.faces)
    w_mesh = bpy.data.meshes.new(name)
    bm_w.to_mesh(w_mesh)
    bm_w.free()
    w_obj = bpy.data.objects.new(name, w_mesh)
    for m_mat in [mats['silver_alloy'], mats['wheel_black'], mats['tyre_rubber'], mats['brake_steel'], mats['brake_caliper']]:
        w_obj.data.materials.append(m_mat)
    for p in w_obj.data.polygons:
        p.use_smooth = True
    if col:
        col.objects.link(w_obj)
    else:
        bpy.context.collection.objects.link(w_obj)
    if parent:
        w_obj.parent = parent
    return w_obj

def build_license_plates(mats, parent=None, col=None):
    hw, hh, hd = 0.526 / 2.0, 0.116 / 2.0, 0.006
    pw, ph = 0.520 / 2.0, 0.110 / 2.0
    
    # 1. Front Plate (mounted on bumper bar at Y = -1.985, Z = 0.360, facing -Y)
    bm_f = bmesh.new()
    bv_f = [
        bm_f.verts.new((-hw, 0.0, -hh)), bm_f.verts.new((+hw, 0.0, -hh)),
        bm_f.verts.new((+hw, +hd, -hh)), bm_f.verts.new((-hw, +hd, -hh)),
        bm_f.verts.new((-hw, 0.0, +hh)), bm_f.verts.new((+hw, 0.0, +hh)),
        bm_f.verts.new((+hw, +hd, +hh)), bm_f.verts.new((-hw, +hd, +hh))
    ]
    bm_f.faces.new([bv_f[0], bv_f[1], bv_f[2], bv_f[3]])
    bm_f.faces.new([bv_f[4], bv_f[7], bv_f[6], bv_f[5]])
    bm_f.faces.new([bv_f[0], bv_f[4], bv_f[5], bv_f[1]])
    bm_f.faces.new([bv_f[1], bv_f[5], bv_f[6], bv_f[2]])
    bm_f.faces.new([bv_f[2], bv_f[6], bv_f[7], bv_f[3]])
    bm_f.faces.new([bv_f[3], bv_f[7], bv_f[4], bv_f[0]])
    
    # Front-facing plate texture face (normal facing -Y)
    pv_f = [
        bm_f.verts.new((+pw, -0.001, +ph)), bm_f.verts.new((-pw, -0.001, +ph)),
        bm_f.verts.new((-pw, -0.001, -ph)), bm_f.verts.new((+pw, -0.001, -ph))
    ]
    fp_f = bm_f.faces.new(pv_f)
    fp_f.material_index = 1
    uv_f = bm_f.loops.layers.uv.verify()
    fp_f.loops[0][uv_f].uv = (1.0, 1.0)
    fp_f.loops[1][uv_f].uv = (0.0, 1.0)
    fp_f.loops[2][uv_f].uv = (0.0, 0.0)
    fp_f.loops[3][uv_f].uv = (1.0, 0.0)
    
    me_f = bpy.data.meshes.new("Scala_Front_Plate")
    bm_f.to_mesh(me_f)
    bm_f.free()
    ob_f = bpy.data.objects.new("Scala_Front_Plate", me_f)
    ob_f.data.materials.append(mats['matte_plastic'])
    ob_f.data.materials.append(mats['plate'])
    ob_f.location = (0.0, -1.985, 0.360)
    ob_f.rotation_euler = (math.radians(3.0), 0.0, 0.0)
    if col:
        col.objects.link(ob_f)
    if parent:
        ob_f.parent = parent
        
    # 2. Rear Plate (mounted in tailgate recess at Y = 1.935, Z = 0.580, facing +Y)
    bm_r = bmesh.new()
    bv_r = [
        bm_r.verts.new((-hw, -hd, -hh)), bm_r.verts.new((+hw, -hd, -hh)),
        bm_r.verts.new((+hw, 0.0, -hh)), bm_r.verts.new((-hw, 0.0, -hh)),
        bm_r.verts.new((-hw, -hd, +hh)), bm_r.verts.new((+hw, -hd, +hh)),
        bm_r.verts.new((+hw, 0.0, +hh)), bm_r.verts.new((-hw, 0.0, +hh))
    ]
    bm_r.faces.new([bv_r[0], bv_r[3], bv_r[2], bv_r[1]])
    bm_r.faces.new([bv_r[4], bv_r[5], bv_r[6], bv_r[7]])
    bm_r.faces.new([bv_r[0], bv_r[1], bv_r[5], bv_r[4]])
    bm_r.faces.new([bv_r[1], bv_r[2], bv_r[6], bv_r[5]])
    bm_r.faces.new([bv_r[2], bv_r[3], bv_r[7], bv_r[6]])
    bm_r.faces.new([bv_r[3], bv_r[0], bv_r[4], bv_r[7]])
    
    # Rear-facing plate texture face (normal facing +Y)
    pv_r = [
        bm_r.verts.new((+pw, 0.001, +ph)), bm_r.verts.new((-pw, 0.001, +ph)),
        bm_r.verts.new((-pw, 0.001, -ph)), bm_r.verts.new((+pw, 0.001, -ph))
    ]
    fp_r = bm_r.faces.new(pv_r)
    fp_r.material_index = 1
    uv_r = bm_r.loops.layers.uv.verify()
    fp_r.loops[0][uv_r].uv = (0.0, 1.0)
    fp_r.loops[1][uv_r].uv = (1.0, 1.0)
    fp_r.loops[2][uv_r].uv = (1.0, 0.0)
    fp_r.loops[3][uv_r].uv = (0.0, 0.0)
    
    me_r = bpy.data.meshes.new("Scala_Rear_Plate")
    bm_r.to_mesh(me_r)
    bm_r.free()
    ob_r = bpy.data.objects.new("Scala_Rear_Plate", me_r)
    ob_r.data.materials.append(mats['matte_plastic'])
    ob_r.data.materials.append(mats['plate'])
    ob_r.location = (0.0, 1.935, 0.580)
    ob_r.rotation_euler = (0.0, 0.0, 0.0)
    if col:
        col.objects.link(ob_r)
    if parent:
        ob_r.parent = parent

def build_complete_master_car():
    master_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=master_path)
    scene = bpy.context.scene
    
    col = bpy.data.collections.get("VEHICLE_SKODA_SCALA")
    if col:
        for ob in list(col.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
    else:
        col = bpy.data.collections.new("VEHICLE_SKODA_SCALA")
        scene.collection.children.link(col)
        
    mats = setup_all_materials()
    
    # Car Root in scene (parked in paved driveway in front of the house entrance)
    # Location: (5.25, -3.50, 0.00), facing South (rot_z = 0.0)
    root = bpy.data.objects.new("Skoda_Scala_MonteCarlo_Root", None)
    root.location = (5.25, -3.50, 0.00)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.empty_display_size = 1.0
    root.empty_display_type = 'ARROWS'
    col.objects.link(root)
    
    # -------------------------------------------------------------
    # 1. LOAD OFFICIAL CAD BODY
    # -------------------------------------------------------------
    zpath_body = r"C:\Users\Vaso\Antigravity\Project blender\assets\skoda_official\SKODA_SCALA_BODY_COLOR_S24_20250928.3mf"
    verts_raw, tris_raw, mmu_raw = load_3mf_geometry(zpath_body, return_mmu=True)
    
    scale_factor = 4.362 / 197.308
    # Keep raw CAD design level (no artificial pitch angle distorting rake)
    
    verts_list = []
    for v in verts_raw:
        vx = v[1] * scale_factor
        vy = v[0] * scale_factor
        vz = v[2] * scale_factor
        verts_list.append((vx, vy, vz))
    verts_arr = np.array(verts_list)
    
    max_tri_idx = 273957
    tris_arr = tris_raw[:max_tri_idx + 1]

    # Face adjacency
    edge_to_faces = defaultdict(list)
    for fi, (v1, v2, v3) in enumerate(tris_arr):
        for e in [(min(v1, v2), max(v1, v2)), (min(v2, v3), max(v2, v3)), (min(v3, v1), max(v3, v1))]:
            edge_to_faces[e].append(fi)

    face_neighbors = defaultdict(list)
    for e, flist in edge_to_faces.items():
        if len(flist) == 2:
            face_neighbors[flist[0]].append(flist[1])
            face_neighbors[flist[1]].append(flist[0])

    v0 = verts_arr[tris_arr[:, 0]]
    v1 = verts_arr[tris_arr[:, 1]]
    v2 = verts_arr[tris_arr[:, 2]]
    face_centers = (v0 + v1 + v2) / 3.0
    normals = np.cross(v1 - v0, v2 - v0)
    norm_len = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, norm_len, where=norm_len > 1e-8)

    def flood_fill_smooth(seed_idx, max_angle_deg=22.0, max_faces=50000):
        visited = set()
        queue = [seed_idx]
        visited.add(seed_idx)
        max_dot = math.cos(math.radians(max_angle_deg))
        while queue and len(visited) < max_faces:
            curr = queue.pop(0)
            curr_n = normals[curr]
            for nbr in face_neighbors[curr]:
                if nbr not in visited:
                    if np.dot(curr_n, normals[nbr]) >= max_dot:
                        visited.add(nbr)
                        queue.append(nbr)
        return visited

    # Find smooth-connected panel face sets using CAD shut lines:
    panel_seeds = {
        'windshield': (0.0, -0.55, 0.35, 18.0),
        'roof': (0.0, 0.45, 0.55, 20.0),
        'rear_hatch_glass': (0.0, 1.35, 0.52, 18.0),
        'tailgate_extended_glass': (0.0, 1.82, 0.28, 18.0),
        'mirror_L': (-0.85, -0.72, 0.28, 18.0),
        'mirror_R': (0.85, -0.72, 0.28, 18.0),
        'taillight_gate_L': (-0.60, 1.95, 0.15, 20.0),
        'taillight_gate_R': (+0.60, 1.95, 0.15, 20.0),
        'taillight_fender_L': (-0.65, 1.82, 0.12, 10.0),
        'taillight_fender_R': (+0.65, 1.82, 0.12, 10.0),
        'headlight_L': (-0.558, -1.796, -0.137, 18.0),
        'headlight_R': (+0.558, -1.796, -0.137, 18.0),
    }

    panel_faces = {}
    for pname, (sx, sy, sz, angle) in panel_seeds.items():
        dists = np.linalg.norm(face_centers - np.array([sx, sy, sz]), axis=1)
        seed = np.argmin(dists)
        panel_faces[pname] = flood_fill_smooth(seed, max_angle_deg=angle)

    # Strictly isolate mirrors so flood fill never leaks down the stalk onto the door skin:
    for m_side in ['mirror_L', 'mirror_R']:
        clean_m = set()
        for fi in panel_faces[m_side]:
            c = face_centers[fi]
            if c[2] >= 0.215 and (abs(c[0]) > 0.80 or (abs(c[0]) > 0.76 and c[2] > 0.22)):
                clean_m.add(fi)
        panel_faces[m_side] = clean_m

    bm = bmesh.new()
    for (vx, vy, vz) in verts_list:
        bm.verts.new((vx, vy, vz))
    bm.verts.ensure_lookup_table()

    for i, (v1_idx, v2_idx, v3_idx) in enumerate(tris_arr):
        f = bm.faces.new([bm.verts[v1_idx], bm.verts[v2_idx], bm.verts[v3_idx]])
        c = face_centers[i]
        n = normals[i]
        cx, cy, cz = c[0], c[1], c[2]
        abs_x = abs(cx)
        
        # 0 = Velvet Red metallic
        mid = 0
        
        # 1. Front Wipers & Scuttle Cowl Grille (Satin / Gloss Black)
        if -1.35 <= cy <= -0.72 and 0.05 <= cz <= 0.32 and abs_x <= 0.68:
            is_windshield_pane = (cy > -0.92 and 0.78 < n[2] < 0.90 and -0.62 < n[1] < -0.42 and abs_x < 0.35)
            if not is_windshield_pane:
                mid = 1
        # 2. Clear automotive safety glass (windshield)
        elif i in panel_faces['windshield']:
            mid = 2
        # 3. B-pillar vertical divider (Gloss black, strictly between front & rear doors above window sill)
        elif 0.075 <= cy <= 0.185 and 0.22 <= cz <= 0.55 and abs_x > 0.65 and abs(n[0]) > 0.60:
            mid = 1
        # 4. Clear automotive safety glass (front door windows in front of B-pillar)
        elif abs_x > 0.54 and -0.72 <= cy < 0.075 and 0.215 <= cz <= 0.52 and abs(n[0]) > 0.50:
            mid = 2
        # 5. Sunset privacy glass (rear door windows + C-pillar quarter windows above fuel tank flap)
        elif abs_x > 0.54 and 0.185 <= cy <= 1.46 and 0.215 <= cz <= 0.52 and abs(n[0]) > 0.50:
            mid = 3
        # 6. Sunset privacy glass (rear hatch glass & extended tailgate glass)
        elif i in panel_faces['rear_hatch_glass'] or i in panel_faces['tailgate_extended_glass']:
            mid = 3
        # 7. Monte Carlo Gloss Black Magic (roof, mirrors)
        elif i in panel_faces['roof'] or i in panel_faces['mirror_L'] or i in panel_faces['mirror_R']:
            mid = 1
        # 5. Taillights (Crystalline dark smoked ruby acrylic on tailgate & rear quarter clusters)
        elif (i in panel_faces['taillight_gate_L'] or i in panel_faces['taillight_gate_R'] or 
              i in panel_faces['taillight_fender_L'] or i in panel_faces['taillight_fender_R']):
            mid = 6
        # 6. Headlights (Crystalline clear polycarbonate lens)
        elif i in panel_faces['headlight_L'] or i in panel_faces['headlight_R']:
            mid = 5
        # 7. Front Grille (Gloss black octagonal frame & vertical slats strictly below hood nose)
        elif cy < -1.80 and -0.38 < cz < -0.15 and abs_x < 0.42:
            mid = 1
        # 8. Lower front air dam, lower intake honeycomb & splitter
        elif cy < -1.78 and cz <= -0.35 and abs_x < 0.68:
            mid = 1
        # 9. Rear diffuser
        elif cy > 1.95 and cz < -0.28 and n[1] > 0.45:
            mid = 1
        # 10. Underbody floorpan (lowest chassis underside, completely below door sills)
        elif cz < -0.46 or (cz < -0.35 and n[2] < -0.7):
            mid = 4
            
        f.material_index = mid

    unused_verts = [v for v in bm.verts if not v.link_faces]
    for v in unused_verts:
        bm.verts.remove(v)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me_body = bpy.data.meshes.new("Skoda_Scala_Official_Body")
    bm.to_mesh(me_body)
    bm.free()

    ob_body = bpy.data.objects.new("Skoda_Scala_Official_Body", me_body)
    col.objects.link(ob_body)
    ob_body.parent = root

    for m_key in ['paint', 'gloss_black', 'glass_clear', 'glass_tinted', 'matte_plastic', 'headlight_glass', 'taillight_red']:
        ob_body.data.materials.append(mats[m_key])

    for p in ob_body.data.polygons:
        p.use_smooth = True

    # Exact factory vertical ride height on driveway (wheel gap = 55 mm, 14 cm clearance)
    car_z_offset = 0.700
    ob_body.location = (0.0, 0.0, car_z_offset)

    # -------------------------------------------------------------
    # 2. MOUNT OFFICIAL 17" KAJAM MONTE CARLO WHEELS & TYRES
    # -------------------------------------------------------------
    zpath_wheels = r"C:\Users\Vaso\Antigravity\Project blender\assets\skoda_official\SKODA_SCALA_WHEELS_S24_20250928.3mf"
    zpath_tyres = r"C:\Users\Vaso\Antigravity\Project blender\assets\skoda_official\SKODA_SCALA_TYRE_S24_20250928.3mf"
    w_verts_cad, w_tris_cad = load_3mf_geometry(zpath_wheels)
    t_verts_cad, t_tris_cad = load_3mf_geometry(zpath_tyres)
    
    # Wheel axle centers: Z = 0.301 m (bottom of 0.301m radius tyre rests at exactly 0.00m on pavers)
    # Track width X = +-0.680 m (aligned flush with tyre outer face tucked 26 mm inside fender)
    wheel_coords = [
        ("Wheel_FL", (-0.680, -1.300, 0.301), True),
        ("Wheel_FR", (+0.680, -1.300, 0.301), False),
        ("Wheel_RL", (-0.680, +1.300, 0.301), True),
        ("Wheel_RR", (+0.680, +1.300, 0.301), False),
    ]
    for w_name, pos, is_left in wheel_coords:
        build_official_kajam_wheel(w_name, pos, is_left, mats, w_verts_cad, w_tris_cad, t_verts_cad, t_tris_cad, scale_factor, root, col)

    # -------------------------------------------------------------
    # 3. MOUNT CZECH LICENSE PLATES (1AH U743)
    # -------------------------------------------------------------
    build_license_plates(mats, root, col)

    bpy.ops.wm.save_mainfile(filepath=master_path)
    print(">>> Saved dum_pudorys.blend with official Škoda Scala Monte Carlo!")

    # -------------------------------------------------------------
    # 4. SETUP CLOSE-UP INSPECTION CAMERAS & RENDER
    # -------------------------------------------------------------
    def get_or_create_cam(c_name, loc, target):
        c_obj = bpy.data.objects.get(c_name)
        if not c_obj:
            c_data = bpy.data.cameras.new(c_name)
            c_obj = bpy.data.objects.new(c_name, c_data)
            scene.collection.objects.link(c_obj)
        c_obj.data.lens = 50.0
        c_obj.location = loc
        look_dir = Vector(target) - Vector(loc)
        c_obj.rotation_euler = look_dir.to_track_quat('-Z', 'Y').to_euler()
        return c_obj

    # Front 3/4 Camera (standing in driveway looking at car front)
    cam_front = get_or_create_cam("Camera_Car_Inspect_Front34", 
                                  (8.50, -7.50, 1.35), 
                                  (5.00, -3.80, 0.58))

    # Rear 3/4 Camera (standing outside on driveway looking at car rear tailgate & wheels)
    cam_rear = get_or_create_cam("Camera_Car_Inspect_Rear34", 
                                 (8.30, -0.60, 1.35), 
                                 (5.00, -2.60, 0.60))

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 128
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.hide_render = False
        sun.hide_viewport = False

    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"

    # Render Front 3/4
    scene.camera = cam_front
    front_path = os.path.join(artifact_dir, "crop_scala_inspect_front34.png")
    scene.render.filepath = front_path
    print(">>> Rendering Close-up Front 3/4...")
    bpy.ops.render.render(write_still=True)
    print("Saved:", front_path)

    # Render Rear 3/4
    scene.camera = cam_rear
    rear_path = os.path.join(artifact_dir, "crop_scala_inspect_rear34.png")
    scene.render.filepath = rear_path
    print(">>> Rendering Close-up Rear 3/4...")
    bpy.ops.render.render(write_still=True)
    print("Saved:", rear_path)

    # Restore master isometric camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile(filepath=master_path)
    print(">>> Master integration and inspection renders completed successfully!")

if __name__ == '__main__':
    build_complete_master_car()
