import zipfile
import os
import time

project_dir = r"C:\Users\Vaso\Antigravity\Project blender"
zip_out = os.path.join(project_dir, "dum_pudorys_master_backup.zip")

files_to_pack = [
    "dum_pudorys.blend",
    "dum_pudorys_overview.png",
    "dum_pudorys_daylight_final.png",
    "dum_pudorys_night_overview.png",
    "dum_pudorys_night_dark.png",
    "build_shower_screen.py",
    "render_and_save_shower.py",
    "build_full_skoda_scala.py",
    "build_mammotion_yuka.py",
    "apply_terrace_fix.py",
    "render_exact_user_modes.py",
    "BUILD_SPECIFICATION_1TO1.md",
    "README.md",
    ".gitignore",
    os.path.join("assets", "license_plate_1AH_U743.png"),
    os.path.join("assets", "K003_PW_Gold_Craft_Oak.jpg"),
]

# Add assets/skoda_official
skoda_dir = os.path.join(project_dir, "assets", "skoda_official")
if os.path.exists(skoda_dir):
    for f in os.listdir(skoda_dir):
        files_to_pack.append(os.path.join("assets", "skoda_official", f))

# Add assets/k003_gold_craft_oak
oak_dir = os.path.join(project_dir, "assets", "k003_gold_craft_oak")
if os.path.exists(oak_dir):
    for f in os.listdir(oak_dir):
        files_to_pack.append(os.path.join("assets", "k003_gold_craft_oak", f))

# Add assets/previews
prev_dir = os.path.join(project_dir, "assets", "previews")
if os.path.exists(prev_dir):
    for f in os.listdir(prev_dir):
        files_to_pack.append(os.path.join("assets", "previews", f))

print(f"Creating ZIP archive: {zip_out}")
t0 = time.time()
with zipfile.ZipFile(zip_out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=4, allowZip64=True) as z:
    for rel_p in files_to_pack:
        full_p = os.path.join(project_dir, rel_p)
        if os.path.exists(full_p):
            size_kb = os.path.getsize(full_p) / 1024
            print(f"  Adding: {rel_p} ({size_kb:,.1f} KB)")
            z.write(full_p, arcname=rel_p)
        else:
            print(f"  Warning: {rel_p} not found!")

t1 = time.time()
size_mb = os.path.getsize(zip_out) / (1024 * 1024)
print(f"\nArchive created successfully in {t1 - t0:.1f}s! Total Size: {size_mb:.2f} MB")
