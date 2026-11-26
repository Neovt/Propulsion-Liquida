"""
ELEMENTO INYECTOR IGNIS v3 — swirl simplex de queroseno, pensado para CNC sin herramientas finas
=================================================================================================
Regla de diseño: NINGUNA broca ni fresa menor que Ø2,0 mm (MIN_HERR). Todas las cotas en mm.
Eje z desde la cara trasera del cuerpo (z = 0) hacia la punta.

Camino del combustible (en orden):
  1. Entrada G1/4 hembra atrás (racor recto G1/4 – tubo 6 mm del banco).
  2. Paso axial Ø6 por el cuerpo.
  3. Cámara de reparto Ø12 x 1,5 frente al remolinador.
  4. 3 agujeros axiales Ø2 que atraviesan el remolinador.
  5. 3 ranuras tangenciales 2,0 x 0,9 en la cara delantera del remolinador (fresa Ø2): aquí nace el giro.
  6. Cámara de remolino Ø8 x 4 (dentro de la punta).
  7. Cono convergente de 90°.
  8. Orificio de salida Ø2,0 x 1,5 -> cono hueco.
Piezas: Cuerpo, Remolinador, Punta (se atornilla DENTRO del cuerpo y aprieta el remolinador contra su asiento).
"""
import math

MIN_HERR = 2.0

# ---------------------------------------------------------------- hidráulica (elegida para CNC)
D_O, L_O = 2.0, 1.5          # orificio
D_S, L_S = 7.0, 4.0          # cámara de remolino (Ø7: deja 0,5 mm entre los agujeros axiales y la cámara)
N_SLOT, B_SLOT = 3, 2.0      # ranuras (fresa Ø2)
H_SLOT = 0.75                # profundidad de ranura (resultado: A ≈ 1,75)
R_IN = D_S / 2 - B_SLOT / 2  # 3,0: la ranura es tangente a la pared de la cámara
A_GEO = math.pi * R_IN * (D_O / 2) / (N_SLOT * B_SLOT * H_SLOT)

# ---------------------------------------------------------------- cuerpo
HEX_AF, Z_HEX = 27.0, 12.0   # hexágono 27, z 0–12; su cara delantera es el hombro de sello
D_G14, L_G14 = 11.445, 12.0  # entrada G1/4 (diámetro menor), largo de rosca
R_UND1, Z_UND1 = 11.0, 14.0  # garganta Ø22 z 12–14 (asiento plano para la arandela)
R_M24, Z_M24_FIN = 12.0, 28.0  # rosca de montaje M24x1,5 z 14–28
R_FRENTE = 11.0              # tramo delantero liso Ø22 (pasa por la rosca M24 de la placa)
D_PASO = 6.0
D_PLEN, P_PLEN = 12.4, 1.5   # cámara de reparto (asiento del remolinador: anillo Ø12,4–Ø14)
D_SW, L_SW = 14.0, 6.0       # alojamiento del remolinador Ø14 H7
Z_SW0 = 32.0                 # cara trasera del remolinador
Z_PLEN0 = Z_SW0 - P_PLEN
Z_ROSCA_INT0 = Z_SW0 + L_SW  # 38: empieza la rosca interior M18x1,5
L_ROSCA_INT = 5.0
Z_FRENTE = Z_ROSCA_INT0 + L_ROSCA_INT   # 43: cara delantera del cuerpo
R_M18_INT = 16.376 / 2       # diámetro menor M18x1,5 interior
# ---------------------------------------------------------------- remolinador
D_HC, R_HC = 2.0, 5.0        # agujeros axiales Ø2 en r = 5 (borde interior a 0,5 de la cámara, pared 1,0 al borde)
CH_SW = 0.3
# ---------------------------------------------------------------- punta
R_M18 = 9.0                  # rosca exterior M18x1,5 (z 38–43, dentro del cuerpo)
R_BRIDA, AF_BRIDA = 11.0, 19.0   # brida Ø22 con planos de llave 19
Z_PUNTA0 = Z_ROSCA_INT0
Z_BRIDA0 = Z_FRENTE + 0.5   # la brida NO toca el cuerpo (juego 0,5): la punta solo aprieta el remolinador
R_UND_P = 8.2               # garganta de salida de rosca en la punta
Z_CAM1 = Z_PUNTA0 + L_S                    # fin de la cámara de remolino
Z_CONO1 = Z_CAM1 + (D_S / 2 - D_O / 2)     # fin del cono 90°
Z_CARA = Z_CONO1 + L_O                     # cara de salida
# ---------------------------------------------------------------- sellos
AR_I, AR_E, AR_T = 24.2, 30.0, 2.0   # arandela de cobre DIN 7603 A 24x30x2


def ranuras():
    out = []
    t_h = math.sqrt(R_HC ** 2 - R_IN ** 2)
    for k in range(N_SLOT):
        a = 2 * math.pi * k / N_SLOT
        n = (math.cos(a), math.sin(a)); t = (-math.sin(a), math.cos(a))
        po = (R_IN * n[0] - t_h * t[0], R_IN * n[1] - t_h * t[1])   # centro del agujero axial
        pt = (R_IN * n[0], R_IN * n[1])                              # punto tangente a la cámara
        out.append((po, pt))
    return out


def resumen():
    return dict(largo_total=Z_CARA, A=A_GEO, min_herr=MIN_HERR)


if __name__ == '__main__':
    print(f"A = {A_GEO:.3f}; largo del elemento {Z_CARA:.1f} mm; brida de la punta Ø{2*R_BRIDA}")
    print("herramientas usadas: brocas Ø2 (orificio, agujeros), fresa Ø2 (ranuras), Ø6, Ø8, Ø12, Ø14 — mínimo", MIN_HERR)
