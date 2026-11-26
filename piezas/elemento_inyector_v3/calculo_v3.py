"""Hidráulica del elemento v3 y dimensionamiento del mini motor v3 (TODO ESTIMACIÓN; ver supuestos)."""
import math, json, sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom_v3 as g
from scipy.optimize import brentq

PA = 101325.0


def teoria(A):
    phi = brentq(lambda p: (1 - p) * math.sqrt(2) / (p * math.sqrt(p)) - A, 1e-4, 0.9999)
    mu = phi * math.sqrt(phi / (2 - phi))
    ta = 2 * mu * A / math.sqrt((1 + math.sqrt(1 - phi)) ** 2 - 4 * mu ** 2 * A ** 2)
    return phi, mu, math.degrees(math.atan(ta))


PHI, MU, SEMI = teoria(g.A_GEO)
A_O = math.pi * (g.D_O * 1e-3) ** 2 / 4
FL = {'agua': (998.0, 1.0e-3, 0.072), 'queroseno': (800.0, 1.5e-3, 0.026)}


def mdot(dp, rho): return MU * A_O * math.sqrt(2 * rho * dp)


def smd(dp, rho, mu_l, sig):
    m = mdot(dp, rho); FN = m / math.sqrt(dp * rho)
    t = 2.7 * (g.D_O * 1e-3 * FN * mu_l / math.sqrt(dp * rho)) ** 0.25
    tc = t * math.cos(math.radians(SEMI))
    return t, (4.52 * (sig * mu_l ** 2 / (1.2 * dp ** 2)) ** 0.25 * tc ** 0.25
               + 0.39 * (sig * rho / (1.2 * dp)) ** 0.25 * tc ** 0.75)


AREAS = {'paso Ø6': math.pi * 9, 'cámara de reparto (anillo Ø6–Ø12 por altura)': math.pi * 6 * 1.5,
         '3 agujeros Ø2': 3 * math.pi, '3 ranuras 2 x 0,9': 3 * g.B_SLOT * g.H_SLOT,
         'orificio Ø2': math.pi, 'área efectiva (mu·A)': MU * math.pi}

# ------------------------------------------------------------- mini motor v3
P_TANQUE = 8e5; DP_LINEA = 0.5e5; PC = 5e5; OF = 2.2; RHO_K = 800.0
DP_INY = P_TANQUE + PA - DP_LINEA - PC
MF = mdot(DP_INY, RHO_K); MO = OF * MF; MT = MF + MO
CSTAR = 1750 * 0.88; GAM = 1.22
AT = MT * CSTAR / PC
DT = round(math.sqrt(4 * AT / math.pi) * 1e3 * 2) / 2      # a 0,5 mm
AT = math.pi * (DT * 1e-3) ** 2 / 4
PC_R = MT * CSTAR / AT
pr = PC_R / PA
Me = math.sqrt(2 / (GAM - 1) * (pr ** ((GAM - 1) / GAM) - 1))
EPS = (1 / Me) * ((2 / (GAM + 1)) * (1 + (GAM - 1) / 2 * Me ** 2)) ** ((GAM + 1) / (2 * (GAM - 1)))
CF = math.sqrt(2 * GAM ** 2 / (GAM - 1) * (2 / (GAM + 1)) ** ((GAM + 1) / (GAM - 1)) * (1 - (1 / pr) ** ((GAM - 1) / GAM)))
F = 0.95 * CF * PC_R * AT
DE = round(DT * math.sqrt(EPS) * 2) / 2
DC = 56.0
CR = (DC / DT) ** 2
LSTAR = 1.2
# GOX: agujeros Ø2 (mínimo de taller), flujo bloqueado
R_O2 = 259.8
def mch(P0, A): return 0.8 * A * P0 * math.sqrt(1.4 / (R_O2 * 293)) * (2 / 2.4) ** (2.4 / 0.8)
N_GAS = 7; D_GAS = 2.0
A_GAS = N_GAS * math.pi * (D_GAS * 1e-3) ** 2 / 4
P0_GOX = brentq(lambda p: mch(p, A_GAS) - MO, 1e5, 1e8)
# solenoide GOX Ø5 (Cd 0,6) con regulador a 20 bar man.: capacidad subsónica hacia P0_GOX
def m_sub(P1, P2, A, Cd=0.6, R=R_O2, T=293, gm=1.4):
    r = P2 / P1
    crit = (2 / (gm + 1)) ** (gm / (gm - 1))
    if r < crit: return Cd * A * P1 * math.sqrt(gm / (R * T)) * (2 / (gm + 1)) ** ((gm + 1) / (2 * (gm - 1)))
    return Cd * A * P1 * math.sqrt(2 * gm / ((gm - 1) * R * T) * (r ** (2 / gm) - r ** ((gm + 1) / gm)))
CAP_SOL = m_sub(21e5, P0_GOX, math.pi * 25e-6 / 4)

