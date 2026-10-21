import bpy
import bmesh
import mathutils
import math

def build_dreame_perfect():
    print("=== BUILDING CAD-PERFECT DREAME L40 ULTRA ===")

    # 1. Clean existing collection
    coll_name = "Appliances_Robot_Vacuum"
    old_coll = bpy.data.collections.get(coll_name)
    if old_coll:
        for o in list(old_coll.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old_coll)

    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)

    # 2. Photorealistic PBR Materials matching dreame1.png and dreame2.png
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

    # Mat 1: Satin White Housing (Premium consumer electronics satin finish)
    mat_white, bsdf_white = get_or_create_mat("Mat_Dreame_White_Satin")
    bsdf_white.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf_white.inputs['Roughness'].default_value = 0.25
    if 'IOR' in bsdf_white.inputs:
        bsdf_white.inputs['IOR'].default_value = 1.49

    # Mat 2: Pale Champagne Silver / Platinum Metallic (Exact match to dreame1.png and dreame2.png)
    mat_champagne, bsdf_champagne = get_or_create_mat("Mat_Dreame_Champagne_Fluted")
    bsdf_champagne.inputs['Base Color'].default_value = (0.92, 0.88, 0.82, 1.0)
    bsdf_champagne.inputs['Metallic'].default_value = 0.92
    bsdf_champagne.inputs['Roughness'].default_value = 0.16

    # Mat 3: Dark Matte Plastic (Chassis underside, washboard, inner dock cavity)
    mat_dark, bsdf_dark = get_or_create_mat("Mat_Dreame_Dark_Plastic")
    bsdf_dark.inputs['Base Color'].default_value = (0.07, 0.07, 0.08, 1.0)
    bsdf_dark.inputs['Roughness'].default_value = 0.45

    # Mat 4: Visor Graphite Housing (Satin dark grey visor housing)
    mat_visor, bsdf_visor = get_or_create_mat("Mat_Dreame_Visor_Graphite")
    bsdf_visor.inputs['Base Color'].default_value = (0.09, 0.09, 0.10, 1.0)
    bsdf_visor.inputs['Roughness'].default_value = 0.32

    # Mat 5: Optical AR Camera Glass (Deep antireflective dark navy/cyan)
    mat_lens, bsdf_lens = get_or_create_mat("Mat_Dreame_Camera_Glass")
    bsdf_lens.inputs['Base Color'].default_value = (0.010, 0.015, 0.025, 1.0)
    bsdf_lens.inputs['Roughness'].default_value = 0.03
    if 'Specular IOR Level' in bsdf_lens.inputs:
        bsdf_lens.inputs['Specular IOR Level'].default_value = 1.0

    # Mat 6: Glossy Piano Black (Camera bezel ring & sensor windows)
    mat_glossy_black, bsdf_gb = get_or_create_mat("Mat_Dreame_Glossy_Black")
    bsdf_gb.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bsdf_gb.inputs['Roughness'].default_value = 0.06

    # Mat 7: Frosted White LED Headlights (Translucent diffusers)
    mat_headlight, bsdf_hl = get_or_create_mat("Mat_Dreame_Headlight")
    bsdf_hl.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf_hl.inputs['Roughness'].default_value = 0.25
    if 'Emission Color' in bsdf_hl.inputs:
        bsdf_hl.inputs['Emission Color'].default_value = (0.95, 0.96, 1.0, 1.0)
    if 'Emission Strength' in bsdf_hl.inputs:
        bsdf_hl.inputs['Emission Strength'].default_value = 3.0

    # Mat 8: AI Crimson Red (for "AI" in "AI Action")
    mat_red, bsdf_red = get_or_create_mat("Mat_Dreame_AI_Red")
    bsdf_red.inputs['Base Color'].default_value = (0.85, 0.08, 0.08, 1.0)
    bsdf_red.inputs['Roughness'].default_value = 0.30

    # Mat 9: Action Titanium Grey (for "Action" in "AI Action")
    mat_grey, bsdf_grey = get_or_create_mat("Mat_Dreame_Action_Silver")
    bsdf_grey.inputs['Base Color'].default_value = (0.42, 0.42, 0.44, 1.0)
    bsdf_grey.inputs['Roughness'].default_value = 0.30

    # Mat 10: Status LED indicator slit
    mat_led, bsdf_led = get_or_create_mat("Mat_Dreame_LED_Indicator")
    bsdf_led.inputs['Base Color'].default_value = (0.90, 0.96, 1.0, 1.0)
    if 'Emission Color' in bsdf_led.inputs:
        bsdf_led.inputs['Emission Color'].default_value = (0.90, 0.96, 1.0, 1.0)
    if 'Emission Strength' in bsdf_led.inputs:
        bsdf_led.inputs['Emission Strength'].default_value = 8.0

    # Mat 11: Brass Charging Contacts
    mat_contact, bsdf_contact = get_or_create_mat("Mat_Dreame_Gold_Contacts")
    bsdf_contact.inputs['Base Color'].default_value = (0.95, 0.76, 0.28, 1.0)
    bsdf_contact.inputs['Metallic'].default_value = 1.0
    bsdf_contact.inputs['Roughness'].default_value = 0.15

    # Mat 12: Matte Black Rubber (Caster & tires)
    mat_rubber, bsdf_rubber = get_or_create_mat("Mat_Dreame_Rubber")
    bsdf_rubber.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0)
    bsdf_rubber.inputs['Roughness'].default_value = 0.60

    # Mat 13: Wall Socket Frame
    mat_socket, bsdf_socket = get_or_create_mat("Mat_Dreame_Socket_Frame")
    bsdf_socket.inputs['Base Color'].default_value = (0.94, 0.94, 0.94, 1.0)
    bsdf_socket.inputs['Roughness'].default_value = 0.25

    def register_obj(obj, parent=None):
        coll.objects.link(obj)
        if parent:
            obj.parent = parent
        if obj.type == 'MESH':
            for poly in obj.data.polygons:
                poly.use_smooth = True
        return obj

    # Root Empty
    root = bpy.data.objects.new("Dreame_L40_Ultra", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 0.2
    root.location = mathutils.Vector((9.420, 8.480, 0.015))
    root.rotation_euler = mathutils.Euler((0.0, 0.0, math.pi / 2.0), 'XYZ')
    register_obj(root)

    # -------------------------------------------------------------------------
    # 3. STATION TOWER GEOMETRY (Matching dreame1.png)
    # -------------------------------------------------------------------------
    w = 0.170
    y_back = -0.215
    y_front = 0.125
    rf = 0.032
    rb = 0.015

    def get_station_contour(inset=0.0):
        pts = []
        _w = w - inset
        _yb = y_back + inset
        _yf = y_front - inset
        _rf = max(0.005, rf - inset)
        _rb = max(0.005, rb - inset)

        # Back straight (+X to -X)
        for i in range(11):
            t = i / 10.0
            pts.append(((_w - _rb) * (1.0 - 2.0 * t), _yb))

        # Back-right corner arc
        cx, cy = -_w + _rb, _yb + _rb
        for i in range(1, 6):
            ang = -math.pi / 2.0 - (math.pi / 2.0) * (i / 5.0)
            pts.append((cx + _rb * math.cos(ang), cy + _rb * math.sin(ang)))

        # Right straight
        for i in range(1, 8):
            t = i / 7.0
            pts.append((-_w, (_yb + _rb) + ((_yf - _rf) - (_yb + _rb)) * t))

        # Front-right corner arc
        cx, cy = -_w + _rf, _yf - _rf
        for i in range(1, 9):
            ang = math.pi - (math.pi / 2.0) * (i / 8.0)
            pts.append((cx + _rf * math.cos(ang), cy + _rf * math.sin(ang)))

        # Front straight
        for i in range(1, 11):
            t = i / 10.0
            pts.append(((-_w + _rf) + (2 * _w - 2 * _rf) * t, _yf))

        # Front-left corner arc
        cx, cy = _w - _rf, _yf - _rf
        for i in range(1, 9):
            ang = math.pi / 2.0 - (math.pi / 2.0) * (i / 8.0)
            pts.append((cx + _rf * math.cos(ang), cy + _rf * math.sin(ang)))

        # Left straight
        for i in range(1, 8):
            t = i / 7.0
            pts.append((_w, (_yf - _rf) - ((_yf - _rf) - (_yb + _rb)) * t))

        # Back-left corner arc
        cx, cy = _w - _rb, _yb + _rb
        for i in range(1, 6):
            ang = 0.0 - (math.pi / 2.0) * (i / 5.0)
            pts.append((cx + _rb * math.cos(ang), cy + _rb * math.sin(ang)))

        return pts

    st_contour = get_station_contour()
    n_pts = len(st_contour)

    # Station Main Body (Smooth white monolithic casing)
    bm_st = bmesh.new()

    # Outer shell from base (0.000) to top rim (0.575)
    # With garage arch cut out at front: between X = -0.142 and +0.142 up to Z = 0.155
    z_lvls = [0.000, 0.155, 0.575]
    v_rings = []
    for z in z_lvls:
        ring = [bm_st.verts.new((p[0], p[1], z)) for p in st_contour]
        v_rings.append(ring)

    # Connect upper shell (0.155 to 0.575) - full continuous perimeter
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        bm_st.faces.new((v_rings[1][i], v_rings[1][i_next], v_rings[2][i_next], v_rings[2][i]))

    # Connect lower shell (0.000 to 0.155) - omit front garage opening
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        v1 = v_rings[0][i]
        v2 = v_rings[0][i_next]
        is_front_opening = (v1.co.y > (y_front - 0.005) and v2.co.y > (y_front - 0.005) and abs(v1.co.x) < 0.142 and abs(v2.co.x) < 0.142)
        if not is_front_opening:
            bm_st.faces.new((v_rings[0][i], v_rings[0][i_next], v_rings[1][i_next], v_rings[1][i]))

    # Garage Interior Cavity (Dark washboard garage)
    v_g_l_fb = bm_st.verts.new((-0.142, y_front, 0.000))
    v_g_l_ft = bm_st.verts.new((-0.142, y_front, 0.155))
    v_g_l_bb = bm_st.verts.new((-0.142, -0.160, 0.000))
    v_g_l_bt = bm_st.verts.new((-0.142, -0.160, 0.155))

    v_g_r_fb = bm_st.verts.new((0.142, y_front, 0.000))
    v_g_r_ft = bm_st.verts.new((0.142, y_front, 0.155))
    v_g_r_bb = bm_st.verts.new((0.142, -0.160, 0.000))
    v_g_r_bt = bm_st.verts.new((0.142, -0.160, 0.155))

    bm_st.faces.new((v_g_l_fb, v_g_l_bb, v_g_l_bt, v_g_l_ft)) # Left inner wall
    bm_st.faces.new((v_g_r_bb, v_g_r_fb, v_g_r_ft, v_g_r_bt)) # Right inner wall
    bm_st.faces.new((v_g_l_bb, v_g_r_bb, v_g_r_bt, v_g_l_bt)) # Back wall
    bm_st.faces.new((v_g_l_bt, v_g_r_bt, v_g_r_ft, v_g_l_ft)) # Ceiling

    # Garage cheek front caps
    v_out_g_lb = min(v_rings[0], key=lambda v: (v.co - mathutils.Vector((-0.142, y_front, 0.000))).length)
    v_out_g_lt = min(v_rings[1], key=lambda v: (v.co - mathutils.Vector((-0.142, y_front, 0.155))).length)
    v_out_g_rb = min(v_rings[0], key=lambda v: (v.co - mathutils.Vector(( 0.142, y_front, 0.000))).length)
    v_out_g_rt = min(v_rings[1], key=lambda v: (v.co - mathutils.Vector(( 0.142, y_front, 0.155))).length)

    bm_st.faces.new((v_out_g_lb, v_g_l_fb, v_g_l_ft, v_out_g_lt))
    bm_st.faces.new((v_g_r_fb, v_out_g_rb, v_out_g_rt, v_g_r_ft))

    bmesh.ops.recalc_face_normals(bm_st, faces=bm_st.faces)
    mesh_st = bpy.data.meshes.new("Dreame_Station_Body")
    bm_st.to_mesh(mesh_st)
    bm_st.free()
    obj_st = bpy.data.objects.new("Dreame_Station_Body", mesh_st)
    obj_st.data.materials.append(mat_white)
    register_obj(obj_st, parent=root)

    # Station Top Lid (Separate clean piece with rounded rim, matching dreame1.png)
    bm_lid = bmesh.new()
    lid_contour = get_station_contour(inset=0.002)
    v_lid_b = [bm_lid.verts.new((p[0], p[1], 0.575)) for p in lid_contour]
    v_lid_m = [bm_lid.verts.new((p[0], p[1], 0.587)) for p in lid_contour]
    v_lid_t = [bm_lid.verts.new((p[0] * 0.985, p[1] * 0.985, 0.590)) for p in lid_contour]

    for i in range(len(lid_contour)):
        i_next = (i + 1) % len(lid_contour)
        bm_lid.faces.new((v_lid_b[i], v_lid_b[i_next], v_lid_m[i_next], v_lid_m[i]))
        bm_lid.faces.new((v_lid_m[i], v_lid_m[i_next], v_lid_t[i_next], v_lid_t[i]))
    bm_lid.faces.new(v_lid_t)

    bmesh.ops.recalc_face_normals(bm_lid, faces=bm_lid.faces)
    mesh_lid = bpy.data.meshes.new("Dreame_Station_Lid")
    bm_lid.to_mesh(mesh_lid)
    bm_lid.free()
    obj_lid = bpy.data.objects.new("Dreame_Station_Lid", mesh_lid)
    obj_lid.data.materials.append(mat_white)
    register_obj(obj_lid, parent=root)

    # -------------------------------------------------------------------------
    # 4. INSET FLUTED PANEL (Real 3D Rounded Ribs & Platinum Finish)
    # -------------------------------------------------------------------------
    # In dreame1.png: The panel is inset in the front face of the station!
    # Width: 266 mm (-0.133 to +0.133), Height: 156 mm (Z = 0.167 to 0.323)
    # Radius of rounded corners: 16 mm
    # Surface has 64 vertical 3D rounded ribs
    bm_flutes = bmesh.new()
    panel_hw = 0.133
    panel_z_b = 0.167
    panel_z_t = 0.323
    panel_rc = 0.016
    n_ribs = 64
    flute_y_base = y_front + 0.0006 # Mounts cleanly on the front face

    for i in range(n_ribs):
        t0 = i / float(n_ribs)
        t1 = (i + 1) / float(n_ribs)
        x0 = -panel_hw + 2 * panel_hw * t0
        x1 = -panel_hw + 2 * panel_hw * t1
        xm = (x0 + x1) / 2.0
        ym = flute_y_base + 0.0018 # 1.8 mm rounded convex flute protrusion

        def get_z_bounds(x):
            dx = abs(x) - (panel_hw - panel_rc)
            if dx > 0:
                dz = panel_rc - math.sqrt(max(0.0, panel_rc**2 - dx**2))
                return panel_z_b + dz, panel_z_t - dz
            return panel_z_b, panel_z_t

        zb0, zt0 = get_z_bounds(x0)
        zbm, ztm = get_z_bounds(xm)
        zb1, zt1 = get_z_bounds(x1)

        v0_b = bm_flutes.verts.new((x0, flute_y_base, zb0))
        v0_t = bm_flutes.verts.new((x0, flute_y_base, zt0))
        vm_b = bm_flutes.verts.new((xm, ym, zbm))
        vm_t = bm_flutes.verts.new((xm, ym, ztm))
        v1_b = bm_flutes.verts.new((x1, flute_y_base, zb1))
        v1_t = bm_flutes.verts.new((x1, flute_y_base, zt1))

        bm_flutes.faces.new((v0_b, vm_b, vm_t, v0_t))
        bm_flutes.faces.new((vm_b, v1_b, v1_t, vm_t))

    # Metallic Bezel Outer Frame (Border trim framing the fluted panel)
    bm_frame = bmesh.new()
    bmesh.ops.create_cube(bm_frame, size=1.0)
    bmesh.ops.scale(bm_frame, vec=(2 * panel_hw + 0.006, 0.0015, panel_z_t - panel_z_b + 0.006), verts=bm_frame.verts)
    bmesh.ops.translate(bm_frame, vec=(0.0, flute_y_base - 0.0004, (panel_z_b + panel_z_t) / 2.0), verts=bm_frame.verts)

    bmesh.ops.recalc_face_normals(bm_flutes, faces=bm_flutes.faces)
    mesh_flutes = bpy.data.meshes.new("Dreame_Station_Fluted_Panel")
    bm_flutes.to_mesh(mesh_flutes)
    bm_flutes.free()
    obj_flutes = bpy.data.objects.new("Dreame_Station_Fluted_Panel", mesh_flutes)
    obj_flutes.data.materials.append(mat_champagne)
    register_obj(obj_flutes, parent=root)

    mesh_frame = bpy.data.meshes.new("Dreame_Fluted_Panel_Frame")
    bm_frame.to_mesh(mesh_frame)
    bm_frame.free()
    obj_frame = bpy.data.objects.new("Dreame_Fluted_Panel_Frame", mesh_frame)
    obj_frame.data.materials.append(mat_champagne)
    register_obj(obj_frame, parent=root)

    # Inscription text badge on bottom right of fluted panel: "Auto-Empty Dust Collection"
    bm_txt = bmesh.new()
    bmesh.ops.create_cube(bm_txt, size=1.0)
    bmesh.ops.scale(bm_txt, vec=(0.045, 0.0006, 0.004), verts=bm_txt.verts)
    bmesh.ops.translate(bm_txt, vec=(0.075, flute_y_base + 0.0022, panel_z_b + 0.012), verts=bm_txt.verts)
    mesh_txt = bpy.data.meshes.new("Dreame_Fluted_Panel_Text")
    bm_txt.to_mesh(mesh_txt)
    bm_txt.free()
    obj_txt = bpy.data.objects.new("Dreame_Fluted_Panel_Text", mesh_txt)
    obj_txt.data.materials.append(mat_grey)
    register_obj(obj_txt, parent=root)

    # -------------------------------------------------------------------------
    # 5. DREAME LOGO & STATUS LED INDICATOR (Matching dreame1.png)
    # -------------------------------------------------------------------------
    bm_led = bmesh.new()
    bmesh.ops.create_cube(bm_led, size=1.0)
    bmesh.ops.scale(bm_led, vec=(0.020, 0.0015, 0.002), verts=bm_led.verts)
    bmesh.ops.translate(bm_led, vec=(0.0, y_front + 0.0006, 0.550), verts=bm_led.verts)
    mesh_led = bpy.data.meshes.new("Dreame_Station_LED")
    bm_led.to_mesh(mesh_led)
    bm_led.free()
    obj_led = bpy.data.objects.new("Dreame_Station_LED", mesh_led)
    obj_led.data.materials.append(mat_led)
    register_obj(obj_led, parent=root)

    bm_logo = bmesh.new()
    bmesh.ops.create_cube(bm_logo, size=1.0)
    bmesh.ops.scale(bm_logo, vec=(0.040, 0.0008, 0.006), verts=bm_logo.verts)
    bmesh.ops.translate(bm_logo, vec=(0.0, y_front + 0.0006, 0.522), verts=bm_logo.verts)
    mesh_logo = bpy.data.meshes.new("Dreame_Station_Logo")
    bm_logo.to_mesh(mesh_logo)
    bm_logo.free()
    obj_logo = bpy.data.objects.new("Dreame_Station_Logo", mesh_logo)
    obj_logo.data.materials.append(mat_champagne)
    register_obj(obj_logo, parent=root)

    # -------------------------------------------------------------------------
    # 6. DOCKING CAVITY DETAILS & WASHBOARD
    # -------------------------------------------------------------------------
    bm_tray = bmesh.new()
    bmesh.ops.create_cube(bm_tray, size=1.0)
    bmesh.ops.scale(bm_tray, vec=(0.270, 0.280, 0.018), verts=bm_tray.verts)
    bmesh.ops.translate(bm_tray, vec=(0.0, -0.015, 0.009), verts=bm_tray.verts)

    for i in range(12):
        y_rib = -0.130 + i * 0.021
        v_rib = bmesh.ops.create_cube(bm_tray, size=1.0)['verts']
        bmesh.ops.scale(bm_tray, vec=(0.230, 0.004, 0.004), verts=v_rib)
        bmesh.ops.translate(bm_tray, vec=(0.0, y_rib, 0.020), verts=v_rib)

    mesh_tray = bpy.data.meshes.new("Dreame_Station_Wash_Tray")
    bm_tray.to_mesh(mesh_tray)
    bm_tray.free()
    obj_tray = bpy.data.objects.new("Dreame_Station_Wash_Tray", mesh_tray)
    obj_tray.data.materials.append(mat_dark)
    register_obj(obj_tray, parent=root)

    # Charging contacts
    for sign in [-1, 1]:
        bm_con = bmesh.new()
        res_c = bmesh.ops.create_cone(bm_con, cap_ends=True, radius1=0.006, radius2=0.006, depth=0.012, segments=16)
        bmesh.ops.rotate(bm_con, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.pi / 2.0, 4, 'X'), verts=res_c['verts'])
        bmesh.ops.translate(bm_con, vec=(sign * 0.055, -0.158, 0.110), verts=res_c['verts'])
        mesh_con = bpy.data.meshes.new(f"Dreame_Charging_Contact_{sign}")
        bm_con.to_mesh(mesh_con)
        bm_con.free()
        obj_con = bpy.data.objects.new(f"Dreame_Charging_Contact_{sign}", mesh_con)
        obj_con.data.materials.append(mat_contact)
        register_obj(obj_con, parent=root)

    # -------------------------------------------------------------------------
    # 7. BASEPLATE RAMP (White molded ramp with ribbed wheel tracks)
    # -------------------------------------------------------------------------
    bm_ramp = bmesh.new()
    rw = 0.185
    ry_front = 0.400
    ry_back = 0.040
    rr_c = 0.040

    ramp_pts = []
    ramp_pts.append((-rw, ry_back))
    ramp_pts.append((-rw, ry_front - rr_c))
    for i in range(1, 11):
        ang = math.pi - (math.pi / 2.0) * (i / 10.0)
        ramp_pts.append((-rw + rr_c + rr_c * math.cos(ang), ry_front - rr_c + rr_c * math.sin(ang)))
    ramp_pts.append((rw - rr_c, ry_front))
    for i in range(1, 11):
        ang = math.pi / 2.0 - (math.pi / 2.0) * (i / 10.0)
        ramp_pts.append((rw - rr_c + rr_c * math.cos(ang), ry_front - rr_c + rr_c * math.sin(ang)))
    ramp_pts.append((rw, ry_front - rr_c))
    ramp_pts.append((rw, ry_back))

    v_top_ramp = []
    v_bot_ramp = []
    for p in ramp_pts:
        z_t = 0.008 if p[1] < 0.280 else 0.002
        v_top_ramp.append(bm_ramp.verts.new((p[0], p[1], z_t)))
        v_bot_ramp.append(bm_ramp.verts.new((p[0], p[1], 0.000)))

    n_rp = len(ramp_pts)
    for i in range(n_rp - 1):
        bm_ramp.faces.new((v_bot_ramp[i], v_bot_ramp[i+1], v_top_ramp[i+1], v_top_ramp[i]))
    bm_ramp.faces.new((v_bot_ramp[-1], v_bot_ramp[0], v_top_ramp[0], v_top_ramp[-1]))
    bm_ramp.faces.new(reversed(v_bot_ramp))
    bm_ramp.faces.new(v_top_ramp)

    bmesh.ops.recalc_face_normals(bm_ramp, faces=bm_ramp.faces)
    mesh_ramp = bpy.data.meshes.new("Dreame_Baseplate_Ramp")
    bm_ramp.to_mesh(mesh_ramp)
    bm_ramp.free()
    obj_ramp = bpy.data.objects.new("Dreame_Baseplate_Ramp", mesh_ramp)
    obj_ramp.data.materials.append(mat_white)
    register_obj(obj_ramp, parent=root)

    # Wheel Traction Pads
    for sign in [-1, 1]:
        bm_tr = bmesh.new()
        for r in range(12):
            y_tr = 0.160 + r * 0.016
            v_tr = bmesh.ops.create_cube(bm_tr, size=1.0)['verts']
            bmesh.ops.scale(bm_tr, vec=(0.046, 0.0035, 0.0016), verts=v_tr)
            bmesh.ops.translate(bm_tr, vec=(sign * 0.115, y_tr, 0.008), verts=v_tr)
        mesh_tr = bpy.data.meshes.new(f"Dreame_Traction_Pad_{sign}")
        bm_tr.to_mesh(mesh_tr)
        bm_tr.free()
        obj_tr = bpy.data.objects.new(f"Dreame_Traction_Pad_{sign}", mesh_tr)
        obj_tr.data.materials.append(mat_white)
        register_obj(obj_tr, parent=root)

    # -------------------------------------------------------------------------
    # 8. THE DREAME L40 ROBOT PUCK (Exact CAD Model matching dreame2.png)
    # -------------------------------------------------------------------------
    bot_y = 0.175
    bot_z_base = 0.010
    bot_r = 0.175
    bot_h = 0.076
    deck_z = bot_z_base + bot_h
    n_seg = 72

    # A. Main Robot Body (Smooth white puck)
    bm_robot = bmesh.new()
    rings_bot = []
    r_radii = [bot_r - 0.010, bot_r, bot_r, bot_r - 0.004]
    r_zeds = [bot_z_base, bot_z_base + 0.010, deck_z - 0.005, deck_z]

    for z_idx, z in enumerate(r_zeds):
        r_curr = r_radii[z_idx]
        ring = []
        for i in range(n_seg):
            ang = 2.0 * math.pi * (i / float(n_seg))
            x = r_curr * math.cos(ang)
            y = bot_y + r_curr * math.sin(ang)
            ring.append(bm_robot.verts.new((x, y, z)))
        rings_bot.append(ring)

    for r in range(len(rings_bot) - 1):
        r1 = rings_bot[r]
        r2 = rings_bot[r + 1]
        for i in range(n_seg):
            i_next = (i + 1) % n_seg
            bm_robot.faces.new((r1[i], r1[i_next], r2[i_next], r2[i]))

    # Top deck face
    v_bot_center = bm_robot.verts.new((0.0, bot_y, deck_z))
    top_r = rings_bot[-1]
    for i in range(n_seg):
        i_next = (i + 1) % n_seg
        bm_robot.faces.new((top_r[i], top_r[i_next], v_bot_center))

    bmesh.ops.recalc_face_normals(bm_robot, faces=bm_robot.faces)
    mesh_robot = bpy.data.meshes.new("Dreame_L40_Robot")
    bm_robot.to_mesh(mesh_robot)
    bm_robot.free()
    obj_robot = bpy.data.objects.new("Dreame_L40_Robot", mesh_robot)
    obj_robot.data.materials.append(mat_white)
    register_obj(obj_robot, parent=root)

    # -------------------------------------------------------------------------
    # 9. FRONT BUMPER WITH VISOR CUTOUT & AI ACTION SYSTEM (Matching dreame2.png!)
    # -------------------------------------------------------------------------
    # Robot front is in +Y direction (bot_y + bot_r = 0.350 m).
    # Angular parameterization: alpha = 0 at front apex (+Y).
    # bx = b_r * sin(alpha), by = bot_y + b_r * cos(alpha)
    # alpha from -pi/2 (Right side, -X) to +pi/2 (Left side, +X)
    visor_hw = 0.062
    visor_z_b = bot_z_base + 0.024
    visor_z_t = bot_z_base + 0.058
    visor_z_c = (visor_z_b + visor_z_t) / 2.0
    ang_cutout = math.asin(visor_hw / bot_r) # Cutout half-angle (~20.7 deg)

    bm_bump = bmesh.new()
    b_r = bot_r + 0.0012
    b_z_b = bot_z_base + 0.005
    b_z_t = deck_z - 0.002

    # A. Right Bumper Flank: alpha from -pi/2 to -ang_cutout
    n_flank = 20
    pts_rf_bot = []
    pts_rf_top = []
    for i in range(n_flank + 1):
        ang = -math.pi / 2.0 + (math.pi / 2.0 - ang_cutout) * (i / float(n_flank))
        bx = b_r * math.sin(ang)
        by = bot_y + b_r * math.cos(ang)
        pts_rf_bot.append(bm_bump.verts.new((bx, by, b_z_b)))
        pts_rf_top.append(bm_bump.verts.new((bx, by, b_z_t)))

    for i in range(n_flank):
        bm_bump.faces.new((pts_rf_bot[i], pts_rf_bot[i+1], pts_rf_top[i+1], pts_rf_top[i]))

    # B. Left Bumper Flank: alpha from +ang_cutout to +pi/2
    pts_lf_bot = []
    pts_lf_top = []
    for i in range(n_flank + 1):
        ang = ang_cutout + (math.pi / 2.0 - ang_cutout) * (i / float(n_flank))
        bx = b_r * math.sin(ang)
        by = bot_y + b_r * math.cos(ang)
        pts_lf_bot.append(bm_bump.verts.new((bx, by, b_z_b)))
        pts_lf_top.append(bm_bump.verts.new((bx, by, b_z_t)))

    for i in range(n_flank):
        bm_bump.faces.new((pts_lf_bot[i], pts_lf_bot[i+1], pts_lf_top[i+1], pts_lf_top[i]))

    # C. Center Bridge Above Visor (alpha from -ang_cutout to +ang_cutout, Z from visor_z_t to b_z_t)
    n_bridge = 16
    pts_br_t_bot = []
    pts_br_t_top = []
    for i in range(n_bridge + 1):
        ang = -ang_cutout + (2 * ang_cutout) * (i / float(n_bridge))
        bx = b_r * math.sin(ang)
        by = bot_y + b_r * math.cos(ang)
        pts_br_t_bot.append(bm_bump.verts.new((bx, by, visor_z_t)))
        pts_br_t_top.append(bm_bump.verts.new((bx, by, b_z_t)))

    for i in range(n_bridge):
        bm_bump.faces.new((pts_br_t_bot[i], pts_br_t_bot[i+1], pts_br_t_top[i+1], pts_br_t_top[i]))

    # D. Center Bridge Below Visor (alpha from -ang_cutout to +ang_cutout, Z from b_z_b to visor_z_b)
    pts_br_b_bot = []
    pts_br_b_top = []
    for i in range(n_bridge + 1):
        ang = -ang_cutout + (2 * ang_cutout) * (i / float(n_bridge))
        bx = b_r * math.sin(ang)
        by = bot_y + b_r * math.cos(ang)
        pts_br_b_bot.append(bm_bump.verts.new((bx, by, b_z_b)))
        pts_br_b_top.append(bm_bump.verts.new((bx, by, visor_z_b)))

    for i in range(n_bridge):
        bm_bump.faces.new((pts_br_b_bot[i], pts_br_b_bot[i+1], pts_br_b_top[i+1], pts_br_b_top[i]))

    bmesh.ops.recalc_face_normals(bm_bump, faces=bm_bump.faces)
    mesh_bump = bpy.data.meshes.new("Dreame_Robot_Bumper")
    bm_bump.to_mesh(mesh_bump)
    bm_bump.free()
    obj_bump = bpy.data.objects.new("Dreame_Robot_Bumper", mesh_bump)
    obj_bump.data.materials.append(mat_white)
    register_obj(obj_bump, parent=root)

    # Bumper Side Seam notches at -90° and +90°
    for sign in [-1, 1]:
        bm_seam = bmesh.new()
        bmesh.ops.create_cube(bm_seam, size=1.0)
        bmesh.ops.scale(bm_seam, vec=(0.002, 0.008, bot_h - 0.008), verts=bm_seam.verts)
        bmesh.ops.translate(bm_seam, vec=(sign * bot_r, bot_y, bot_z_base + bot_h / 2.0), verts=bm_seam.verts)
        mesh_seam = bpy.data.meshes.new(f"Dreame_Bumper_Seam_{sign}")
        bm_seam.to_mesh(mesh_seam)
        bm_seam.free()
        obj_seam = bpy.data.objects.new(f"Dreame_Bumper_Seam_{sign}", mesh_seam)
        obj_seam.data.materials.append(mat_dark)
        register_obj(obj_seam, parent=root)

    # -------------------------------------------------------------------------
    # THE AI ACTION VISOR MODULE (Curved CAD Masterpiece matching dreame2.png)
    # -------------------------------------------------------------------------
    # In dreame2.png:
    # 1. Curved dark graphite housing that follows bumper circle
    # 2. Central recessed RGB camera bezel & optical glass eye
    # 3. Two vertical frosted LED headlights flanking camera
    # 4. Two deep sculpted 3D structured light laser pockets on outer wings
    # 5. "AI Action" badge on white bumper above visor

    # A. Graphite Inset Visor Housing (Curved along bumper arc, flush with bumper surface!)
    bm_vhous = bmesh.new()
    n_vc = 32
    vh_d = 0.016 # 16 mm depth
    v_vh_f_b = []
    v_vh_f_t = []
    v_vh_b_b = []
    v_vh_b_t = []

    for i in range(n_vc + 1):
        t = i / float(n_vc)
        vx = -visor_hw + 2 * visor_hw * t
        ang_v = math.asin(vx / b_r)
        # Front face sits flush with outer bumper (b_r), in FRONT of inner robot body
        vy_f = bot_y + b_r * math.cos(ang_v) + 0.0003
        vy_b = vy_f - vh_d

        v_vh_f_b.append(bm_vhous.verts.new((vx, vy_f, visor_z_b)))
        v_vh_f_t.append(bm_vhous.verts.new((vx, vy_f, visor_z_t)))
        v_vh_b_b.append(bm_vhous.verts.new((vx, vy_b, visor_z_b)))
        v_vh_b_t.append(bm_vhous.verts.new((vx, vy_b, visor_z_t)))

    for i in range(n_vc):
        # Front face (visible dark graphite visor!)
        bm_vhous.faces.new((v_vh_f_b[i], v_vh_f_b[i+1], v_vh_f_t[i+1], v_vh_f_t[i]))
        # Back face
        bm_vhous.faces.new((v_vh_b_b[i+1], v_vh_b_b[i], v_vh_b_t[i], v_vh_b_t[i+1]))
        # Bottom face
        bm_vhous.faces.new((v_vh_f_b[i], v_vh_b_b[i], v_vh_b_b[i+1], v_vh_f_b[i+1]))
        # Top face
        bm_vhous.faces.new((v_vh_f_t[i+1], v_vh_b_t[i+1], v_vh_b_t[i], v_vh_f_t[i]))

    # End caps
    bm_vhous.faces.new((v_vh_f_b[0], v_vh_f_t[0], v_vh_b_t[0], v_vh_b_b[0]))
    bm_vhous.faces.new((v_vh_f_b[n_vc], v_vh_b_b[n_vc], v_vh_b_t[n_vc], v_vh_f_t[n_vc]))

    bmesh.ops.recalc_face_normals(bm_vhous, faces=bm_vhous.faces)
    mesh_vhous = bpy.data.meshes.new("Dreame_Visor_Housing")
    bm_vhous.to_mesh(mesh_vhous)
    bm_vhous.free()
    obj_vhous = bpy.data.objects.new("Dreame_Visor_Housing", mesh_vhous)
    obj_vhous.data.materials.append(mat_visor)
    register_obj(obj_vhous, parent=root)

    # B. Central RGB Camera Bezel (Glossy black piano lacquer, protruding slightly from visor face)
    bm_cbez = bmesh.new()
    bmesh.ops.create_cube(bm_cbez, size=1.0)
    bmesh.ops.scale(bm_cbez, vec=(0.034, 0.006, 0.022), verts=bm_cbez.verts)
    bmesh.ops.translate(bm_cbez, vec=(0.0, bot_y + b_r - 0.001, visor_z_c), verts=bm_cbez.verts)
    mesh_cbez = bpy.data.meshes.new("Dreame_Camera_Bezel")
    bm_cbez.to_mesh(mesh_cbez)
    bm_cbez.free()
    obj_cbez = bpy.data.objects.new("Dreame_Camera_Bezel", mesh_cbez)
    obj_cbez.data.materials.append(mat_glossy_black)
    register_obj(obj_cbez, parent=root)

    # Antireflective Optical Lens Eye
    bm_lens = bmesh.new()
    res_l = bmesh.ops.create_cone(bm_lens, cap_ends=True, radius1=0.0065, radius2=0.0065, depth=0.004, segments=24)
    bmesh.ops.rotate(bm_lens, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.pi / 2.0, 4, 'X'), verts=res_l['verts'])
    bmesh.ops.translate(bm_lens, vec=(0.0, bot_y + b_r + 0.0015, visor_z_c), verts=res_l['verts'])
    mesh_lens = bpy.data.meshes.new("Dreame_Camera_Lens")
    bm_lens.to_mesh(mesh_lens)
    bm_lens.free()
    obj_lens = bpy.data.objects.new("Dreame_Camera_Lens", mesh_lens)
    obj_lens.data.materials.append(mat_lens)
    register_obj(obj_lens, parent=root)

    # C. Dual Vertical LED Headlights (Frosted diffusers)
    for sign in [-1, 1]:
        bm_hl = bmesh.new()
        bmesh.ops.create_cube(bm_hl, size=1.0)
        bmesh.ops.scale(bm_hl, vec=(0.0035, 0.004, 0.016), verts=bm_hl.verts)
        ang_hl = math.asin(sign * 0.022 / b_r)
        y_hl = bot_y + b_r * math.cos(ang_hl)
        bmesh.ops.translate(bm_hl, vec=(sign * 0.022, y_hl + 0.0008, visor_z_c), verts=bm_hl.verts)
        mesh_hl = bpy.data.meshes.new(f"Dreame_LED_Headlight_{sign}")
        bm_hl.to_mesh(mesh_hl)
        bm_hl.free()
        obj_hl = bpy.data.objects.new(f"Dreame_LED_Headlight_{sign}", mesh_hl)
        obj_hl.data.materials.append(mat_headlight)
        register_obj(obj_hl, parent=root)

    # D. Outer 3D Structured Light Laser Pockets
    for sign in [-1, 1]:
        bm_las = bmesh.new()
        bmesh.ops.create_cube(bm_las, size=1.0)
        bmesh.ops.scale(bm_las, vec=(0.013, 0.008, 0.024), verts=bm_las.verts)
        ang_las = math.asin(sign * 0.046 / b_r)
        y_las = bot_y + b_r * math.cos(ang_las)
        bmesh.ops.translate(bm_las, vec=(sign * 0.046, y_las - 0.004, visor_z_c), verts=bm_las.verts)

        # Vertical black optical sensor slit inside pocket
        v_slit = bmesh.ops.create_cube(bm_las, size=1.0)['verts']
        bmesh.ops.scale(bm_las, vec=(0.002, 0.003, 0.018), verts=v_slit)
        bmesh.ops.translate(bm_las, vec=(sign * 0.046, y_las - 0.001, visor_z_c), verts=v_slit)

        mesh_las = bpy.data.meshes.new(f"Dreame_3D_Laser_Pocket_{sign}")
        bm_las.to_mesh(mesh_las)
        bm_las.free()
        obj_las = bpy.data.objects.new(f"Dreame_3D_Laser_Pocket_{sign}", mesh_las)
        obj_las.data.materials.append(mat_dark)
        register_obj(obj_las, parent=root)

    # E. "AI Action" Text Badges above Visor on White Bumper (Matching dreame2.png!)
    # Red "AI" on the viewer's left (+X in local coords when viewed from front)
    bm_ai = bmesh.new()
    bmesh.ops.create_cube(bm_ai, size=1.0)
    bmesh.ops.scale(bm_ai, vec=(0.007, 0.0006, 0.0035), verts=bm_ai.verts)
    bmesh.ops.translate(bm_ai, vec=(0.008, bot_y + b_r + 0.0008, visor_z_t + 0.005), verts=bm_ai.verts)
    mesh_ai = bpy.data.meshes.new("Dreame_Badge_AI")
    bm_ai.to_mesh(mesh_ai)
    bm_ai.free()
    obj_ai = bpy.data.objects.new("Dreame_Badge_AI", mesh_ai)
    obj_ai.data.materials.append(mat_red)
    register_obj(obj_ai, parent=root)

    # Silver "Action" on the viewer's right (-X in local coords when viewed from front)
    bm_act = bmesh.new()
    bmesh.ops.create_cube(bm_act, size=1.0)
    bmesh.ops.scale(bm_act, vec=(0.016, 0.0006, 0.0035), verts=bm_act.verts)
    bmesh.ops.translate(bm_act, vec=(-0.007, bot_y + b_r + 0.0008, visor_z_t + 0.005), verts=bm_act.verts)
    mesh_act = bpy.data.meshes.new("Dreame_Badge_Action")
    bm_act.to_mesh(mesh_act)
    bm_act.free()
    obj_act = bpy.data.objects.new("Dreame_Badge_Action", mesh_act)
    obj_act.data.materials.append(mat_grey)
    register_obj(obj_act, parent=root)

    # F. Right Side Wall-Following Sensor (Matching dreame2.png)
    bm_side = bmesh.new()
    bmesh.ops.create_cube(bm_side, size=1.0)
    bmesh.ops.scale(bm_side, vec=(0.024, 0.008, 0.018), verts=bm_side.verts)
    ang_s = -math.radians(45.0)
    bmesh.ops.rotate(bm_side, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(ang_s, 4, 'Z'), verts=bm_side.verts)
    bmesh.ops.translate(bm_side, vec=(-0.124, bot_y + 0.124, visor_z_c), verts=bm_side.verts)
    mesh_side = bpy.data.meshes.new("Dreame_Robot_Side_Sensor")
    bm_side.to_mesh(mesh_side)
    bm_side.free()
    obj_side = bpy.data.objects.new("Dreame_Robot_Side_Sensor", mesh_side)
    obj_side.data.materials.append(mat_glossy_black)
    register_obj(obj_side, parent=root)

    # -------------------------------------------------------------------------
    # 10. LIDAR TURRET WITH FLAT BRUSHED CAP & 4 PILLARS (Matching dreame2.png)
    # -------------------------------------------------------------------------
    lidar_x = 0.0
    lidar_y = bot_y
    turret_r = 0.038
    cap_r = 0.0365

    # A. Smooth White Collar Base
    bm_lcol = bmesh.new()
    res_col = bmesh.ops.create_cone(bm_lcol, cap_ends=True, radius1=turret_r + 0.006, radius2=turret_r, depth=0.007, segments=48)
    bmesh.ops.translate(bm_lcol, vec=(lidar_x, lidar_y, deck_z + 0.0035), verts=res_col['verts'])
    mesh_lcol = bpy.data.meshes.new("Dreame_Robot_LiDAR_Collar")
    bm_lcol.to_mesh(mesh_lcol)
    bm_lcol.free()
    obj_lcol = bpy.data.objects.new("Dreame_Robot_LiDAR_Collar", mesh_lcol)
    obj_lcol.data.materials.append(mat_white)
    register_obj(obj_lcol, parent=root)

    # B. 360-degree Dark Sensor Chamber with 4 Vertical Black Support Pillars
    chamber_z_b = deck_z + 0.007
    chamber_h = 0.011
    bm_lcham = bmesh.new()
    res_cham = bmesh.ops.create_cone(bm_lcham, cap_ends=True, radius1=turret_r - 0.002, radius2=turret_r - 0.002, depth=chamber_h, segments=48)
    bmesh.ops.translate(bm_lcham, vec=(lidar_x, lidar_y, chamber_z_b + chamber_h / 2.0), verts=res_cham['verts'])

    for pil_ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
        px = (turret_r - 0.001) * math.cos(pil_ang)
        py = (turret_r - 0.001) * math.sin(pil_ang)
        v_pil = bmesh.ops.create_cube(bm_lcham, size=1.0)['verts']
        bmesh.ops.scale(bm_lcham, vec=(0.0035, 0.0035, chamber_h), verts=v_pil)
        bmesh.ops.translate(bm_lcham, vec=(lidar_x + px, lidar_y + py, chamber_z_b + chamber_h / 2.0), verts=v_pil)

    mesh_lcham = bpy.data.meshes.new("Dreame_Robot_LiDAR_Chamber")
    bm_lcham.to_mesh(mesh_lcham)
    bm_lcham.free()
    obj_lcham = bpy.data.objects.new("Dreame_Robot_LiDAR_Chamber", mesh_lcham)
    obj_lcham.data.materials.append(mat_dark)
    register_obj(obj_lcham, parent=root)

    # C. FLAT Brushed Champagne Metallic Cap with Chamfered Edge (Exact replica of dreame2.png!)
    cap_z = chamber_z_b + chamber_h
    cap_thick = 0.0032
    bm_lcap = bmesh.new()
    v_cap_bot = []
    v_cap_mid = []
    v_cap_top = []
    n_cseg = 48
    for i in range(n_cseg):
        ang = 2.0 * math.pi * (i / float(n_cseg))
        cx = math.cos(ang)
        cy = math.sin(ang)
        v_cap_bot.append(bm_lcap.verts.new((lidar_x + cap_r * cx, lidar_y + cap_r * cy, cap_z)))
        v_cap_mid.append(bm_lcap.verts.new((lidar_x + cap_r * cx, lidar_y + cap_r * cy, cap_z + cap_thick - 0.0008)))
        v_cap_top.append(bm_lcap.verts.new((lidar_x + (cap_r - 0.0012) * cx, lidar_y + (cap_r - 0.0012) * cy, cap_z + cap_thick)))

    for i in range(n_cseg):
        i_next = (i + 1) % n_cseg
        bm_lcap.faces.new((v_cap_bot[i], v_cap_bot[i_next], v_cap_mid[i_next], v_cap_mid[i]))
        bm_lcap.faces.new((v_cap_mid[i], v_cap_mid[i_next], v_cap_top[i_next], v_cap_top[i]))

    v_cap_center = bm_lcap.verts.new((lidar_x, lidar_y, cap_z + cap_thick))
    for i in range(n_cseg):
        i_next = (i + 1) % n_cseg
        bm_lcap.faces.new((v_cap_top[i], v_cap_top[i_next], v_cap_center))

    bmesh.ops.recalc_face_normals(bm_lcap, faces=bm_lcap.faces)
    mesh_lcap = bpy.data.meshes.new("Dreame_Robot_LiDAR_Cap")
    bm_lcap.to_mesh(mesh_lcap)
    bm_lcap.free()
    obj_lcap = bpy.data.objects.new("Dreame_Robot_LiDAR_Cap", mesh_lcap)
    obj_lcap.data.materials.append(mat_champagne)
    register_obj(obj_lcap, parent=root)

    # Laser Engraving text ring on Cap
    bm_ltxt = bmesh.new()
    bmesh.ops.create_cone(bm_ltxt, cap_ends=False, radius1=0.022, radius2=0.022, depth=0.0004, segments=36)
    bmesh.ops.translate(bm_ltxt, vec=(lidar_x, lidar_y, cap_z + cap_thick + 0.0002), verts=bm_ltxt.verts)
    mesh_ltxt = bpy.data.meshes.new("Dreame_LiDAR_Cap_Engraving")
    bm_ltxt.to_mesh(mesh_ltxt)
    bm_ltxt.free()
    obj_ltxt = bpy.data.objects.new("Dreame_LiDAR_Cap_Engraving", mesh_ltxt)
    obj_ltxt.data.materials.append(mat_grey)
    register_obj(obj_ltxt, parent=root)

    # -------------------------------------------------------------------------
    # 11. BUTTON CONSOLE & DUSTBIN LID SEAM (Matching dreame2.png)
    # -------------------------------------------------------------------------
    btn_y = lidar_y + 0.048
    bm_btray = bmesh.new()
    bmesh.ops.create_cube(bm_btray, size=1.0)
    bmesh.ops.scale(bm_btray, vec=(0.044, 0.013, 0.001), verts=bm_btray.verts)
    bmesh.ops.translate(bm_btray, vec=(0.0, btn_y, deck_z - 0.0002), verts=bm_btray.verts)
    mesh_btray = bpy.data.meshes.new("Dreame_Robot_Button_Tray")
    bm_btray.to_mesh(mesh_btray)
    bm_btray.free()
    obj_btray = bpy.data.objects.new("Dreame_Robot_Button_Tray", mesh_btray)
    obj_btray.data.materials.append(mat_white)
    register_obj(obj_btray, parent=root)

    for i, bx in enumerate([-0.014, 0.0, 0.014]):
        bm_btn = bmesh.new()
        res_btn = bmesh.ops.create_cone(bm_btn, cap_ends=True, radius1=0.0035, radius2=0.0035, depth=0.0008, segments=20)
        bmesh.ops.translate(bm_btn, vec=(bx, btn_y, deck_z + 0.0004), verts=res_btn['verts'])
        mesh_btn = bpy.data.meshes.new(f"Dreame_Robot_Button_{i}")
        bm_btn.to_mesh(mesh_btn)
        bm_btn.free()
        obj_btn = bpy.data.objects.new(f"Dreame_Robot_Button_{i}", mesh_btn)
        obj_btn.data.materials.append(mat_champagne)
        register_obj(obj_btn, parent=root)

    # Dustbin Lid Seam
    bm_seam = bmesh.new()
    seam_pts = []
    for i in range(36):
        ang = -math.pi / 3.0 + (4.0 * math.pi / 3.0) * (i / 35.0)
        sx = 0.062 * math.cos(ang)
        sy = lidar_y + 0.062 * math.sin(ang)
        seam_pts.append((sx, sy))
    for i in range(len(seam_pts) - 1):
        p1 = seam_pts[i]
        p2 = seam_pts[i + 1]
        v_seg = bmesh.ops.create_cube(bm_seam, size=1.0)['verts']
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx*dx + dy*dy)
        bmesh.ops.scale(bm_seam, vec=(length, 0.0012, 0.0008), verts=v_seg)
        bmesh.ops.rotate(bm_seam, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.atan2(dy, dx), 4, 'Z'), verts=v_seg)
        bmesh.ops.translate(bm_seam, vec=((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, deck_z + 0.0004), verts=v_seg)

    mesh_seam = bpy.data.meshes.new("Dreame_Robot_Lid_Seam")
    bm_seam.to_mesh(mesh_seam)
    bm_seam.free()
    obj_seam = bpy.data.objects.new("Dreame_Robot_Lid_Seam", mesh_seam)
    obj_seam.data.materials.append(mat_dark)
    register_obj(obj_seam, parent=root)

    # "DREAME" text logo on rear deck of robot
    bm_rlogo = bmesh.new()
    bmesh.ops.create_cube(bm_rlogo, size=1.0)
    bmesh.ops.scale(bm_rlogo, vec=(0.032, 0.0006, 0.005), verts=bm_rlogo.verts)
    bmesh.ops.translate(bm_rlogo, vec=(0.0, bot_y - 0.080, deck_z + 0.0004), verts=bm_rlogo.verts)
    mesh_rlogo = bpy.data.meshes.new("Dreame_Robot_Logo")
    bm_rlogo.to_mesh(mesh_rlogo)
    bm_rlogo.free()
    obj_rlogo = bpy.data.objects.new("Dreame_Robot_Logo", mesh_rlogo)
    obj_rlogo.data.materials.append(mat_grey)
    register_obj(obj_rlogo, parent=root)

    # -------------------------------------------------------------------------
    # 12. UNDERSIDE DETAILS: CASTER WHEEL & FLEXARM SIDE BRUSH (Matching dreame2.png)
    # -------------------------------------------------------------------------
    bm_caster = bmesh.new()
    v_cbra = bmesh.ops.create_cube(bm_caster, size=1.0)['verts']
    bmesh.ops.scale(bm_caster, vec=(0.026, 0.030, 0.010), verts=v_cbra)
    bmesh.ops.translate(bm_caster, vec=(0.0, bot_y + bot_r - 0.040, bot_z_base + 0.008), verts=v_cbra)

    res_cw = bmesh.ops.create_cone(bm_caster, cap_ends=True, radius1=0.009, radius2=0.009, depth=0.014, segments=20)
    bmesh.ops.rotate(bm_caster, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.pi / 2.0, 4, 'Y'), verts=res_cw['verts'])
    bmesh.ops.translate(bm_caster, vec=(0.0, bot_y + bot_r - 0.040, bot_z_base + 0.004), verts=res_cw['verts'])

    mesh_caster = bpy.data.meshes.new("Dreame_Front_Caster_Wheel")
    bm_caster.to_mesh(mesh_caster)
    bm_caster.free()
    obj_caster = bpy.data.objects.new("Dreame_Front_Caster_Wheel", mesh_caster)
    obj_caster.data.materials.append(mat_rubber)
    register_obj(obj_caster, parent=root)

    # FlexArm Side Brush (Right side quadrant, matching dreame1.png and dreame2.png)
    brush_x = -0.132
    brush_y = bot_y + 0.100
    brush_z = bot_z_base + 0.004
    bm_brush = bmesh.new()
    res_bhub = bmesh.ops.create_cone(bm_brush, cap_ends=True, radius1=0.010, radius2=0.008, depth=0.005, segments=18)
    bmesh.ops.translate(bm_brush, vec=(brush_x, brush_y, brush_z), verts=res_bhub['verts'])

    for a in range(3):
        ang_b = a * (2.0 * math.pi / 3.0) + math.radians(20)
        v_arm = bmesh.ops.create_cube(bm_brush, size=1.0)['verts']
        bmesh.ops.scale(bm_brush, vec=(0.046, 0.0035, 0.002), verts=v_arm)
        bmesh.ops.rotate(bm_brush, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(ang_b, 4, 'Z'), verts=v_arm)
        bmesh.ops.translate(bm_brush, vec=(brush_x + 0.024 * math.cos(ang_b), brush_y + 0.024 * math.sin(ang_b), brush_z - 0.001), verts=v_arm)

        v_bris = bmesh.ops.create_cube(bm_brush, size=1.0)['verts']
        bmesh.ops.scale(bm_brush, vec=(0.014, 0.007, 0.0018), verts=v_bris)
        bmesh.ops.rotate(bm_brush, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(ang_b + math.radians(35), 4, 'Z'), verts=v_bris)
        bmesh.ops.translate(bm_brush, vec=(brush_x + 0.046 * math.cos(ang_b), brush_y + 0.046 * math.sin(ang_b), brush_z - 0.002), verts=v_bris)

    mesh_brush = bpy.data.meshes.new("Dreame_Robot_Side_Brush")
    bm_brush.to_mesh(mesh_brush)
    bm_brush.free()
    obj_brush = bpy.data.objects.new("Dreame_Robot_Side_Brush", mesh_brush)
    obj_brush.data.materials.append(mat_dark)
    register_obj(obj_brush, parent=root)

    # -------------------------------------------------------------------------
    # 13. WALL SOCKET & POWER CABLE (Against East Wall)
    # -------------------------------------------------------------------------
    bm_sock = bmesh.new()
    bmesh.ops.create_cube(bm_sock, size=1.0)
    bmesh.ops.scale(bm_sock, vec=(0.084, 0.010, 0.084), verts=bm_sock.verts)
    bmesh.ops.translate(bm_sock, vec=(-0.250, -0.210, 0.345), verts=bm_sock.verts)

    res_plug = bmesh.ops.create_cone(bm_sock, cap_ends=True, radius1=0.018, radius2=0.018, depth=0.028, segments=24)
    bmesh.ops.rotate(bm_sock, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.pi / 2.0, 4, 'X'), verts=res_plug['verts'])
    bmesh.ops.translate(bm_sock, vec=(-0.250, -0.198, 0.345), verts=res_plug['verts'])

    mesh_sock = bpy.data.meshes.new("Dreame_Wall_Socket")
    bm_sock.to_mesh(mesh_sock)
    bm_sock.free()
    obj_sock = bpy.data.objects.new("Dreame_Wall_Socket", mesh_sock)
    obj_sock.data.materials.append(mat_socket)
    register_obj(obj_sock, parent=root)

    curve_data = bpy.data.curves.new("Dreame_Power_Cable", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.0035
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(3)

    pts_cable = [
        ((-0.250, -0.185, 0.345), (-0.250, -0.175, 0.345), (-0.250, -0.185, 0.300)),
        ((-0.245, -0.195, 0.180), (-0.245, -0.195, 0.230), (-0.245, -0.195, 0.120)),
        ((-0.215, -0.200, 0.070), (-0.230, -0.200, 0.070), (-0.195, -0.200, 0.070)),
        ((-0.170, -0.180, 0.075), (-0.185, -0.185, 0.075), (-0.165, -0.175, 0.075))
    ]

    for i, (co, h_l, h_r) in enumerate(pts_cable):
        bp = polyline.bezier_points[i]
        bp.co = co
        bp.handle_left = h_l
        bp.handle_right = h_r

    obj_cable = bpy.data.objects.new("Dreame_Power_Cable", curve_data)
    obj_cable.data.materials.append(mat_white)
    register_obj(obj_cable, parent=root)

    print("=== DREAME L40 ULTRA CAD MODEL SUCCESSFULLY BUILT ===")

if __name__ == '__main__':
    build_dreame_perfect()
    bpy.ops.wm.save_mainfile()
