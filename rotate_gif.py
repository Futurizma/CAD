"""Create a rotating GIF of the building model."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import struct, imageio.v2 as imageio, io

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
pts = tris.reshape(-1, 3)
xr = (pts[:,0].min(), pts[:,0].max())
yr = (pts[:,1].min(), pts[:,1].max())
zr = (pts[:,2].min(), pts[:,2].max())

frames = []
angles = range(0, 360, 12)   # 30 frames
for az in angles:
    fig = plt.figure(figsize=(11, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolor="#8fb0d4",
                        edgecolor="#26405e", linewidths=0.08, alpha=0.55))
    ax.set_xlim(xr); ax.set_ylim(yr); ax.set_zlim(zr)
    ax.set_box_aspect((xr[1]-xr[0], yr[1]-yr[0], zr[1]-zr[0]))
    ax.view_init(elev=22, azim=az)
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=85, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    frames.append(imageio.imread(buf))
    print(f"frame az={az}")

imageio.mimsave("/home/user/CAD/building_rotate.gif", frames, duration=0.12, loop=0)
print("Saved building_rotate.gif")
