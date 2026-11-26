"""
Estimaciones de caudal y tiempo de descarga para los inyectores de prueba.
SON ESTIMACIONES de diseño, no mediciones: el Cd real hay que medirlo en el banco.

Modelo
  agua:  Q = mu * A_o * sqrt(2*dP/rho)         mu de la teoría de remolino (Abramovich), A_geo = 1,7
  aire:  flujo crítico si P0/Pa > 1,893         mdot = Cd * A_o * P0 * sqrt(g/(R*T0)) * (2/(g+1))^((g+1)/(2(g-1)))
         subsónico en caso contrario            (Cd del aire por el remolino: se supone 0,6, rango 0,5-0,8)
  tanque: 14 L, vaciado adiabático (g = 1,4), T0 = 293 K, descarga a Pa = 1,013 bar
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_inyector as gi

PA = 101325.0; RHO = 998.0; R = 287.0; G = 1.4; T0 = 293.0
V_TANQUE = 14e-3
CD_AIRE = 0.6

def caudal_agua(d_o, dP_bar, mu):
    A = np.pi * (d_o * 1e-3)**2 / 4
    return mu * A * np.sqrt(2 * dP_bar * 1e5 / RHO)          # m3/s

def mdot_aire(P, Tt, A, Cd):
    r = P / PA
    if r >= ((G + 1) / 2) ** (G / (G - 1)):
        return Cd * A * P * np.sqrt(G / (R * Tt)) * (2 / (G + 1)) ** ((G + 1) / (2 * (G - 1)))
    pr = PA / P
    return Cd * A * P * np.sqrt(2 * G / ((G - 1) * R * Tt)) * np.sqrt(pr ** (2 / G) - pr ** ((G + 1) / G))

def tiempo_vaciado(d_o, P0_man_bar, Cd=CD_AIRE, P_fin_man_bar=0.2):
    A = np.pi * (d_o * 1e-3)**2 / 4
    P0 = PA + P0_man_bar * 1e5; Pf = PA + P_fin_man_bar * 1e5
    m0 = P0 * V_TANQUE / (R * T0)
    P = P0; t = 0.0; dt = 0.01
    while P > Pf and t < 3600:
        Tt = T0 * (P / P0) ** ((G - 1) / G)
        md = mdot_aire(P, Tt, A, Cd)
        dP = -md * G * P0 ** (1 / G) / m0 * P ** (1 - 1 / G)
        P += dP * dt; t += dt
    return t

if __name__ == '__main__':
    print("Ø sal | puertos Ø | semiáng. | mu   | AGUA mL/s a dP=1/2/3 bar      | AIRE g/s a 2/3 bar man. | vaciado 14 L (a 0,2 bar man.) 2 / 3 bar")
    for d in (1.5, 2.0, 2.5, 3.0):
        r_p, R_in = gi.swirl_geom(d)
        t = gi.swirl_teoria(R_in, d / 2, r_p)
        q = [caudal_agua(d, p, t['mu']) * 1e6 for p in (1, 2, 3)]
        A = np.pi * (d * 1e-3)**2 / 4
        m = [mdot_aire(PA + p * 1e5, T0, A, CD_AIRE) * 1e3 for p in (2, 3)]
        tv = [tiempo_vaciado(d, p) for p in (2, 3)]
        print(f"{d:4.1f}  | {2*r_p:5.2f}     | {2*t['semiangulo']:4.0f}° tot| {t['mu']:.3f}| {q[0]:5.1f} / {q[1]:5.1f} / {q[2]:5.1f}      | {m[0]:4.2f} / {m[1]:4.2f}           | {tv[0]:5.0f} s / {tv[1]:5.0f} s")
    print("\nSensibilidad del vaciado con aire (Ø2,0, 3 bar man.) al Cd supuesto:")
    for cd in (0.5, 0.6, 0.8):
        print(f"  Cd={cd}: {tiempo_vaciado(2.0, 3, cd):.0f} s")