# contorno de tobera
RC, RTH, RE = DC / 2, DT / 2, DE / 2
R1, R2, R3 = 10.0, 1.5 * RTH, 0.4 * RTH
TC, TD = math.radians(30), math.radians(15)
U0 = 2.0
c1 = (U0, RC - R1)
e1 = (c1[0] + R1 * math.sin(TC), c1[1] + R1 * math.cos(TC))
m1 = (c1[0] + R1 * math.sin(TC / 2), c1[1] + R1 * math.cos(TC / 2))
s2r = RTH + R2 - R2 * math.cos(TC)
s2 = (e1[0] + (e1[1] - s2r) / math.tan(TC), s2r)
ut = s2[0] + R2 * math.sin(TC)
m2 = (ut - R2 * math.sin(TC / 2), RTH + R2 - R2 * math.cos(TC / 2))
th = (ut, RTH)
e3 = (ut + R3 * math.sin(TD), RTH + R3 - R3 * math.cos(TD))
m3 = (ut + R3 * math.sin(TD / 2), RTH + R3 - R3 * math.cos(TD / 2))
ex = (e3[0] + max(RE - e3[1], 0.3) / math.tan(TD), max(RE, e3[1] + 0.3))
CONT = dict(p0=(0.0, RC), a1=(U0, RC), m1=m1, e1=e1, s2=s2, m2=m2, th=th, m3=m3, e3=e3, ex=ex)
# volumen convergente (aprox. tronco de cono) para fijar el largo del tubo por L*
v_conv = math.pi / 3 * (s2[0] - U0) * 1e-3 * ((RC * 1e-3) ** 2 + RC * RTH * 1e-6 + (RTH * 1e-3) ** 2)
L_CIL = (LSTAR * AT - v_conv) / (math.pi * (RC * 1e-3) ** 2) * 1e3

def dT(q, t, k, rho, cp): return 2 * q * math.sqrt(t) / (math.sqrt(math.pi) * math.sqrt(k * rho * cp))

if __name__ == '__main__':
    print("=== ELEMENTO v3 ===")
    print(f"orificio Ø{g.D_O} x {g.L_O}, cámara Ø{g.D_S} x {g.L_S}, {g.N_SLOT} ranuras {g.B_SLOT} x {g.H_SLOT} -> A = {g.A_GEO:.3f}")
    print(f"mu = {MU:.3f}, cono ≈ {2*SEMI:.0f}° total; herramienta mínima Ø{g.MIN_HERR} mm")
    print("áreas en serie (mm2):", {k: round(v, 2) for k, v in AREAS.items()})
    print(" ΔP bar | fluido    | g/s   | mL/s | SMD µm")
    for dp in (1, 2, 3.5, 5, 8):
        for n, (rho, mu_l, sig) in FL.items():
            m = mdot(dp * 1e5, rho); _, d = smd(dp * 1e5, rho, mu_l, sig)
            print(f" {dp:6.1f} | {n:9s} | {m*1e3:5.1f} | {m/rho*1e6:4.1f} | {d*1e6:5.0f}")
    print(f"comparación: Allison 250 (CFD de A. Espinoza, 5 bar de entrada) 27,8 g/s; v3 con agua a 5 bar {mdot(5e5,998)*1e3:.1f} g/s")
    print("\n=== MINI MOTOR v3 (con el elemento v3) ===")
    print(f"ΔP inyector {DP_INY/1e5:.2f} bar | queroseno {MF*1e3:.1f} g/s ({MF/RHO_K*1e6:.0f} mL/s) | GOX {MO*1e3:.1f} g/s | total {MT*1e3:.1f} g/s")
    print(f"garganta Ø{DT} (Pc {PC_R/1e5:.2f} bar) | cámara Ø{DC} (contracción {CR:.1f}) | salida Ø{DE} (ε {EPS:.2f}) | empuje ≈ {F:.0f} N")
    print(f"largo cilíndrico de cámara para L* = {LSTAR} m: {L_CIL:.0f} mm")
    print(f"GOX: {N_GAS} agujeros Ø{D_GAS} -> colector {P0_GOX/1e5:.1f} bar abs (bloqueado: {P0_GOX/PC:.2f} > 1,89)")
    print(f"solenoide GOX Ø5 con regulador 20 bar man.: capacidad ≈ {CAP_SOL*1e3:.0f} g/s (necesario {MO*1e3:.0f})")
    print(f"2 L de queroseno alcanzan para {2000/(MF/RHO_K*1e6):.0f} s; encendido de 3 s: {MF*3/RHO_K*1e6:.0f} mL y {MO*3*1e3:.0f} g de GOX")
    for nm, (k, rho, cp) in {'cobre': (390, 8900, 385), 'inox': (16, 8000, 500)}.items():
        print(f"  {nm}: garganta +{dT(4e6,3,k,rho,cp):.0f} K en 3 s, cámara +{dT(1.5e6,3,k,rho,cp):.0f} K")
    json.dump(dict(DT=DT, DE=DE, DC=DC, L_CIL=round(L_CIL), N_GAS=N_GAS, D_GAS=D_GAS,
                   CONT={k: [round(v[0], 4), round(v[1], 4)] for k, v in CONT.items()}),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mini_motor_v3', 'motor_v3.json'), 'w'), indent=1)
