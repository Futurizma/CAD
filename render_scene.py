"""
Architectural scene: building + grass + trees + parking lot WITH CARS + lamps.
All faces go into ONE Poly3DCollection so matplotlib depth-sorts correctly.
"""
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
        t = np.zeros((n,3,3), dtype=np.float32)
        for i in range(n):
            f.read(12)
            for v in range(3):
                t[i,v]=struct.unpack("<3f", f.read(12))
            f.read(2)
    return t

tris = load_stl("/home/user/CAD/building.stl")/1000.0
tris -= tris.reshape(-1,3).mean(axis=0)
pts = tris.reshape(-1,3)
xr=(pts[:,0].min(),pts[:,0].max()); yr=(pts[:,1].min(),pts[:,1].max()); zr=(pts[:,2].min(),pts[:,2].max())
BX,BY,BZ=xr[1]-xr[0],yr[1]-yr[0],zr[1]-zr[0]; G=zr[0]
rng=np.random.default_rng(7)

# Global accumulators: faces + matching colors
FACES=[]; COLORS=[]
def add(face_list, color):
    for f in face_list:
        FACES.append(f); COLORS.append(color)

def box(cx,cy,z0,sx,sy,sz):
    x0,x1=cx-sx/2,cx+sx/2; y0,y1=cy-sy/2,cy+sy/2; z1=z0+sz
    v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
    fc=[(0,1,2),(0,2,3),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(2,3,7),(2,7,6),(1,2,6),(1,6,5),(0,3,7),(0,7,4)]
    return [[v[a],v[b],v[c]] for a,b,c in fc]

def cyl(cx,cy,z0,z1,r,n=10):
    a=np.linspace(0,2*np.pi,n,endpoint=False); o=[]
    for i in range(n):
        a0,a1=a[i],a[(i+1)%n]
        o.append([[cx+r*np.cos(a0),cy+r*np.sin(a0),z0],[cx+r*np.cos(a1),cy+r*np.sin(a1),z0],[cx+r*np.cos(a1),cy+r*np.sin(a1),z1]])
        o.append([[cx+r*np.cos(a0),cy+r*np.sin(a0),z0],[cx+r*np.cos(a1),cy+r*np.sin(a1),z1],[cx+r*np.cos(a0),cy+r*np.sin(a0),z1]])
    return o

def sph(cx,cy,cz,r,n=7):
    o=[]
    for i in range(n):
        t0=np.pi*i/n; t1=np.pi*(i+1)/n
        for j in range(n):
            p0=2*np.pi*j/n; p1=2*np.pi*(j+1)/n
            P=lambda t,p:[cx+r*np.sin(t)*np.cos(p),cy+r*np.sin(t)*np.sin(p),cz+r*np.cos(t)]
            o.append([P(t0,p0),P(t1,p0),P(t1,p1)]); o.append([P(t0,p0),P(t1,p1),P(t0,p1)])
    return o

def tile(x0,x1,y0,y1,z):
    return [[[x0,y0,z],[x1,y0,z],[x1,y1,z]],[[x0,y0,z],[x1,y1,z],[x0,y1,z]]]

PAD=22
# Grass subdivided into tiles (so depth-sort works)
gx0,gx1,gy0,gy1=xr[0]-PAD,xr[1]+PAD,yr[0]-PAD,yr[1]+PAD
NX,NY=40,12
for i in range(NX):
    for j in range(NY):
        x0=gx0+(gx1-gx0)*i/NX; x1=gx0+(gx1-gx0)*(i+1)/NX
        y0=gy0+(gy1-gy0)*j/NY; y1=gy0+(gy1-gy0)*(j+1)/NY
        shade="#67ad47" if (i+j)%2==0 else "#5fa341"
        add(tile(x0,x1,y0,y1,G), shade)

# Parking apron + road (tiled)
py0,py1=yr[0]-19,yr[0]-3
for i in range(NX):
    x0=xr[0]+(BX)*i/NX; x1=xr[0]+(BX)*(i+1)/NX
    add(tile(x0,x1,py0,py1,G+0.01), "#9aa4ab")
