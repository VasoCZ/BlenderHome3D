import zipfile
import os
import time

project_dir = r"C:\Users\Vaso\Antigravity\Project blender"
zip_out = os.path.join(project_dir, "dum_pudorys_alfa.zip")

files_to_pack = [
    "dum_pudorys.blend",
    "dum_pudorys_overview.png",
    "dum_pudorys_daylight_final.png",
    "dum_pudorys_night_overview.png",
    "dum_pudorys_night_dark.png",
    "render_exact_user_modes.py",
    "apply_terrace_fix.py",
    "inspect_terrace_paving.py",
    "GEMINI.md",
    "BUILD_SPECIFICATION_1TO1.md",
    os.path.join("assets", "license_plate_1AH_U743.png"),
    os.path.join("assets", "K003_PW_Gold_Craft_Oak.jpg"),
    os.path.join("scratch", "build_final_scala.py")
]

# Also include assets/skoda_official
skoda_dir = os.path.join(project_dir, "assets", "skoda_official")
if os.path.exists(skoda_dir):
    for f in os.listdir(skoda_dir):
        files_to_pack.append(os.path.join("assets", "skoda_official", f))

print(f"Creating ZIP archive: {zip_out}")
t0 = time.time()
with zipfile.ZipFile(zip_out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=4, allowZip64=True) as z:
    for rel_p in files_to_pack:
        full_p = os.path.join(project_dir, rel_p)
        if os.path.exists(full_p):
            print(f"  Adding: {rel_p} ({os.path.getsize(full_p):,} bytes)")
            z.write(full_p, arcname=rel_p)
        else:
            print(f"  Warning: {rel_p} not found!")

t1 = time.time()
size_mb = os.path.getsize(zip_out) / (1024 * 1024)
print(f"Archive created successfully in {t1 - t0:.1f}s! Size: {size_mb:.1f} MB ({zip_out})")
