"""Render the building STL to PNG images from multiple angles."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import struct

def load_stl(path):
    with open(path, "rb") as f:
        head = f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        tris = np.zeros((n, 3, 3), dtype=np.float32)
        for i in range(n):
            f.read(12)  # normal
            for v in range(3):
                tris[i, v] = struct.unpack("<3f", f.read(12))
            f.read(2)   # attr
    return tris

tris = load_stl("/home/user/CAD/building.stl")
print(f"Triangles: {len(tris)}")

# Center & scale to meters
tris_m = tris / 1000.0
center = tris_m.reshape(-1, 3).mean(axis=0)
tris_c = tris_m - center

views = [
    ("perspective", 25, -60),
    ("front",        5, -90),
    ("corner",      30, -45),
]

fig = plt.figure(figsize=(20, 12))
for idx, (name, elev, azim) in enumerate(views, 1):
    ax = fig.add_subplot(3, 1, idx, projection="3d")
    coll = Poly3DCollection(tris_c, facecolor="#9fb4c7",
                            edgecolor="#33414f", linewidths=0.05, alpha=1.0)
    ax.add_collection3d(coll)

    allpts = tris_c.reshape(-1, 3)
    xr = allpts[:, 0].min(), allpts[:, 0].max()
    yr = allpts[:, 1].min(), allpts[:, 1].max()
    zr = allpts[:, 2].min(), allpts[:, 2].max()
    ax.set_xlim(xr); ax.set_ylim(yr); ax.set_zlim(zr)
    ax.set_box_aspect((xr[1]-xr[0], yr[1]-yr[0], zr[1]-zr[0]))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(f"{name}  (elev={elev}, azim={azim})", color="#222")
    ax.set_axis_off()

plt.tight_layout()
plt.savefig("/home/user/CAD/building_render.png", dpi=110,
            bbox_inches="tight", facecolor="white")
print("Saved building_render.png")
