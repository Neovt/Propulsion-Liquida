import sys, math, numpy as np
from scipy import ndimage as ndi
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom_v4 import *

h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.07
X = np.arange(-18, 18 + h / 2, h, dtype=np.float32)
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
t12 = math.tan(math.radians(ANG_CONO))
ext = np.where(z < Z_ROSCA12_FIN, R_M12, np.where(z < Z_HEX0, R_UND0, 0))
cuerpo = ((z >= 0) & (z < Z_HEX0) & (r <= ext)) | ((z >= Z_HEX0) & (z < Z_HEX1) & (hexf(HEX_AF) <= 0))
ext2 = np.where(z < Z_UND1, R_UND1, np.where(z < Z_M24_FIN, R_M24, R_FRENTE))
cuerpo |= (z >= Z_HEX1) & (z <= Z_FRENTE) & (r <= ext2)
zc_fin = (D_CONO_ENT - D_TUBO) / 2 / t12
zp0 = Z_SW0 - P_PLEN
rin = np.where(z < zc_fin, D_CONO_ENT / 2 - z * t12, np.where(z < Z_TOPE, D_TUBO / 2, np.where(z < zp0 - (D_PLEN/2 - D_PASO/2), D_PASO / 2,
       np.where(z < zp0, D_PASO / 2 + (z - (zp0 - (D_PLEN/2 - D_PASO/2))), np.where(z < Z_SW0, D_PLEN / 2,
       np.where(z < Z_RI0, D_SW / 2, R_M18_INT))))))
cuerpo &= ~(r < rin)
junta = (z >= Z_SW0) & (z < Z_SW_A) & (r >= D_PLEN / 2 + 0.1) & (r <= D_SW / 2 - 0.05)
# remolinador
sw = (z >= Z_SW_A) & (z <= Z_RI0) & (r <= np.where(z < Z_SW_A + CH_SW, D_SW / 2 - CH_SW + (z - Z_SW_A), D_SW / 2))
for po, pt in ranuras():
    sw &= ~((np.hypot(x - po[0], y - po[1]) <= D_HC / 2))
    ab = np.array(pt) - np.array(po)
    tt = np.clip(((x - po[0]) * ab[0] + (y - po[1]) * ab[1]) / (ab @ ab), 0, 1)
    d = np.hypot(x - po[0] - tt * ab[0], y - po[1] - tt * ab[1])
    sw &= ~((d <= B_SLOT / 2) & (z >= Z_RI0 - H_SLOT))
# punta
pin = np.where(z < Z_CAM1, D_S / 2, np.where(z < Z_CONO1, D_S / 2 - (z - Z_CAM1), D_O / 2))
pout = np.where(z < Z_BRIDA0, R_M18, R_BRIDA)
planos = (np.abs(x) <= AF_BRIDA / 2) | (z < Z_BRIDA0)
punta = (z >= Z_RI0) & (z <= Z_CARA) & (r <= pout) & (r >= pin) & planos
arand = (z >= Z_FRENTE) & (z < Z_BRIDA0) & (r >= AR_P_I/2) & (r <= AR_P_E/2)
print("interferencias remolinador–cuerpo / –punta / junta–remolinador (vóxeles):", int((sw & cuerpo).sum()), int((sw & punta).sum()), int((junta & sw).sum()))
sol = cuerpo | sw | punta | junta | arand
cerr = sol | (z < 0.03) | (z > Z_CARA - 0.03) | ((r > R_M12) & (z < Z_HEX0)) | ((hexf(HEX_AF) > 0) & (z >= Z_HEX0) & (z < Z_HEX1)) | ((r > R_M24) & (z >= Z_HEX1)) | ((r > R_BRIDA + 0.02) & (z >= Z_FRENTE))
lab, n = ndi.label(~cerr)
L = lambda pz: lab[np.argmin(abs(X)), np.argmin(abs(X)), np.argmin(abs(Z - pz))]
print("entrada -> orificio conectados:", L(3.0) == L(Z_CARA - 0.3) != 0)
sw2 = (z >= Z_SW_A) & (z <= Z_RI0) & (r <= D_SW / 2)
for po, pt in ranuras():
    sw2 &= ~((np.hypot(x - po[0], y - po[1]) <= D_HC / 2))
lab2, _ = ndi.label(~(cerr | cuerpo | punta | sw2 | junta | arand))
L2 = lambda pz: lab2[np.argmin(abs(X)), np.argmin(abs(X)), np.argmin(abs(Z - pz))]
print("sin ranuras, ¿sigue conectado? (debe ser False):", L2(3.0) == L2(Z_CARA - 0.3))
del lab, lab2
for nm, s in (('cuerpo', cuerpo), ('remolinador', sw), ('punta', punta)):  # noqa
    dt = ndi.distance_transform_edt(s).astype(np.float32) * h
    mx = ndi.maximum_filter(dt, size=3); eje = s & (dt == mx) & (dt > 1.5 * h)
    v = 2 * dt[eje]
    print(f"{nm:12s}: pared mínima ≈ {v.min():.2f} mm | percentil 1 % ≈ {np.percentile(v,1):.2f} mm")
    del dt, mx, eje
