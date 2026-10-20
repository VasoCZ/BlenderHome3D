import bpy
import bmesh
from mathutils import Vector

def inspect_model():
    print("Inspecting dum_pudorys_before_tiling.blend...")
    for name in ['Exterior_Walls', 'Interior_Walls']:
        obj = bpy.data.objects.get(name)
        print(f"Object {name}: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")

inspect_model()
