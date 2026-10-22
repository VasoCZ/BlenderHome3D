import bpy
import mathutils

blinds = bpy.data.objects.get("Blinds_Window_1.06_South")
if blinds:
    mw = blinds.matrix_world
    verts = [mw @ v.co for v in blinds.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    print(f"Blinds 1.06 South: X=[{min(xs):.3f}, {max(xs):.3f}], Y=[{min(ys):.3f}, {max(ys):.3f}], Z=[{min(zs):.3f}, {max(zs):.3f}]")

# Let's inspect Wooden Cupboard rotation:
wb = bpy.data.objects.get("Wooden Cupboard")
if wb:
    print(f"Wooden Cupboard rot deg: {[r * 180 / 3.14159265 for r in wb.rotation_euler]}")
    mw = wb.matrix_world
    bbox = [mw @ mathutils.Vector(b) for b in wb.bound_box]
    xs = [v.x for v in bbox]
    ys = [v.y for v in bbox]
    zs = [v.z for v in bbox]
    print(f"Wooden Cupboard bbox: X=[{min(xs):.3f}, {max(xs):.3f}], Y=[{min(ys):.3f}, {max(ys):.3f}], Z=[{min(zs):.3f}, {max(zs):.3f}]")

# Let's inspect Ikea Kallax 147x147cm:
k = bpy.data.objects.get("Ikea Kallax 147x147cm")
if k:
    mw = k.matrix_world
    bbox = [mw @ mathutils.Vector(b) for b in k.bound_box]
    xs = [v.x for v in bbox]
    ys = [v.y for v in bbox]
    zs = [v.z for v in bbox]
    print(f"Kallax bbox: X=[{min(xs):.3f}, {max(xs):.3f}], Y=[{min(ys):.3f}, {max(ys):.3f}], Z=[{min(zs):.3f}, {max(zs):.3f}]")
