"""
Proto-tanque IGNIS - piezas provisorias impresas (PETG/PLA)
  Pieza 1: adaptador cuello M30x1,5 (macho) -> R1/4 BSPT (macho), sello o-ring triangular
  Pieza 2: niple doble R1/4 BSPT macho (cruz -> solenoide JT22-02)

Generador de mallas STL solo con numpy: cada pieza es un perfil (r, z) revolucionado,
donde el radio de cada anillo puede depender del angulo (rosca helicoidal, hexagono).
Todas las cotas en mm. Editar PARAMETROS y volver a correr:  python3 generar_piezas.py
"""
import numpy as np, struct, sys, os

# ---------------------------------------------------------------- PARAMETROS
N_THETA = 360            # divisiones angulares
PASOS_POR_HILO = 24      # anillos por paso de rosca

BORE = 4.0               # diametro del agujero pasante (ambas piezas)

# R1/4 BSPT (ISO 7-1, Whitworth 55 grados, conica 1:16)
R14_P = 25.4 / 19        # 1,337 mm
R14_DMAJ_GAUGE = 13.157  # diametro mayor en el plano de calibre
R14_GAUGE_DESDE_PUNTA = 6.0
R14_AJUSTE_DIAM = -0.20  # compensa sobre-extrusion (negativo = mas delgado)
R14_LARGO = 10.0         # largo roscado
R14_UNDERCUT = 1.5       # garganta de salida junto al hexagono

# M30x1,5 macho (ISO metrica 60 grados, paralela)
M30_P = 1.5
M30_DMAJ = 30.0
M30_HOLGURA_DIAM = 0.30  # holgura para impresion (diametro)
M30_LARGO = 12.0         # largo roscado (no pasarse de la profundidad del cuello)

# Sello o-ring en el cuello (glandula triangular 45 grados)
ORING_CS = 2.0           # seccion del o-ring
ORING_DI = 31.0          # diametro interior del o-ring (= diametro del collar)

# Hexagonos (entre caras)
HEX1_AF = 40.0           # pieza 1
HEX1_ALTO = 12.0         # desde la cara del cuello hasta la cara superior
HEX2_AF = 17.0           # pieza 2
HEX2_ALTO = 9.0
# ---------------------------------------------------------------------------

TH = np.linspace(0, 2*np.pi, N_THETA, endpoint=False)


def hex_r(af):
    a = af / 2
    phi = (TH % (np.pi/3)) - np.pi/6
    return a / np.cos(phi)


def perfil_trapecio(P, h, semiang_deg, cresta):
    w = h * np.tan(np.radians(semiang_deg))
    raiz = P - 2*w - cresta
    def f(u):
        u = np.mod(u, P)
        y = np.zeros_like(u)
        a0 = raiz/2; a1 = a0 + w; a2 = a1 + cresta; a3 = a2 + w
        m = (u >= a0) & (u < a1); y[m] = (u[m]-a0)/w*h
        m = (u >= a1) & (u < a2); y[m] = h
        m = (u >= a2) & (u < a3); y[m] = (a3-u[m])/w*h
        return y
    return f

R14_H = 0.640327 * R14_P
R14_PERF = perfil_trapecio(R14_P, R14_H, 27.5, (R14_P - 2*R14_H*np.tan(np.radians(27.5)))/2)
M30_H = 0.61343 * M30_P
M30_PERF = perfil_trapecio(M30_P, M30_H, 30.0, M30_P/8)


def anillos_rosca(z0, z1, P, perf, cresta_r, punta_z, punta_r0):
    """Anillos de rosca (mano derecha) entre z0 y z1.
    cresta_r(z): radio de cresta; chaflan 45 grados en la punta (punta_z, punta_r0)."""
    n = max(2, int(np.ceil(abs(z1-z0)/P*PASOS_POR_HILO)) + 1)
    out = []
    for z in np.linspace(z0, z1, n):
        u = z - P*TH/(2*np.pi)
        h = perf(u)
        rc = cresta_r(z)
        r = (rc - perf_h_max(perf, P)) + h
        r = np.minimum(r, punta_r0 + abs(z - punta_z))
        out.append((z, r))
    return out

_cache = {}
def perf_h_max(perf, P):
    k = id(perf)
    if k not in _cache:
        _cache[k] = perf(np.linspace(0, P, 2000)).max()
    return _cache[k]


def c(z, r):
    return (z, np.full(N_THETA, float(r)))


def malla(anillos):
    """Revoluciona un perfil cerrado de anillos -> triangulos (toro cerrado)."""
    Z = np.array([a[0] for a in anillos]); R = np.array([a[1] for a in anillos])
    n = len(anillos); m = N_THETA
    V = np.stack([R*np.cos(TH), R*np.sin(TH), np.repeat(Z[:, None], m, 1)], -1).reshape(-1, 3)
    idx = lambda i, j: (i % n)*m + (j % m)
    F = []
    for i in range(n):
        for j in range(m):
            a, b, c_, d = idx(i, j), idx(i, j+1), idx(i+1, j+1), idx(i+1, j)
            F.append((a, b, c_)); F.append((a, c_, d))
    F = np.array(F)
    # quitar triangulos degenerados
    t = V[F]
    area = np.linalg.norm(np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0]), axis=1)
    F = F[area > 1e-10]
    t = V[F]
    vol = np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum()/6
    if vol < 0:
        F = F[:, ::-1]; vol = -vol
    return V, F, vol


