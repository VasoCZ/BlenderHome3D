import bpy

print('=== THOROUGH VERIFICATION REPORT ===')

# 1. Floor & Threshold materials
print('\n[1] Floors and Thresholds:')
expected_koupelna = [
    'Floor_1.01_Zadveri', 'Floor_1.08_WC', 'Floor_1.09_Technicka_mistnost',
    'Floor_1.10_Koupelna', 'Floor_1.11_Chodba',
    'Floor_Threshold_101_102', 'Floor_Threshold_104_111',
    'Floor_Threshold_111_108', 'Floor_Threshold_111_109', 'Floor_Threshold_111_110',
    'Floor_Threshold_Front_Entrance'
]
all_floors_ok = True
for name in expected_koupelna:
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f'  ERROR: {name} not found!')
        all_floors_ok = False
        continue
    mats = [s.material.name if s.material else 'NONE' for s in obj.material_slots]
    if 'koupelna' not in mats:
        print(f'  ERROR: {name} does not have koupelna! Has: {mats}')
        all_floors_ok = False
    else:
        print(f'  OK: {name} -> {mats}')

if all_floors_ok:
    print('  ==> ALL wet-room floors and thresholds correctly have original "koupelna" material.')

# 2. Kallax in office
print('\n[2] Office Kallax:')
k1 = bpy.data.objects.get('Ikea Kallax 147x147cm.001')
k2 = bpy.data.objects.get('Ikea Kallax 147x147cm.002')
for k in [k1, k2]:
    if k:
        print(f'  OK: {k.name}: loc={k.location}, in collections={[c.name for c in k.users_collection]}, mats={[m.name for m in k.data.materials if m]}')
    else:
        print(f'  ERROR: {k} missing!')

# 3. Doors
print('\n[3] Doors in scene:')
door_leaves = [o.name for o in bpy.data.objects if o.name.startswith('DoorLeaf_')]
print(f'  Door leaves: {door_leaves} (exactly 1 preserved: {"OK" if door_leaves == ["DoorLeaf_102_105"] else "FAIL"})')

# 4. Bathroom
print('\n[4] Bathroom status:')
bath_objs = [o.name for o in bpy.data.objects if o.name.startswith('Bath_')]
print(f'  Bath_* objects present: {len(bath_objs)} (should be 0: {"OK" if len(bath_objs) == 0 else "FAIL"})')
sh = bpy.data.objects.get('Shower')
ss = bpy.data.objects.get('Shower Set')
print(f'  Original Shower: {"OK" if sh else "MISSING"}, Shower Set: {"OK" if ss else "MISSING"}')

# 5. Wood decors
print('\n[5] Gold Craft Oak decor:')
check_oak_objs = [
    ('Dining_Table', 0),
    ('Comoda', 0),
    ('Ikea Kallax 147x147cm', 0),
    ('Body', 0),
    ('Doors', 0),
    ('TV cabinet', 0),
    ('Bristol-shelf', 0)
]
for oname, sidx in check_oak_objs:
    obj = bpy.data.objects.get(oname)
    if obj:
        slot_mat = obj.material_slots[sidx].material.name if len(obj.material_slots) > sidx and obj.material_slots[sidx].material else 'NONE'
        print(f'  {oname} (slot {sidx}): {slot_mat} ({"OK" if "Gold_Craft_Oak" in slot_mat else "FAIL"})')
    else:
        print(f'  {oname}: MISSING!')

# 6. Active camera
print('\n[6] Camera & Viewport:')
print(f'  Active Camera: {bpy.context.scene.camera.name}')
