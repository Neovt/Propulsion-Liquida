"""Caudal del elemento v5 contra ΔP, y calibración con remolinadores alternativos (ESTIMACIÓN, teoría de Abramovich)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom_v5 as g
from scipy.optimize import brentq


def teoria(A):
    phi = brentq(lambda p: (1 - p) * math.sqrt(2) / (p * math.sqrt(p)) - A, 1e-5, 0.9999)
    mu = phi * math.sqrt(phi / (2 - phi))
    ta = 2 * mu * A / math.sqrt((1 + math.sqrt(1 - phi)) ** 2 - 4 * mu ** 2 * A ** 2)
    return mu, 2 * math.degrees(math.atan(ta))


AO = math.pi * (g.D_O * 1e-3) ** 2 / 4
print("h ranura | A    | cono  | queroseno g/s a 5 / 7,5 / 8 / 10 bar | agua g/s a 7,5 bar")
for h in (g.H_ALT[0], g.H_SLOT, g.H_ALT[1]):
    A = math.pi * g.R_IN * (g.D_O / 2) / (g.N_SLOT * g.B_SLOT * h)
    mu, cono = teoria(A)
    q = [mu * AO * math.sqrt(2 * 800 * dp * 1e5) * 1e3 for dp in (5, 7.5, 8, 10)]
    w = mu * AO * math.sqrt(2 * 998 * 7.5e5) * 1e3
    print(f"  {h:.2f}   | {A:.2f} | {cono:.0f}°  | " + " / ".join(f"{x:.1f}" for x in q) + f"            | {w:.1f}")
print("2 L de queroseno a 15 g/s: %.0f s" % (2000 * 0.8 / 15))
