"""
ELEMENTO INYECTOR IGNIS v4 — swirl simplex de queroseno, objetivo 15 g/s a 7,5 bar, herramienta mínima Ø2
=========================================================================================================
Eje z desde la punta de la entrada macho (z = 0) hacia la salida. Cotas en mm.

Camino del combustible:
  1. Entrada MACHO M12x1,5 con cono interior de 24° (DIN 2353 / ISO 8434-1, serie L, tubo Ø6): el tubo de acero
     de 6 mm del banco se conecta directo con tuerca y anillo cortante.
  2. Paso Ø4 (igual que la entrada del Allison, Ø4,1).
  3. Cámara de reparto Ø13,4.
  4. 2 agujeros axiales Ø2 en el remolinador.
  5. 2 ranuras tangenciales 2,0 x 0,44 (fresa Ø2), tangentes a la cámara de remolino: aquí nace el giro.
  6. Cámara de remolino Ø8 x 4 (en la punta), cono 90°, orificio Ø2 x 1,5.
Sellos (sin ranuras abiertas):
  * Junta de cobre bajo el remolinador (como la pieza 9 del Allison).
  * La punta aprieta el remolinador y su brida asienta contra el cuerpo con arandela de cobre.
  * Montaje: hombro del hexágono contra la placa o el soporte con arandela de cobre DIN 7603 24x30x2.
"""
import math

MIN_HERR = 2.0
# ---------------- hidráulica
D_O, L_O = 2.0, 1.5
D_S, L_S = 8.0, 4.0
N_SLOT, B_SLOT = 2, 2.0
H_SLOT = 0.44                 # calibración: remolinadores alternativos 0,40 y 0,48
H_ALT = (0.40, 0.48)
R_IN = D_S / 2 - B_SLOT / 2   # 3,0
A_GEO = math.pi * R_IN * (D_O / 2) / (N_SLOT * B_SLOT * H_SLOT)
# ---------------- entrada macho DIN 2353 L6 (M12x1,5, cono 24°)
R_M12, L_STUD = 6.0, 12.0     # espiga roscada z 0–12 (rosca útil hasta 10,5)
Z_ROSCA12_FIN, R_UND0 = 10.5, 5.1
D_CONO_ENT, ANG_CONO = 8.1, 12.0   # diámetro del cono en la cara y semiángulo (24° incluido)
D_TUBO, Z_TOPE = 6.05, 7.0         # alojamiento del tubo y tope
D_PASO = 4.0
# ---------------- cuerpo
HEX_AF, Z_HEX0, Z_HEX1 = 30.0, 12.0, 22.0   # hexágono 30; su cara delantera (z 22) es el hombro de sello
R_UND1, Z_UND1 = 11.0, 24.0                 # garganta Ø22 z 22–24
R_M24, Z_M24_FIN = 12.0, 38.0               # montaje M24x1,5 z 24–38
R_FRENTE = 11.0                             # frente liso Ø22
D_PLEN, P_PLEN = 13.4, 1.5
Z_SW0 = 40.0                                # fondo del alojamiento (asiento de la junta)
JUNTA_SW = 0.5                              # junta de cobre Ø13,6/Ø15,9 x 0,5
D_SW, L_SW = 16.0, 6.0                      # remolinador Ø16 x 6
Z_SW_A = Z_SW0 + JUNTA_SW                   # cara trasera del remolinador
Z_RI0 = Z_SW_A + L_SW                       # 46,5: cara delantera del remolinador = inicio rosca interior M18
L_RI = 5.0
Z_FRENTE = Z_RI0 + L_RI                     # 51,5: cara delantera del cuerpo
R_M18_INT = 16.376 / 2
D_HC, R_HC = 2.0, 5.5                       # agujeros axiales Ø2 en r 5,5 (borde interior a 0,5 de la cámara)
CH_SW = 0.3
# ---------------- punta
R_M18 = 9.0
AR_P_I, AR_P_E, AR_P_T = 18.5, 22.0, 1.0    # arandela de cobre de la punta
Z_BRIDA0 = Z_FRENTE + AR_P_T                # 52,5
R_BRIDA, AF_BRIDA = 11.0, 19.0
Z_CAM1 = Z_RI0 + L_S
Z_CONO1 = Z_CAM1 + (D_S / 2 - D_O / 2)
Z_CARA = Z_CONO1 + L_O                      # 55,0
# ---------------- arandela de montaje
AR_I, AR_E, AR_T = 24.2, 30.0, 2.0


def ranuras():
    out = []
    t_h = math.sqrt(R_HC ** 2 - R_IN ** 2)
    for k in range(N_SLOT):
        a = 2 * math.pi * k / N_SLOT
        n = (math.cos(a), math.sin(a)); t = (-math.sin(a), math.cos(a))
        out.append(((R_IN * n[0] - t_h * t[0], R_IN * n[1] - t_h * t[1]), (R_IN * n[0], R_IN * n[1])))
    return out


if __name__ == '__main__':
    print(f"A = {A_GEO:.2f}; largo del elemento {Z_CARA:.1f} mm; cara de la punta Ø{2*R_BRIDA}")
    print(f"agujero axial: borde interior {R_HC-1:.1f} vs cámara {D_S/2:.1f}; borde exterior {R_HC+1:.1f} vs remolinador {D_SW/2:.1f}; reparto r {D_PLEN/2:.1f}")
