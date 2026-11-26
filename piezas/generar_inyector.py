"""
Inyector de prueba imprimible (PETG/PLA) para la salida de la solenoide JT22-02
===============================================================================
Se enrosca (R1/4 BSPT macho + teflón) en la salida 1/4" BSPP hembra de la válvula.
Descarga recta, en el eje. Dos tipos:

  swirl     inyector de remolino: 4 canales -> 4 puertos tangenciales -> cámara de remolino
            -> cono 45° -> orificio de salida. Con líquido forma un cono hueco; con aire
            da un chorro ancho y turbulento.
  orificio  orificio recto calibrado (referencia para medir el Cd del montaje).

El sólido se define como campo de distancia (SDF) y se triangula con marching cubes
(scikit-image). Roscas y hexágono reutilizan generar_piezas.py (misma rosca que P1/P2).

Uso:   python3 generar_inyector.py [carpeta_salida] [--h 0.12] [--d 1.5 2.0 2.5 3.0] [--ref 2.0]
Todas las cotas en mm. Eje z hacia arriba; la punta de la rosca queda en z = 0
(orientación de impresión: rosca sobre la cama, salida hacia arriba).
"""
import os, sys, struct, argparse
import numpy as np
from scipy.optimize import brentq
from skimage import measure

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_piezas as gp

# ---------------------------------------------------------------- PARAMETROS
BORE_R   = 2.25      # radio del agujero de entrada (Ø4,5)
THR_LEN  = 10.0      # largo de rosca R1/4
Z_HEX0   = 11.5      # base del hexágono
HEX_AF   = 17.0      # llave de 17 mm

N_PORT   = 4         # puertos tangenciales
A_GEO    = 1.7       # constante geométrica del remolino  A = R_in*r_o/(n*r_p^2)
R_CHAM   = 3.0       # radio de la cámara de remolino (Ø6)
SPOKE_R  = 1.2       # radio de los canales de reparto y ascendentes (Ø2,4)
RISER_POS = 5.6      # radio al que suben los canales
Z_SPOKE  = 15.4      # altura de los canales radiales de reparto
Z_PORT   = 20.6      # altura de los puertos tangenciales
Z_CH0    = 19.2      # piso de la cámara
CH_ABOVE = 3.0       # cámara cilíndrica sobre el eje de los puertos
# ---------------------------------------------------------------------------


def r_orificio_largo(d_o):
    return max(0.8, 0.5 * d_o)


def swirl_geom(d_o, n=N_PORT, A=A_GEO, R_s=R_CHAM):
    """Radio de los puertos y brazo de remolino para una constante A dada."""
    r_o = d_o / 2
    a = n * A
    r_p = (-r_o + np.sqrt(r_o**2 + 4 * a * R_s * r_o)) / (2 * a)
    return r_p, R_s - r_p


def swirl_teoria(R_in, r_o, r_p, n=N_PORT):
    """Teoría de Abramovich / Bazarov para inyector de remolino con líquido."""
    A = R_in * r_o / (n * r_p**2)
    phi = brentq(lambda p: (1 - p) * np.sqrt(2) / (p * np.sqrt(p)) - A, 1e-3, 0.999)
    mu = phi * np.sqrt(phi / (2 - phi))
    tan_a = 2 * mu * A / np.sqrt((1 + np.sqrt(1 - phi))**2 - 4 * mu**2 * A**2)
    return dict(A=A, phi=phi, mu=mu, semiangulo=np.degrees(np.arctan(tan_a)))