def guardar_stl(path, V, F, nombre):
    t = V[F]
    nrm = np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    with open(path, 'wb') as f:
        f.write(nombre.encode()[:80].ljust(80, b' '))
        f.write(struct.pack('<I', len(F)))
        rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')])
        rec['n'] = nrm; rec['v'] = t.reshape(-1, 9)
        f.write(rec.tobytes())


def r14_cresta(z_punta, sentido):
    """sentido=+1: la rosca crece hacia +z desde la punta; -1: crece hacia -z."""
    rg = (R14_DMAJ_GAUGE + R14_AJUSTE_DIAM)/2
    return lambda z: rg + (sentido*(z - z_punta) - R14_GAUGE_DESDE_PUNTA)/32.0


# ------------------------------------------------------------------ PIEZA 1
def pieza1():
    rb = BORE/2
    m30_rc = (M30_DMAJ - M30_HOLGURA_DIAM)/2
    m30_rr = m30_rc - M30_H
    Lg = 1.35*ORING_CS                 # cateto de la glandula triangular
    rcol = ORING_DI/2                  # collar donde se monta el o-ring
    r_tope = rcol + Lg                 # inicio del anillo de tope (contacta el cuello)
    r_tope2 = r_tope + 0.6
    a = HEX1_AF/2; rcorner = a/np.cos(np.pi/6)
    zt = HEX1_ALTO                     # cara superior del hexagono
    cr = r14_cresta(zt + R14_UNDERCUT + R14_LARGO, -1)
    r14_raiz_base = cr(zt + R14_UNDERCUT) - R14_H
    ztop = zt + R14_UNDERCUT + R14_LARGO

    A = []
    A.append(c(-M30_LARGO, rb))
    A += anillos_rosca(-M30_LARGO, 0.0, M30_P, M30_PERF, lambda z: m30_rc,
                       -M30_LARGO, m30_rr - 0.4)
    A.append(c(0.0, rcol))             # escalon al collar
    A.append(c(Lg, rcol))              # vertice superior de la glandula
    A.append(c(0.0, r_tope))           # cono interior 45 -> tope
    A.append(c(0.0, r_tope2))          # anillo de tope 0,6 mm
    # cono exterior 45 grados recortado por el hexagono (imprimible sin soporte)
    for z in np.linspace(0, rcorner - r_tope2, 40)[1:]:
        A.append((z, np.minimum(hex_r(HEX1_AF), r_tope2 + z)))
    # chaflan superior y cara superior
    zc = zt - (rcorner - a)
    A.append((zc, hex_r(HEX1_AF)))
    for z in np.linspace(zc, zt, 12)[1:]:
        A.append((z, np.minimum(hex_r(HEX1_AF), a + (zt - z))))
    A.append(c(zt, r14_raiz_base - 0.1))
    A.append(c(zt + R14_UNDERCUT, r14_raiz_base - 0.1))
    A += anillos_rosca(zt + R14_UNDERCUT, ztop, R14_P, R14_PERF, cr, ztop, cr(ztop) - R14_H - 0.3)
    A.append(c(ztop, rb))
    return A


# ------------------------------------------------------------------ PIEZA 2
def pieza2():
    rb = BORE/2
    a = HEX2_AF/2; rcorner = a/np.cos(np.pi/6)
    crA = r14_cresta(0.0, +1)
    z1 = R14_LARGO
    ruA = crA(z1) - R14_H - 0.1
    z2 = z1 + R14_UNDERCUT
    zh_top = z2 + HEX2_ALTO
    z3 = zh_top + R14_UNDERCUT
    ztop = z3 + R14_LARGO
    crB = r14_cresta(ztop, -1)
    ruB = crB(z3) - R14_H - 0.1

    A = []
    A.append(c(0.0, rb))
    A += anillos_rosca(0.0, z1, R14_P, R14_PERF, crA, 0.0, crA(0.0) - R14_H - 0.3)
    A.append(c(z1, ruA)); A.append(c(z2, ruA))
    for z in np.linspace(z2, z2 + (rcorner - ruA), 30)[1:]:
        A.append((z, np.minimum(hex_r(HEX2_AF), ruA + (z - z2))))
    zc = zh_top - (rcorner - a)
    A.append((zc, hex_r(HEX2_AF)))
    for z in np.linspace(zc, zh_top, 10)[1:]:
        A.append((z, np.minimum(hex_r(HEX2_AF), a + (zh_top - z))))
    A.append(c(zh_top, ruB)); A.append(c(z3, ruB))
    A += anillos_rosca(z3, ztop, R14_P, R14_PERF, crB, ztop, crB(ztop) - R14_H - 0.3)
    A.append(c(ztop, rb))
    return A


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for nombre, fn in [('P1_adaptador_M30_R14', pieza1), ('P2_niple_R14_R14', pieza2)]:
        A = fn()
        V, F, vol = malla(A)
        z = V[:, 2]; V[:, 2] -= z.min()   # apoyar en z=0 (orientacion de impresion)
        guardar_stl(os.path.join(out, nombre + '.stl'), V, F, nombre)
        print(f'{nombre}: {len(F)} triangulos, volumen {vol/1000:.2f} cm3, '
              f'alto {z.max()-z.min():.1f} mm, masa PETG ~{vol/1000*1.27:.1f} g')
