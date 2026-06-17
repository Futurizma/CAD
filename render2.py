"""Detailed renders: facade close-up + transparent structural view."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import struct

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
center = tris.reshape(-1, 3).mean(axis=0)
tris -= center
allpts = tris.reshape(-1, 3)

# ---- View 1: zoom on left portion of facade to see windows ----
fig = plt.figure(figsize=(18, 7))
ax = fig.add_subplot(1, 1, 1, projection="3d")
ax.add_collection3d(Poly3DCollection(tris, facecolor="#aebfce",
                    edgecolor="#2e3b47", linewidths=0.15))
# Zoom to leftmost ~35 m
xmin = allpts[:, 0].min()
ax.set_xlim(xmin, xmin + 38)
ax.set_ylim(allpts[:, 1].min(), allpts[:, 1].max())
ax.set_zlim(allpts[:, 2].min(), allpts[:, 2].max())
ax.set_box_aspect((38, 12, 7.7))
ax.view_init(elev=12, azim=-78)
ax.set_axis_off()
ax.set_title("Фасад крупным планом — видны оконные проёмы и колонны", color="#222", fontsize=13)
plt.tight_layout()
plt.savefig("/home/user/CAD/facade_closeup.png", dpi=120, bbox_inches="tight", facecolor="white")
print("Saved facade_closeup.png")

# ---- View 2: transparent overview to reveal internal columns ----
fig = plt.figure(figsize=(20, 7))
ax = fig.add_subplot(1, 1, 1, projection="3d")
ax.add_collection3d(Poly3DCollection(tris, facecolor="#7fa8d0",
                    edgecolor="#274260", linewidths=0.1, alpha=0.18))
ax.set_xlim(allpts[:, 0].min(), allpts[:, 0].max())
ax.set_ylim(allpts[:, 1].min(), allpts[:, 1].max())
ax.set_zlim(allpts[:, 2].min(), allpts[:, 2].max())
ax.set_box_aspect((126, 12, 7.7))
ax.view_init(elev=22, azim=-55)
ax.set_axis_off()
ax.set_title("Полный объём здания (полупрозрачный) — каркас из 22 колонн × 2 этажа", color="#222", fontsize=13)
plt.tight_layout()
plt.savefig("/home/user/CAD/overview_transparent.png", dpi=110, bbox_inches="tight", facecolor="white")
print("Saved overview_transparent.png")
