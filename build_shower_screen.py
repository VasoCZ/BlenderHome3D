import bpy
import bmesh
import math
from mathutils import Vector, Matrix

print("======================================================================")
print("--- BUILDING WALK-IN SHOWER SCREEN (ALIGNED TO REAL SPRCHA.JPG) ---")
print("======================================================================")

# 1. Setup Collection
COLL_NAME = "Bathroom_Fixtures"
coll = bpy.data.collections.get(COLL_NAME)
if not coll:
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)

# Clean up all existing shower screen objects
for obj in list(bpy.data.objects):
    if obj.name.startswith("Bath_Shower"):
        print(f"Removing old object: {obj.name}")
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Materials Setup
# 2a. Clear Glass
mat_glass = bpy.data.materials.get("Glass_Clear")
if not mat_glass:
    mat_glass = bpy.data.materials.new(name="Glass_Clear")
    mat_glass.use_nodes = True
    bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Roughness'].default_value = 0.005
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 1.0
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 1.0
        bsdf.inputs['IOR'].default_value = 1.52

# 2b. Mirror Stripes Material (Mat_Shower_Mirror_Stripes)
mat_mirror = bpy.data.materials.get("Mat_Shower_Mirror_Stripes")
if not mat_mirror:
    mat_mirror = bpy.data.materials.new(name="Mat_Shower_Mirror_Stripes")
    mat_mirror.use_nodes = True
tree = mat_mirror.node_tree
tree.nodes.clear()
out_node = tree.nodes.new(type='ShaderNodeOutputMaterial')
p_node = tree.nodes.new(type='ShaderNodeBsdfPrincipled')
p_node.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
p_node.inputs['Metallic'].default_value = 1.0
p_node.inputs['Roughness'].default_value = 0.015
if 'Specular IOR Level' in p_node.inputs:
    p_node.inputs['Specular IOR Level'].default_value = 1.0
tree.links.new(p_node.outputs['BSDF'], out_node.inputs['Surface'])

# 2c. Chrome Material
mat_chrome = bpy.data.materials.get("Mat_Kitchen_Chrome")
if not mat_chrome:
    mat_chrome = bpy.data.materials.get("Chrome.002")

# 2d. Rubber Gasket Material
mat_rubber = bpy.data.materials.get("Mat_Shower_Black_Rubber")
if not mat_rubber:
    mat_rubber = bpy.data.materials.new(name="Mat_Shower_Black_Rubber")
    mat_rubber.use_nodes = True
    bsdf = mat_rubber.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.65
        bsdf.inputs['Metallic'].default_value = 0.0

# 2e. Brushed Stainless Steel
mat_steel = bpy.data.materials.get("Mat_Brushed_Stainless_Steel")
if not mat_steel:
    mat_steel = mat_chrome

# -------------------------------------------------------------------------
# Position Shower Column on South Wall (Y = 9.918)
# -------------------------------------------------------------------------
shower_obj = bpy.data.objects.get("Shower")
if shower_obj:
    shower_obj.matrix_world = Matrix.Translation((0.720, 9.918, 1.0181)) @ Matrix.Rotation(math.radians(180), 4, 'Z')
    print("Mounted Shower Column on South wall (X=0.72, Y=9.92, Z=1.02, facing North)")

# -------------------------------------------------------------------------
# 3. MODEL: Glass Screen with 3 Mirror Bands (Bath_Shower_Glass_Screen)
# -------------------------------------------------------------------------
# Geometry:
# West wall attachment: X = 0.365
# Outer edge into bathroom: X = 1.368 (length = 1.003 m)
# Glass thickness: 8 mm, centered at Y = 10.888 (Y from 10.884 to 10.892)
# Height: 2.000 m (Z from 0.018 to 2.018)

x_start = 0.365
x_end = 1.368
y_min = 10.884
y_max = 10.892

# 3 Mirror bands (each 16cm high, spaced by 8cm clear gaps)
# Band 0: Clear Glass [0.018, 0.820] (80.2 cm)
# Band 1: Mirror Strip 3 [0.820, 0.980] (16.0 cm)
# Band 2: Clear Gap 2 [0.980, 1.060] (8.0 cm)
# Band 3: Mirror Strip 2 [1.060, 1.220] (16.0 cm)
# Band 4: Clear Gap 1 [1.220, 1.300] (8.0 cm)
# Band 5: Mirror Strip 1 [1.300, 1.460] (16.0 cm)
# Band 6: Clear Glass Top [1.460, 2.018] (55.8 cm)

