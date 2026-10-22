import bpy

# Let's inspect Interior_Door_Frames or interior walls
door_obj = bpy.data.objects.get("Doors_Interior") or bpy.data.objects.get("Interior_Door_Frames")
if door_obj:
    print(f"Door obj: {door_obj.name}")
    # inspect mesh vertices near 1.06
    mw = door_obj.matrix_world
    verts_106 = [mw @ v.co for v in door_obj.data.vertices if 0.0 <= (mw @ v.co).x <= 4.8 and 0.0 <= (mw @ v.co).y <= 4.2]
    print(f"Door vertices near 1.06: count = {len(verts_106)}")
    if verts_106:
        xs = [v.x for v in verts_106]
        ys = [v.y for v in verts_106]
        print(f"Door near 1.06 bounds: X=[{min(xs):.3f}, {max(xs):.3f}], Y=[{min(ys):.3f}, {max(ys):.3f}]")

# Let's check window Window_1.06_South
win = bpy.data.objects.get("Window_1.06_South")
if win:
    print(f"Window_1.06_South: loc={win.location}, rot={win.rotation_euler}, dim={win.dimensions}")

# Check Wooden Cupboard
wb = bpy.data.objects.get("Wooden Cupboard")
if wb:
    print(f"Wooden Cupboard: loc={wb.location}, rot={wb.rotation_euler}, dim={wb.dimensions}")

# Check existing Kallax
k = bpy.data.objects.get("Ikea Kallax 147x147cm")
if k:
    print(f"Ikea Kallax 147x147cm: loc={k.location}, rot={k.rotation_euler}, dim={k.dimensions}")
