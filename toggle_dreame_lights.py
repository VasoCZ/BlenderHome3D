"""
toggle_dreame_lights.py
Prepíná stav osvetlenia a svietiacich prvkov vysávaca Dreame L40 Ultra (kolekcia Dreame_Active_Lights).
1-klik prepnutie v Blender Outlineri alebo cez tento skript.
"""

import bpy

COLL_NAME = "Dreame_Active_Lights"
coll = bpy.data.collections.get(COLL_NAME)

if not coll:
    print(f"Kolekcia '{COLL_NAME}' nebola nájdená!")
else:
    # Prepnutie stavu
    new_state = not coll.hide_render
    coll.hide_render = new_state
    coll.hide_viewport = new_state
    
    state_str = "VYPNUTÉ (OFF / DORMANT)" if new_state else "ZAPNUTÉ (ON / RUNNING GLOW)"
    print("=" * 60)
    print(f"Dreame L40 Ultra svetlá sú teraz: {state_str}")
    print("=" * 60)
    
    # Prekreslenie viewportu
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
