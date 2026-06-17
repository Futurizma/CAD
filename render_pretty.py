"""
Cinematic rotating GIF: building + grass + trees + sky gradient + shadows.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import struct, imageio.v2 as imageio, io

# ── Load STL ─────────────────────────────────────────────────────────────────
def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        tris = np.zeros((n, 3, 3), dtype=np.float32)
        for i in range(n):
            f.read(12)
            for v in range(3):
                tris[i, v] = struct.unpack("<3f", f.read(12))
            f.read(2)
    return tris

tris = load_stl("/home/user/CAD/building.stl") / 1000.0
tris -= tris.reshape(-1, 3).mean(axis=0)
pts  = tris.reshape(-1, 3)
xr = (pts[:,0].min(), pts[:,0].max())
yr = (pts[:,1].min(), pts[:,1].max())
zr = (pts[:,2].min(), pts[:,2].max())

BX = xr[1] - xr[0]   # 126 m
BY = yr[1] - yr[0]    # 12 m
BZ = zr[1] - zr[0]    # 7.7 m
GROUND = zr[0]

rng = np.random.default_rng(42)

# ── Helper: cylinder (tree trunk) ────────────────────────────────────────────
def cylinder_tris(cx, cy, z0, z1, r, n=8):
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    tops, bots = [], []
    for i in range(n):
        a0, a1 = angles[i], angles[(i+1) % n]
        p = [[cx + r*np.cos(a0), cy + r*np.sin(a0), z0],
             [cx + r*np.cos(a1), cy + r*np.sin(a1), z0],
             [cx + r*np.cos(a1), cy + r*np.sin(a1), z1]]
        q = [[cx + r*np.cos(a0), cy + r*np.sin(a0), z0],
             [cx + r*np.cos(a1), cy + r*np.sin(a1), z1],
             [cx + r*np.cos(a0), cy + r*np.sin(a0), z1]]
        tops.append(p); tops.append(q)
    return tops

# ── Helper: sphere-ish cone (tree crown) ─────────────────────────────────────
def cone_tris(cx, cy, zb, zt, r, n=10):
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    result = []
    for i in range(n):
        a0, a1 = angles[i], angles[(i+1) % n]
        result.append([[cx, cy, zt],
                       [cx + r*np.cos(a0), cy + r*np.sin(a0), zb],
                       [cx + r*np.cos(a1), cy + r*np.sin(a1), zb]])
    return result

# ── Helper: ground quad ───────────────────────────────────────────────────────
def ground_quad(x0, x1, y0, y1, z):
    return [[[x0,y0,z],[x1,y0,z],[x1,y1,z]],
            [[x0,y0,z],[x1,y1,z],[x0,y1,z]]]

# ── Scene geometry ────────────────────────────────────────────────────────────
PAD = 20   # grass padding around building

# Ground plane (grass)
grass = ground_quad(xr[0]-PAD, xr[1]+PAD, yr[0]-PAD, yr[1]+PAD, GROUND)

# Road / pavement strip in front of building
road = ground_quad(xr[0]-2, xr[1]+2, yr[0]-PAD, yr[0]-2, GROUND+0.01)

# Parking lot markings (flat quads)
parking = []
for i in range(14):
    px = xr[0] + 4 + i * 9
    parking += ground_quad(px, px+6, yr[0]-18, yr[0]-4, GROUND+0.02)

# Trees — front row along facade
tree_trunks_geo, tree_crowns_geo, tree_shadows = [], [], []
tree_positions = []
for i in range(12):
    tx = xr[0] + 5 + i * 10.5
    ty = yr[0] - 5
    tree_positions.append((tx, ty))

# Trees — back row
for i in range(8):
    tx = xr[0] + 8 + i * 15
    ty = yr[1] + 6
    tree_positions.append((tx, ty))

# Corner accent trees
for tx, ty in [(xr[0]-8, yr[0]-8),(xr[1]+8, yr[0]-8),(xr[0]-8, yr[1]+8),(xr[1]+8, yr[1]+8)]:
    tree_positions.append((tx, ty))

for tx, ty in tree_positions:
    h  = rng.uniform(5, 8)
    r  = rng.uniform(2.5, 3.8)
    tree_trunks_geo += cylinder_tris(tx, ty, GROUND, GROUND+h*0.45, 0.3)
    tree_crowns_geo += cone_tris(tx, ty, GROUND+h*0.3, GROUND+h, r)
    # Shadow ellipse (fake, flat)
    for a in np.linspace(0, 2*np.pi, 12, endpoint=False):
        a2 = a + 2*np.pi/12
        tree_shadows.append([[tx, ty, GROUND+0.005],
                             [tx+r*0.8*np.cos(a),  ty+r*0.4*np.sin(a),  GROUND+0.005],
                             [tx+r*0.8*np.cos(a2), ty+r*0.4*np.sin(a2), GROUND+0.005]])

# Building shadow (offset to the right-back)
bshadow_dx, bshadow_dy = 3, -3
bshadow = [
    [[xr[0]+bshadow_dx, yr[0]+bshadow_dy, GROUND+0.003],
     [xr[1]+bshadow_dx, yr[0]+bshadow_dy, GROUND+0.003],
     [xr[1]+bshadow_dx, yr[1]+bshadow_dy, GROUND+0.003]],
    [[xr[0]+bshadow_dx, yr[0]+bshadow_dy, GROUND+0.003],
     [xr[1]+bshadow_dx, yr[1]+bshadow_dy, GROUND+0.003],
     [xr[0]+bshadow_dx, yr[1]+bshadow_dy, GROUND+0.003]],
]

# ── Render frames ─────────────────────────────────────────────────────────────
AZIMS = list(range(-30, 330, 10))   # 36 frames, full rotation
frames = []

for az in AZIMS:
    fig = plt.figure(figsize=(14, 7), facecolor="#d0e8f7")
    ax  = fig.add_subplot(111, projection="3d", facecolor="#d0e8f7")

    # Sky gradient via background rectangle (hack: colored figure bg)
    fig.patch.set_facecolor("#c8dff0")

    # Ground — grass
    ax.add_collection3d(Poly3DCollection(grass,      facecolor="#5a9e5a", edgecolor="none", alpha=1.0, zorder=0))
    # Road
    ax.add_collection3d(Poly3DCollection(road,       facecolor="#8a8a8a", edgecolor="none", alpha=1.0, zorder=1))
    # Parking
    ax.add_collection3d(Poly3DCollection(parking,    facecolor="#a0a0a0", edgecolor="#ffffff", linewidths=0.3, alpha=1.0, zorder=1))
    # Building shadow
    ax.add_collection3d(Poly3DCollection(bshadow,    facecolor="#2a4a2a", edgecolor="none", alpha=0.18, zorder=2))
    # Tree shadows
    ax.add_collection3d(Poly3DCollection(tree_shadows, facecolor="#2a4a2a", edgecolor="none", alpha=0.22, zorder=3))
    # Tree trunks
    ax.add_collection3d(Poly3DCollection(tree_trunks_geo, facecolor="#6b4c2a", edgecolor="#3d2a10", linewidths=0.1, zorder=4))
    # Tree crowns
    ax.add_collection3d(Poly3DCollection(tree_crowns_geo, facecolor="#2d7a2d", edgecolor="#1a4d1a", linewidths=0.1, alpha=0.92, zorder=5))
    # Building
    ax.add_collection3d(Poly3DCollection(tris,       facecolor="#d6dfe8", edgecolor="#4a5a6a", linewidths=0.12, alpha=1.0, zorder=6))

    # Axis limits with scene padding
    margin = 5
    ax.set_xlim(xr[0]-PAD-margin, xr[1]+PAD+margin)
    ax.set_ylim(yr[0]-PAD-margin, yr[1]+PAD+margin)
    ax.set_zlim(GROUND - 0.5, GROUND + BZ + 12)
    ax.set_box_aspect((BX + 2*PAD, BY + 2*PAD, BZ + 14))

    ax.view_init(elev=32, azim=az)
    ax.set_axis_off()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=90, bbox_inches="tight", facecolor="#c8dff0")
    plt.close(fig)
    buf.seek(0)
    frames.append(imageio.imread(buf))
    print(f"az={az:4d}  frame {len(frames)}/{len(AZIMS)}")

imageio.mimsave("/home/user/CAD/building_pretty.gif", frames, duration=0.1, loop=0)
print("Saved building_pretty.gif")
