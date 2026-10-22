import bpy

print("="*60)
print("ALL COLLECTIONS:")
for c in bpy.data.collections:
    print(f"Collection: {c.name} ({len(c.objects)} objects)")

print("\nOBJECTS IN ROOM 1.06 BOUNDING BOX (X: 0.3 to 4.5, Y: 0.3 to 4.0):")
for obj in bpy.data.objects:
    loc = obj.matrix_world.translation
    if 0.2 <= loc.x <= 4.6 and 0.2 <= loc.y <= 4.2:
        print(f"  {obj.name} ({obj.type}): loc=({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f}), dim=({obj.dimensions.x:.3f}, {obj.dimensions.y:.3f}, {obj.dimensions.z:.3f}), coll={[c.name for c in obj.users_collection]}")

print("\nOBJECTS MATCHING 'Kallax' or '1.06' or 'Pokoj':")
for obj in bpy.data.objects:
    if any(k in obj.name.lower() for k in ['kallax', '1.06', 'pokoj', 'desk', 'stul', 'stůl', 'skrin', 'skříň']):
        print(f"  {obj.name}: loc={tuple(round(v, 3) for v in obj.location)}, coll={[c.name for c in obj.users_collection]}")

print("="*60)