def segmento(x, y, z, a, b, rad):
    """Distancia con signo a una cápsula (segmento a-b, radio rad)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    ab = b - a
    t = ((x - a[0]) * ab[0] + (y - a[1]) * ab[1] + (z - a[2]) * ab[2]) / (ab @ ab)
    t = np.clip(t, 0, 1)
    dx = x - (a[0] + t * ab[0]); dy = y - (a[1] + t * ab[1]); dz = z - (a[2] + t * ab[2])
    return np.sqrt(dx * dx + dy * dy + dz * dz) - rad


def construir(d_o, tipo="swirl", h=0.12):
    r_o = d_o / 2
    l_o = r_orificio_largo(d_o)
    z_c1 = Z_PORT + CH_ABOVE
    z_cone_end = z_c1 + (R_CHAM - r_o)
    z_top = z_cone_end + l_o

    ex = 10.3
    X = np.arange(-ex, ex + h / 2, h, dtype=np.float32)
    Z = np.arange(-0.6, z_top + 0.6 + h / 2, h, dtype=np.float32)
    x = X[:, None, None]; y = X[None, :, None]; z = Z[None, None, :]
    r = np.sqrt(x * x + y * y)

    # ---- sólido: rosca + garganta + hexágono
    th = np.arctan2(y, x)
    u = z - gp.R14_P * th / (2 * np.pi)
    cr = gp.r14_cresta(0.0, +1)
    r_t = (cr(z) - gp.perf_h_max(gp.R14_PERF, gp.R14_P)) + gp.R14_PERF(u)
    r_tip = cr(0.0) - gp.R14_H - 0.3 + z                      # chaflán de entrada 45°
    f_slab = np.maximum(r - np.minimum(r_t, r_tip), np.maximum(-z, z - THR_LEN))
    r_u = cr(THR_LEN) - gp.R14_H - 0.15
    f_u = np.maximum(r - r_u, np.maximum(THR_LEN - 0.1 - z, z - (Z_HEX0 + 0.1)))

    a = HEX_AF / 2
    f_hex = None
    for k in range(6):
        ang = np.radians(30 + 60 * k)
        fk = x * np.cos(ang) + y * np.sin(ang) - a
        f_hex = fk if f_hex is None else np.maximum(f_hex, fk)
    f_hex = np.maximum(f_hex, np.maximum(Z_HEX0 - z, z - z_top))
    f_hex = np.maximum(f_hex, (r - r_u - (z - Z_HEX0)) / np.sqrt(2))   # cono inferior 45°
    f_hex = np.maximum(f_hex, (r - a - (z_top - z)) / np.sqrt(2))      # chaflán superior
    f_solid = np.minimum(np.minimum(f_slab, f_u), f_hex)

    # ---- cavidades
    cav = []
    if tipo == "swirl":
        zb1 = Z_SPOKE - 1.2                                    # fin del tramo cilíndrico de entrada
        rl = np.where(z <= zb1, BORE_R, BORE_R - (z - zb1))
        cav.append(np.where(z <= zb1, r - BORE_R, (r - rl) / np.sqrt(2)))

        r_p, R_in = swirl_geom(d_o)
        L = np.sqrt(RISER_POS**2 - R_in**2)
        for k in range(N_PORT):
            phi = 2 * np.pi * k / N_PORT
            n_ = np.array([np.cos(phi), np.sin(phi)])
            t_ = np.array([-np.sin(phi), np.cos(phi)])
            p_start = R_in * n_ - L * t_
            p_end = R_in * n_
            cav.append(segmento(x, y, z, (0, 0, Z_SPOKE), (p_start[0], p_start[1], Z_SPOKE), SPOKE_R))
            cav.append(segmento(x, y, z, (p_start[0], p_start[1], Z_SPOKE),
                                (p_start[0], p_start[1], Z_PORT), SPOKE_R))
            cav.append(segmento(x, y, z, (p_start[0], p_start[1], Z_PORT),
                                (p_end[0], p_end[1], Z_PORT), r_p))
        rl_c = np.where(z < z_c1, R_CHAM, np.where(z < z_cone_end, R_CHAM - (z - z_c1), r_o))
        esc = np.where((z >= z_c1) & (z < z_cone_end), np.sqrt(2), 1.0)
        cav.append(np.maximum((r - rl_c) / esc, Z_CH0 - z))
    else:   # orificio recto de referencia
        zb1 = z_top - l_o - (BORE_R - r_o)
        rl = np.where(z <= zb1, BORE_R, np.where(z < zb1 + (BORE_R - r_o), BORE_R - (z - zb1), r_o))
        esc = np.where((z > zb1) & (z < zb1 + (BORE_R - r_o)), np.sqrt(2), 1.0)
        cav.append((r - rl) / esc)

    f_cav = cav[0]
    for c in cav[1:]:
        f_cav = np.minimum(f_cav, c)
    f = np.maximum(f_solid, -f_cav).astype(np.float32)

    verts, faces, _, _ = measure.marching_cubes(f, level=0.0, spacing=(h, h, h))
    verts = verts + np.array([X[0], X[0], Z[0]], dtype=np.float32)
    t = verts[faces]
    vol = np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6
    if vol < 0:
        faces = faces[:, ::-1]; vol = -vol
    info = dict(d_o=d_o, tipo=tipo, z_top=z_top, l_o=l_o, vol=vol, h=h)
    return verts, faces, info, (f, X, Z)


def guardar_stl(path, V, F, nombre):
    t = V[F]
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    nrm /= (np.linalg.norm(nrm, axis=1)[:, None] + 1e-20)
    with open(path, 'wb') as fh:
        fh.write(nombre.encode()[:80].ljust(80, b' '))
        fh.write(struct.pack('<I', len(F)))
        rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')])
        rec['n'] = nrm; rec['v'] = t.reshape(-1, 9)
        fh.write(rec.tobytes())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('salida', nargs='?', default='.')
    ap.add_argument('--h', type=float, default=0.12, help='paso de la malla (mm)')
    ap.add_argument('--d', type=float, nargs='*', default=[1.5, 2.0, 2.5, 3.0],
                    help='diámetros de salida de los inyectores swirl (mm)')
    ap.add_argument('--ref', type=float, nargs='*', default=[2.0],
                    help='diámetros de los orificios rectos de referencia (mm)')
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    trabajos = [(d, 'swirl') for d in a.d] + [(d, 'orificio') for d in a.ref]
    for d, tipo in trabajos:
        V, F, info, _ = construir(d, tipo, a.h)
        nombre = f"INY_{tipo}_d{d:.1f}".replace('.', 'p')
        guardar_stl(os.path.join(a.salida, nombre + '.stl'), V, F, nombre)
        print(f"{nombre}: {len(F)} triangulos, largo {info['z_top']:.1f} mm, "
              f"volumen {info['vol']/1000:.2f} cm3, masa PETG ~{info['vol']/1000*1.27:.1f} g")