z_levels = [0.018, 0.820, 0.980, 1.060, 1.220, 1.300, 1.460, 2.018]
mirror_band_indices = [1, 3, 5]

mesh_glass = bpy.data.meshes.new("Mesh_Bath_Shower_Glass_Screen")
bm_g = bmesh.new()

rings = []
for z in z_levels:
    v0 = bm_g.verts.new((x_start, y_min, z))
    v1 = bm_g.verts.new((x_end, y_min, z))
    v2 = bm_g.verts.new((x_end, y_max, z))
    v3 = bm_g.verts.new((x_start, y_max, z))
    rings.append((v0, v1, v2, v3))

# Bottom cap
f_bot = bm_g.faces.new([rings[0][0], rings[0][3], rings[0][2], rings[0][1]])
f_bot.material_index = 0

# Vertical segments
for k in range(len(z_levels) - 1):
    mat_idx = 1 if k in mirror_band_indices else 0
    r_low = rings[k]
    r_high = rings[k+1]
    
    # South face (facing inside shower)
    f_south = bm_g.faces.new([r_low[0], r_low[1], r_high[1], r_high[0]])
    f_south.material_index = mat_idx
    
    # East face (outer edge)
    f_east = bm_g.faces.new([r_low[1], r_low[2], r_high[2], r_high[1]])
    f_east.material_index = mat_idx
    
    # North face (facing outside room)
    f_north = bm_g.faces.new([r_low[2], r_low[3], r_high[3], r_high[2]])
    f_north.material_index = mat_idx
    
    # West face (against wall profile)
    f_west = bm_g.faces.new([r_low[3], r_low[0], r_high[0], r_high[3]])
    f_west.material_index = mat_idx

# Top cap
f_top = bm_g.faces.new([rings[-1][0], rings[-1][1], rings[-1][2], rings[-1][3]])
f_top.material_index = 0

bm_g.to_mesh(mesh_glass)
bm_g.free()

obj_glass = bpy.data.objects.new("Bath_Shower_Glass_Screen", mesh_glass)
obj_glass.data.materials.append(mat_glass)   # Slot 0
obj_glass.data.materials.append(mat_mirror)  # Slot 1
coll.objects.link(obj_glass)
print(f"Created {obj_glass.name} (length 1.00m, height 2.00m, 3 mirror stripes)")

# -------------------------------------------------------------------------
# 4. MODEL: West Wall U-Profile (Bath_Shower_Wall_Profile)
# -------------------------------------------------------------------------
mesh_prof = bpy.data.meshes.new("Mesh_Bath_Shower_Wall_Profile")
bm_p = bmesh.new()
# Outer U-channel: X from 0.365 to 0.388, Y from 10.875 to 10.901, Z from 0.015 to 2.022
bmesh.ops.create_cube(bm_p, size=1.0, 
                      matrix=Matrix.Translation((0.376, 10.888, 1.0185)) @ 
                             Matrix.Diagonal((0.023, 0.026, 2.007, 1.0)))
# Top cap
bmesh.ops.create_cube(bm_p, size=1.0,
                      matrix=Matrix.Translation((0.376, 10.888, 2.0235)) @
                             Matrix.Diagonal((0.025, 0.028, 0.005, 1.0)))
bm_p.to_mesh(mesh_prof)
bm_p.free()

obj_prof = bpy.data.objects.new("Bath_Shower_Wall_Profile", mesh_prof)
obj_prof.data.materials.append(mat_chrome)
coll.objects.link(obj_prof)

# -------------------------------------------------------------------------
# 5. MODEL: Bottom Sealing Profile (Bath_Shower_Bottom_Seal)
# -------------------------------------------------------------------------
mesh_bseal = bpy.data.meshes.new("Mesh_Bath_Shower_Bottom_Seal")
bm_bs = bmesh.new()
bmesh.ops.create_cube(bm_bs, size=1.0,
                      matrix=Matrix.Translation((0.875, 10.888, 0.0165)) @
                             Matrix.Diagonal((0.980, 0.014, 0.005, 1.0)))