for i in range(NX):
    x0=gx0+(gx1-gx0)*i/NX; x1=gx0+(gx1-gx0)*(i+1)/NX
    add(tile(x0,x1,gy0,py0-1,G+0.006), "#5d6d7e")

# Stall lines
ns=24
for i in range(ns+1):
    sx=xr[0]+2+i*(BX-4)/ns
    add(tile(sx-0.08,sx+0.08,py0,py1,G+0.02), "#f5f5f5")

# Cars
pal=["#c0392b","#2980b9","#239b56","#e67e22","#7f8c8d","#ecf0f1","#34495e","#8e44ad"]
for i in range(ns):
    if rng.random()<0.32: continue
    cx=xr[0]+2+(i+0.5)*(BX-4)/ns; cy=(py0+py1)/2+rng.uniform(-0.5,0.5)
    col=pal[rng.integers(0,len(pal))]
    add(tile(cx-1.2,cx+1.2,cy-2.6,cy+2.6,G+0.015), "#1a1a1a")   # shadow
    add(box(cx,cy,G+0.05,1.9,4.6,0.8), col)                      # body
    add(box(cx,cy-0.1,G+0.85,1.6,2.6,0.6), "#aed6f1")            # cabin

# Trees
pos=[]
for i in range(13): pos.append((xr[0]+3+i*10, yr[1]+7))
for c in [(xr[0]-9,yr[0]-9),(xr[1]+9,yr[0]-9),(xr[0]-9,yr[1]+9),(xr[1]+9,yr[1]+9)]: pos.append(c)
for i in range(6): pos.append((xr[0]+10+i*22, gy0+3))
for tx,ty in pos:
    h=rng.uniform(6,9); r=rng.uniform(2.6,3.8)
    add(tile(tx-r,tx+r,ty-r*0.5,ty+r*0.5,G+0.006), "#3a5a30")  # shadow
    add(cyl(tx,ty,G,G+h*0.4,0.32), "#6b4423")
    add(sph(tx,ty,G+h*0.7,r,7), "#2b9b4e")

# Lamps
for i in range(7):
    lx=xr[0]+5+i*(BX-10)/6; ly=py0-2
    add(cyl(lx,ly,G,G+6,0.12,6), "#566573")
    add(sph(lx,ly,G+6.2,0.5,6), "#fdeaa8")

# Building shadow + building
add(tile(xr[0]+4,xr[1]+4,yr[0]-4,yr[1]-4,G+0.004), "#3a5030")
for f in tris:
    FACES.append(f); COLORS.append("#e1e8ee")

FACES=np.array(FACES); COLORS=np.array(COLORS, dtype=object)
print(f"Total faces: {len(FACES)}")

def render(az, elev, size, dpi):
    fig=plt.figure(figsize=size, facecolor="#bcdcf0")
    ax=fig.add_subplot(111, projection="3d", facecolor="#bcdcf0")
    coll=Poly3DCollection(FACES, facecolors=list(COLORS), edgecolors="none", linewidths=0)
    # subtle edges only for building handled by color contrast
    ax.add_collection3d(coll)
    ax.set_xlim(gx0,gx1); ax.set_ylim(gy0,gy1); ax.set_zlim(G-0.5,G+BZ+12)
    ax.set_box_aspect((gx1-gx0, gy1-gy0, BZ+14))
    ax.view_init(elev=elev, azim=az); ax.set_axis_off()
    buf=io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="#bcdcf0")
    plt.close(fig); buf.seek(0)
    return imageio.imread(buf)

# Hero
img=render(-55,26,(16,8),130)
imageio.imwrite("/home/user/CAD/scene_hero.png", img)
print("Saved scene_hero.png")

# GIF
frames=[render(az,30,(13,6.5),85) for az in range(-40,320,12)]
imageio.mimsave("/home/user/CAD/scene_rotate.gif", frames, duration=0.11, loop=0)
print("Saved scene_rotate.gif")
