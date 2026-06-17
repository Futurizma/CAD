"""
Industrial building 3D model based on the elevation drawing.
Grid: ~22 columns (axes E -> B), 2 floors, flat roof.
All dimensions in mm.
"""
from build123d import *

# --- Parameters ---
BAY_WIDTH    = 6000    # column spacing
NUM_BAYS     = 21      # 22 columns
DEPTH        = 12000   # building depth (Y axis)
FL_H         = 3600    # floor-to-floor height
NUM_FL       = 2
COL_W        = 400     # column section
SLAB_T       = 250     # slab thickness
WALL_T       = 300     # wall thickness
LENGTH       = BAY_WIDTH * NUM_BAYS   # total length X

# Window params
WIN_W  = 1200
WIN_H  = 1400
WIN_SILL = 900         # from floor finish to window bottom
WINS_PER_BAY = 3
WIN_GAP = 180

parts = []

# ── Foundation slab ──────────────────────────────────────────────────────────
parts.append(Box(LENGTH + COL_W, DEPTH + COL_W, 200,
                 align=(Align.CENTER, Align.CENTER, Align.MIN)))

# ── Columns ───────────────────────────────────────────────────────────────────
for col in range(NUM_BAYS + 1):
    x = -LENGTH / 2 + col * BAY_WIDTH
    for fl in range(NUM_FL):
        z = 200 + fl * FL_H
        col_box = Box(COL_W, DEPTH + COL_W, FL_H,
                      align=(Align.CENTER, Align.CENTER, Align.MIN))
        parts.append(col_box.moved(Location((x, 0, z))))

# ── Floor & roof slabs ────────────────────────────────────────────────────────
for fl in range(NUM_FL + 1):
    z = 200 + fl * FL_H
    slab = Box(LENGTH + COL_W, DEPTH + COL_W, SLAB_T,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(slab.moved(Location((0, 0, z))))

# ── Walls (front, back, sides) — per floor ───────────────────────────────────
front_y =  (DEPTH / 2 + COL_W / 2)
back_y  = -(DEPTH / 2 + COL_W / 2)
left_x  = -(LENGTH / 2 + COL_W / 2)
right_x =  (LENGTH / 2 + COL_W / 2)

for fl in range(NUM_FL):
    z     = 200 + SLAB_T + fl * FL_H
    wh    = FL_H - SLAB_T     # wall height between slabs

    # front wall
    fw = Box(LENGTH + COL_W, WALL_T, wh,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(fw.moved(Location((0, front_y - WALL_T / 2, z))))

    # back wall
    bw = Box(LENGTH + COL_W, WALL_T, wh,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(bw.moved(Location((0, back_y + WALL_T / 2, z))))

    # left wall
    lw = Box(WALL_T, DEPTH + COL_W, wh,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(lw.moved(Location((left_x + WALL_T / 2, 0, z))))

    # right wall
    rw = Box(WALL_T, DEPTH + COL_W, wh,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(rw.moved(Location((right_x - WALL_T / 2, 0, z))))

# ── Merge all solid parts ────────────────────────────────────────────────────
building = parts[0]
for p in parts[1:]:
    building = building + p

# ── Window cutouts (front wall only) ─────────────────────────────────────────
total_wins_w = WINS_PER_BAY * WIN_W + (WINS_PER_BAY - 1) * WIN_GAP

for fl in range(NUM_FL):
    z_sill = 200 + SLAB_T + fl * FL_H + WIN_SILL
    for bay in range(NUM_BAYS):
        bay_cx = -LENGTH / 2 + bay * BAY_WIDTH + BAY_WIDTH / 2
        for w in range(WINS_PER_BAY):
            wx = bay_cx - total_wins_w / 2 + w * (WIN_W + WIN_GAP) + WIN_W / 2
            win_cutter = Box(WIN_W, WALL_T + 40, WIN_H,
                             align=(Align.CENTER, Align.CENTER, Align.MIN))
            win_cutter = win_cutter.moved(Location((wx, front_y - WALL_T / 2 - 20, z_sill)))
            building = building - win_cutter

# ── Export ────────────────────────────────────────────────────────────────────
export_step(building, "/home/user/CAD/building.step")
export_stl(building, "/home/user/CAD/building.stl")
print("Done!")
bb = building.bounding_box()
print(f"Size: {bb.size.X/1000:.1f} x {bb.size.Y/1000:.1f} x {bb.size.Z/1000:.1f} m")