bm_bs.to_mesh(mesh_bseal)
bm_bs.free()
obj_bseal = bpy.data.objects.new("Bath_Shower_Bottom_Seal", mesh_bseal)
obj_bseal.data.materials.append(mat_chrome)
coll.objects.link(obj_bseal)

# -------------------------------------------------------------------------
# 6. MODEL: Top Stabilizer Bar (Bath_Shower_Stabilizer_Bar)
# -------------------------------------------------------------------------
# Square chrome tube 20mm x 20mm spanning from South wall (Y = 9.900) to glass clamp (Y = 10.888)
# At X = 1.250 (approx 12 cm from outer edge of glass), Z = 2.030 (just above glass top at 2.018)
mesh_bar = bpy.data.meshes.new("Mesh_Bath_Shower_Stabilizer_Bar")
bm_bar = bmesh.new()
bar_y_len = 10.888 - 9.900
bar_center_y = (9.900 + 10.888) / 2.0
bar_x = 1.250
bmesh.ops.create_cube(bm_bar, size=1.0,
                      matrix=Matrix.Translation((bar_x, bar_center_y, 2.030)) @
                             Matrix.Diagonal((0.020, bar_y_len, 0.020, 1.0)))
bm_bar.to_mesh(mesh_bar)
bm_bar.free()

obj_bar = bpy.data.objects.new("Bath_Shower_Stabilizer_Bar", mesh_bar)
obj_bar.data.materials.append(mat_chrome)
coll.objects.link(obj_bar)

# -------------------------------------------------------------------------
# 7. MODEL: South Wall Mount Bracket / Flange (Bath_Shower_Wall_Bracket)
# -------------------------------------------------------------------------
mesh_wb = bpy.data.meshes.new("Mesh_Bath_Shower_Wall_Bracket")
bm_wb = bmesh.new()
# Wall escutcheon plate on South wall (Y = 9.900)
bmesh.ops.create_cube(bm_wb, size=1.0,
                      matrix=Matrix.Translation((bar_x, 9.905, 2.030)) @
                             Matrix.Diagonal((0.044, 0.010, 0.044, 1.0)))
# Socket collar
bmesh.ops.create_cube(bm_wb, size=1.0,
                      matrix=Matrix.Translation((bar_x, 9.918, 2.030)) @
                             Matrix.Diagonal((0.028, 0.016, 0.028, 1.0)))
bm_wb.to_mesh(mesh_wb)
bm_wb.free()

obj_wb = bpy.data.objects.new("Bath_Shower_Wall_Bracket", mesh_wb)
obj_wb.data.materials.append(mat_chrome)
coll.objects.link(obj_wb)

# -------------------------------------------------------------------------
# 8. MODEL: Top Chrome Glass Clamp (Bath_Shower_Glass_Clamp)
# -------------------------------------------------------------------------
# Precision bracket gripping top edge of glass:
# Sleeve receiving tube, plus two clamping jaws extending down both sides of glass
mesh_clamp = bpy.data.meshes.new("Mesh_Bath_Shower_Glass_Clamp")
bm_cl = bmesh.new()

clamp_x = bar_x
clamp_y = 10.888
clamp_z = 2.018

# A. Top Clamp Head / Sleeve
bmesh.ops.create_cube(bm_cl, size=1.0,
                      matrix=Matrix.Translation((clamp_x, clamp_y, 2.030)) @
                             Matrix.Diagonal((0.042, 0.038, 0.024, 1.0)))

# B. Clamping Jaws straddling the 8mm glass (glass Y from 10.884 to 10.892)
# South Jaw (inside shower): Y center = 10.876, thickness = 0.014, height = 0.032 (Z from 1.986 to 2.018)
bmesh.ops.create_cube(bm_cl, size=1.0,
                      matrix=Matrix.Translation((clamp_x, 10.877, 2.002)) @
                             Matrix.Diagonal((0.042, 0.012, 0.032, 1.0)))

# North Jaw (outside shower): Y center = 10.900, thickness = 0.014, height = 0.032 (Z from 1.986 to 2.018)
bmesh.ops.create_cube(bm_cl, size=1.0,
                      matrix=Matrix.Translation((clamp_x, 10.899, 2.002)) @
                             Matrix.Diagonal((0.042, 0.012, 0.032, 1.0)))

