import sys, math, numpy as np
from scipy import ndimage as ndi
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom_v3 import *

h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.07
X = np.arange(-14.5, 14.5 + h / 2, h, dtype=np.float32)
Z = np.arange(-0.5, Z_CARA + 0.5 + h / 2, h, dtype=np.float32)
x = X[:, None, None]; y = X[None, :, None]; z = Z[None, None, :]
r = np.sqrt(x * x + y * y); T59 = math.tan(math.radians(59))

def hexf(af):
    f = None
    for k in range(6):
        a = math.radians(30 + 60 * k); g_ = x * math.cos(a) + y * math.sin(a) - af / 2
        f = g_ if f is None else np.maximum(f, g_)
    return f

# cuerpo
ext = np.where(z < Z_UND1, R_UND1, np.where(z < Z_M24_FIN, R_M24, R_FRENTE))
cuerpo = ((z >= 0) & (z < Z_HEX) & (hexf(HEX_AF) <= 0)) | ((z >= Z_HEX) & (z <= Z_FRENTE) & (r <= ext))
rg, rp = D_G14 / 2, D_PASO / 2
z1 = L_G14; z2 = z1 + (rg - rp) / T59
rin = np.where(z < z1, rg, np.where(z < z2, rg - (z - z1) * T59, np.where(z < Z_PLEN0, rp,
       np.where(z < Z_SW0, D_PLEN / 2, np.where(z < Z_ROSCA_INT0, D_SW / 2, R_M18_INT)))))
cuerpo &= ~(r < rin)
# remolinador
sw = (z >= Z_SW0) & (z <= Z_ROSCA_INT0) & (r <= np.where(z < Z_SW0 + CH_SW, D_SW / 2 - CH_SW + (z - Z_SW0), D_SW / 2))
for po, pt in ranuras():
    sw &= ~((np.hypot(x - po[0], y - po[1]) <= D_HC / 2))
    ab = np.array(pt) - np.array(po)
    tt = np.clip(((x - po[0]) * ab[0] + (y - po[1]) * ab[1]) / (ab @ ab), 0, 1)
    d = np.hypot(x - po[0] - tt * ab[0], y - po[1] - tt * ab[1])
    sw &= ~((d <= B_SLOT / 2) & (z >= Z_ROSCA_INT0 - H_SLOT))
# punta
pin = np.where(z < Z_CAM1, D_S / 2, np.where(z < Z_CONO1, D_S / 2 - (z - Z_CAM1), D_O / 2))
pout = np.where(z < Z_FRENTE - 0.5, R_M18, np.where(z < Z_BRIDA0, R_UND_P, R_BRIDA))
planos = (np.abs(x) <= AF_BRIDA / 2) | (z < Z_BRIDA0)
punta = (z >= Z_PUNTA0) & (z <= Z_CARA) & (r <= pout) & (r >= pin) & planos
print("interferencias remolinador–cuerpo / –punta (vóxeles):", int((sw & cuerpo).sum()), int((sw & punta).sum()))
sol = cuerpo | sw | punta
cerr = sol | (z < 0.03) | (z > Z_CARA - 0.03) | ((r > R_FRENTE + 0.02) & (z > Z_HEX + 0.5) & (z < Z_FRENTE)) | ((r > R_BRIDA + 0.02) & (z >= Z_FRENTE)) | ((r > R_UND_P) & (z >= Z_FRENTE) & (z < Z_BRIDA0)) | ((hexf(HEX_AF) > 0) & (z <= Z_HEX + 0.5))
lab, n = ndi.label(~cerr)
L = lambda pz: lab[np.argmin(abs(X)), np.argmin(abs(X)), np.argmin(abs(Z - pz))]
print("entrada -> orificio conectados:", L(3.0) == L(Z_CARA - 0.3) != 0)
sw2 = (z >= Z_SW0) & (z <= Z_ROSCA_INT0) & (r <= D_SW / 2)
for po, pt in ranuras():
    sw2 &= ~((np.hypot(x - po[0], y - po[1]) <= D_HC / 2))
lab2, _ = ndi.label(~(cerr | cuerpo | punta | sw2))
L2 = lambda pz: lab2[np.argmin(abs(X)), np.argmin(abs(X)), np.argmin(abs(Z - pz))]
print("sin ranuras, ¿sigue conectado? (debe ser False):", L2(3.0) == L2(Z_CARA - 0.3))
del lab, lab2
for nm, s in (('cuerpo', cuerpo), ('remolinador', sw), ('punta', punta)):
    dt = ndi.distance_transform_edt(s).astype(np.float32) * h
    mx = ndi.maximum_filter(dt, size=3); eje = s & (dt == mx) & (dt > 1.5 * h)
    v = 2 * dt[eje]
    print(f"{nm:12s}: pared mínima ≈ {v.min():.2f} mm | percentil 1 % ≈ {np.percentile(v,1):.2f} mm")
    del dt, mx, eje
