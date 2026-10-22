import bpy

floor = bpy.data.objects.get("Floor_1.06_Pokoj")
if floor:
    mw = floor.matrix_world
    verts = [mw @ v.co for v in floor.data.vertices]
    min_x = min(v.x for v in verts)
    max_x = max(v.x for v in verts)
    min_y = min(v.y for v in verts)
    max_y = max(v.y for v in verts)
    min_z = min(v.z for v in verts)
    max_z = max(v.z for v in verts)
    print(f"Floor_1.06_Pokoj bounds: X=[{min_x:.3f}, {max_x:.3f}], Y=[{min_y:.3f}, {max_y:.3f}], Z=[{min_z:.3f}, {max_z:.3f}]")

kallax = bpy.data.objects.get("Ikea Kallax 147x147cm")
if kallax:
    print(f"Kallax location: {kallax.location}, rotation_euler: {kallax.rotation_euler}, dimensions: {kallax.dimensions}")

cupboard = bpy.data.objects.get("Wooden Cupboard")
if cupboard:
    print(f"Wooden Cupboard location: {cupboard.location}, rotation_euler: {cupboard.rotation_euler}, dimensions: {cupboard.dimensions}")

# Check doors
for obj in bpy.data.objects:
    if "door" in obj.name.lower():
        loc = obj.matrix_world.translation
        if min_x - 0.5 <= loc.x <= max_x + 0.5 and min_y - 0.5 <= loc.y <= max_y + 0.5:
            print(f"Door near 1.06: {obj.name} at {loc}")

# Check cameras
for cam in bpy.data.cameras:
    print(f"Camera: {cam.name}")
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        print(f"Camera obj: {obj.name} at {obj.location}")