# C. Clamping hex bolt head detail on the inside (South) jaw
bmesh.ops.create_cone(bm_cl, cap_ends=True, cap_tris=False, radius1=0.005, radius2=0.005, depth=0.004,
                      matrix=Matrix.Translation((clamp_x, 10.870, 2.002)) @
                             Matrix.Rotation(math.radians(90), 4, 'X'))

# D. Black protective gasket pads directly integrated
bmesh.ops.create_cube(bm_cl, size=1.0,
                      matrix=Matrix.Translation((clamp_x, 10.8835, 2.002)) @
                             Matrix.Diagonal((0.040, 0.001, 0.030, 1.0)))
bmesh.ops.create_cube(bm_cl, size=1.0,
                      matrix=Matrix.Translation((clamp_x, 10.8925, 2.002)) @
                             Matrix.Diagonal((0.040, 0.001, 0.030, 1.0)))

bm_cl.to_mesh(mesh_clamp)
bm_cl.free()

obj_clamp = bpy.data.objects.new("Bath_Shower_Glass_Clamp", mesh_clamp)
obj_clamp.data.materials.append(mat_chrome)
coll.objects.link(obj_clamp)

# -------------------------------------------------------------------------
# 9. MODEL: Over-the-Glass Chrome Double Towel Hook (as in sprcha.jpg)
# -------------------------------------------------------------------------
mesh_hook = bpy.data.meshes.new("Mesh_Bath_Shower_Towel_Hook")
bm_hk = bmesh.new()
hook_x = 0.950
# Top bridge over glass
bmesh.ops.create_cube(bm_hk, size=1.0,
                      matrix=Matrix.Translation((hook_x, 10.888, 2.023)) @
                             Matrix.Diagonal((0.030, 0.020, 0.006, 1.0)))
# Downward outer stem (towards North)
bmesh.ops.create_cube(bm_hk, size=1.0,
                      matrix=Matrix.Translation((hook_x, 10.896, 1.960)) @
                             Matrix.Diagonal((0.024, 0.005, 0.120, 1.0)))
# Upward outer hook prong
bmesh.ops.create_cube(bm_hk, size=1.0,
                      matrix=Matrix.Translation((hook_x, 10.910, 1.910)) @
                             Matrix.Diagonal((0.020, 0.024, 0.006, 1.0)))
bmesh.ops.create_cube(bm_hk, size=1.0,
                      matrix=Matrix.Translation((hook_x, 10.920, 1.930)) @
                             Matrix.Diagonal((0.020, 0.005, 0.036, 1.0)))
bm_hk.to_mesh(mesh_hook)
bm_hk.free()

obj_hook = bpy.data.objects.new("Bath_Shower_Towel_Hook", mesh_hook)
obj_hook.data.materials.append(mat_chrome)
coll.objects.link(obj_hook)

# -------------------------------------------------------------------------
# 10. MODEL: Stainless Steel Linear Shower Drain (Bath_Shower_Linear_Drain)
# -------------------------------------------------------------------------
# Runs across shower entrance along X = 1.300, Y from 9.930 to 10.850
mesh_drain = bpy.data.meshes.new("Mesh_Bath_Shower_Linear_Drain")
bm_dr = bmesh.new()
drain_center_y = (9.930 + 10.850) / 2.0
drain_len_y = 10.850 - 9.930
# Drain body rim
bmesh.ops.create_cube(bm_dr, size=1.0,
                      matrix=Matrix.Translation((1.300, drain_center_y, 0.016)) @
                             Matrix.Diagonal((0.065, drain_len_y, 0.003, 1.0)))
# Inner drain slot grate
bmesh.ops.create_cube(bm_dr, size=1.0,
                      matrix=Matrix.Translation((1.300, drain_center_y, 0.017)) @
                             Matrix.Diagonal((0.045, drain_len_y - 0.030, 0.002, 1.0)))
bm_dr.to_mesh(mesh_drain)
bm_dr.free()

obj_drain = bpy.data.objects.new("Bath_Shower_Linear_Drain", mesh_drain)
obj_drain.data.materials.append(mat_steel)
coll.objects.link(obj_drain)

print("--- ALL SHOWER SCREEN ELEMENTS ALIGNED & BUILT SUCCESSFULLY! ---")
