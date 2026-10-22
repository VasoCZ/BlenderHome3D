import bpy

slab = bpy.data.objects.get("Foundation_Slab")
if slab:
    print(f"Foundation_Slab mesh: {slab.data.name}")
    print(f"Number of polygons: {len(slab.data.polygons)}")
    print(f"UV layers: {[uv.name for uv in slab.data.uv_layers]}")
    # Check material slot assignment per polygon
    mat_counts = {}
    for poly in slab.data.polygons:
        idx = poly.material_index
        mat_counts[idx] = mat_counts.get(idx, 0) + 1
    print(f"Material slot polygon counts: {mat_counts}")
