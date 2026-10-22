"""
set_tv_power.py
----------------
Ovládání stavu televizí (1.04 Obývací pokoj, 1.05 Ložnice) v modelu dum_pudorys.blend.

Použití z příkazové řádky:
  blender dum_pudorys.blend -b -P set_tv_power.py -- --room 1.04 --state on
  blender dum_pudorys.blend -b -P set_tv_power.py -- --room all --state off

Nebo import v Pythonu:
  from set_tv_power import set_tv_power
  set_tv_power(room="1.04", state=True)
"""

import sys
import bpy

def set_tv_power(room="all", state=False):
    rooms = ["1.04", "1.05"] if room in ["all", "both"] else [room]
    
    config = {
        "1.04": {
            "glow": "TV_Screen_Glow_1.04",
            "light": "Light_1.04_Obyvaci_pokoj_TV",
            "default_energy": 55.0
        },
        "1.05": {
            "glow": "TV_Screen_Glow_1.05",
            "light": "Light_1.05_Loznice_TV",
            "default_energy": 45.0
        }
    }

    for r in rooms:
        if r not in config:
            print(f"Varování: Neznámá místnost pro TV: {r}")
            continue
            
        c = config[r]
        glow = bpy.data.objects.get(c["glow"])
        light = bpy.data.objects.get(c["light"])
        
        is_on = (state is True or str(state).lower() in ['on', 'true', '1'])
        
        if glow:
            glow.hide_render = not is_on
            glow.hide_viewport = not is_on
            
        if light:
            light.hide_render = not is_on
            light.hide_viewport = not is_on
            target_energy = light.get("active_energy", c["default_energy"]) if is_on else 0.0
            light.data.energy = target_energy
            
        status_str = "ZAPNUTA (ON)" if is_on else "VYPNUTA (OFF)"
        print(f">>> TV {r}: {status_str}")

if __name__ == '__main__':
    # Parse CLI arguments if run with Blender
    args = sys.argv
    target_room = "all"
    target_state = "off"
    
    if "--" in args:
        idx = args.index("--")
        cli_args = args[idx+1:]
        for i, a in enumerate(cli_args):
            if a in ["--room", "-r"] and i + 1 < len(cli_args):
                target_room = cli_args[i+1]
            elif a in ["--state", "-s"] and i + 1 < len(cli_args):
                target_state = cli_args[i+1]

    set_tv_power(room=target_room, state=target_state)
    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend uloženo se zadaným stavem TV.")
