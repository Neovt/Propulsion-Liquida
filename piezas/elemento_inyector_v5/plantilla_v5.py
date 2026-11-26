"""
Script de Fusion — ELEMENTO INYECTOR IGNIS v5 (swirl simplex de queroseno, 15 g/s a 7,5 bar, herramienta mínima Ø2,
entrada macho M12x1,5 24°) + bosquejo del mini motor.
Cambios respecto de v4 (pedidos por M. Morales, 26-11-2026):
  - Brida de la punta ensanchada a Ø26 (planos de llave 24): la cara de salida tapa la arandela de cobre Ø22.
  - Sin agujeros de alambre de seguridad (punta y hexágono del cuerpo).
  - Cámara sin puertos laterales (se agregarán cuando corresponda).
  - Placa inyectora con avellanado Ø26,4 para la brida.
Montaje: la brida Ø26 no pasa por el M24, así que primero se atornilla el cuerpo (banco o colector) y después
se ponen la junta, el remolinador, la arandela y la punta.
"""
import adsk.core, adsk.fusion, traceback, math

E = __ELEMENTO__
M = __MOTOR__

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
avisos = []
T59 = math.tan(math.radians(59))


def cm(v): return v / 10.0
def P3(x, y, z): return adsk.core.Point3D.create(cm(x), cm(y), cm(z))
def VR(v): return adsk.core.ValueInput.createByReal(v)
def polar(r, a): return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def plano_z(comp, z):
    if abs(z) < 1e-9: return comp.xYConstructionPlane
    pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xYConstructionPlane, VR(cm(z)))
    return comp.constructionPlanes.add(pi)


def plano_x(comp, x):
    if abs(x) < 1e-9: return comp.yZConstructionPlane
    pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.yZConstructionPlane, VR(cm(x)))
    return comp.constructionPlanes.add(pi)


def circulo(sk, p, d):
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(P3(*p)), cm(d / 2))


def perfiles(sk, lazos=None):
    col = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        if lazos is None or pr.profileLoops.count == lazos: col.add(pr)
    return col


def cuerpos(comp): return [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]


def extruir(comp, prof, dist, op, cuerpo=None):
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(prof, op); ei.setDistanceExtent(False, VR(cm(dist)))
    if op in (CUT, JOIN): ei.participantBodies = [cuerpo] if cuerpo else cuerpos(comp)
    return ext.add(ei)


def cortes_z(comp, z, agujeros, dist, cuerpo=None):
    sk = comp.sketches.add(plano_z(comp, z))
    for (x, y, d) in agujeros: circulo(sk, (x, y, z), d)
    extruir(comp, perfiles(sk), dist, CUT, cuerpo)


def anillo(comp, z, r0, r1, dist, op, cuerpo=None):
    sk = comp.sketches.add(plano_z(comp, z))
    circulo(sk, (0, 0, z), 2 * r0); circulo(sk, (0, 0, z), 2 * r1)
    return extruir(comp, perfiles(sk, 2), dist, op, cuerpo)


def disco(comp, z0, d, h, nombre):
    sk = comp.sketches.add(plano_z(comp, z0)); circulo(sk, (0, 0, z0), d)
    b = extruir(comp, sk.profiles.item(0), h, NEW).bodies.item(0); b.name = nombre
    return b


def poligono_rz(comp, pts, op, cuerpo=None, nombre=None):
    """revoluciona un polígono (r, z) cerrado alrededor del eje Z del componente."""
    sk = comp.sketches.add(comp.xZConstructionPlane)
    S = lambda p: sk.modelToSketchSpace(P3(p[0], 0, p[1]))
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        if abs(a[0] - b[0]) > 1e-9 or abs(a[1] - b[1]) > 1e-9:
            sk.sketchCurves.sketchLines.addByTwoPoints(S(a), S(b))
    return revolver(comp, sk, comp.zConstructionAxis, op, cuerpo, nombre)


def revolver(comp, sk, eje, op, cuerpo=None, nombre=None, perfil=None):
    rev = comp.features.revolveFeatures
    ri = rev.createInput(perfil or sk.profiles.item(0), eje, op)
    ri.setAngleExtent(False, VR(2 * math.pi))
    if op in (CUT, JOIN): ri.participantBodies = [cuerpo] if cuerpo else cuerpos(comp)
    f = rev.add(ri)
    if nombre and op == NEW: f.bodies.item(0).name = nombre
    return f


def taladro(comp, o, d, perfil, op=CUT, cuerpo=None):
    """agujero de revolución con eje en el plano XZ; perfil [(u, radio)] a lo largo de d desde o=(x,z)."""
    sk = comp.sketches.add(comp.xZConstructionPlane)
    nx, nz = d[1], -d[0]
    S = lambda u, v: sk.modelToSketchSpace(P3(o[0] + u * d[0] + v * nx, 0, o[1] + u * d[1] + v * nz))
    pts = [(perfil[0][0], 0.0)] + perfil + [(perfil[-1][0], 0.0)]
    ln = sk.sketchCurves.sketchLines
    for i in range(len(pts) - 1):
        if abs(pts[i][0] - pts[i + 1][0]) < 1e-9 and abs(pts[i][1] - pts[i + 1][1]) < 1e-9: continue
        ln.addByTwoPoints(S(*pts[i]), S(*pts[i + 1]))
    eje = ln.addByTwoPoints(S(*pts[-1]), S(*pts[0]))
    return revolver(comp, sk, eje, op, cuerpo)


def hexagono(sk, c3, af, eje='z', d_ag=None):
    R = af / math.sqrt(3); pts = []
    for k in range(6):
        a = math.radians(30 + 60 * k)
        if eje == 'z': pts.append(sk.modelToSketchSpace(P3(c3[0] + R * math.cos(a), c3[1] + R * math.sin(a), c3[2])))
        else: pts.append(sk.modelToSketchSpace(P3(c3[0], c3[1] + R * math.cos(a), c3[2] + R * math.sin(a))))
    for k in range(6): sk.sketchCurves.sketchLines.addByTwoPoints(pts[k], pts[(k + 1) % 6])
    if d_ag: circulo(sk, c3, d_ag)


def poligono_xy(sk, z, pts):
    P = [sk.modelToSketchSpace(P3(p[0], p[1], z)) for p in pts]
    for i in range(len(P)): sk.sketchCurves.sketchLines.addByTwoPoints(P[i], P[(i + 1) % len(P)])


def capsula(sk, z, p, q, w):
    S = lambda x, y: sk.modelToSketchSpace(P3(x, y, z))
    L = math.hypot(q[0] - p[0], q[1] - p[1]); d = ((q[0] - p[0]) / L, (q[1] - p[1]) / L); n = (-d[1], d[0])
    pu, pd = S(p[0] + w * n[0], p[1] + w * n[1]), S(p[0] - w * n[0], p[1] - w * n[1])
    qu, qd = S(q[0] + w * n[0], q[1] + w * n[1]), S(q[0] - w * n[0], q[1] - w * n[1])
    sk.sketchCurves.sketchLines.addByTwoPoints(pu, qu); sk.sketchCurves.sketchLines.addByTwoPoints(pd, qd)
    sk.sketchCurves.sketchArcs.addByThreePoints(qd, S(q[0] + w * d[0], q[1] + w * d[1]), qu)
    sk.sketchCurves.sketchArcs.addByThreePoints(pu, S(p[0] - w * d[0], p[1] - w * d[1]), pd)


def nuevo_comp(root, nombre):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = nombre
    return occ


# ----------------------------------------------------------------- roscas cosméticas
def caras_cilindro(body, radio_mm, eje, centros):
    out = []
    for i in range(body.faces.count):
        f = body.faces.item(i); g = f.geometry
        if g.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType: continue
        if abs(g.radius - cm(radio_mm)) > 2e-4: continue
        ax, o = g.axis, g.origin
        if eje == 'z' and abs(abs(ax.z) - 1) > 1e-6: continue
        if eje == 'x' and abs(abs(ax.x) - 1) > 1e-6: continue
        for c in centros:
            if eje == 'z' and math.hypot(o.x - cm(c[0]), o.y - cm(c[1])) < 1e-3: out.append(f); break
            if eje == 'x' and math.hypot(o.y - cm(c[0]), o.z - cm(c[1])) < 1e-3: out.append(f); break
    return out


def norm(v):
    v = v.replace('"', '').replace(' ', '')
    try: return '%g' % float(v)
    except ValueError: return v


BSP = ['BSPP', 'BSP Pipe', 'ISO 228', 'BSP']
MET = ['ISO Metric profile', 'ISO Metric']


def rosca(comp, body, radio, eje, centros, tipos, tam, desig, interna, nombre):
    try:
        th = comp.features.threadFeatures; q = th.threadDataQuery
        tipo = None
        for p in tipos:
            for t in q.allThreadTypes:
                if p.lower() in t.lower() and not any(e in t for e in ('Taper', 'BSPT', 'NPT')): tipo = t; break
            if tipo: break
        if not tipo: raise RuntimeError('tipo no encontrado')
        size = next(s for s in q.allSizes(tipo) if norm(s) == norm(tam))
        ds = list(q.allDesignations(tipo, size))
        d = next((x for x in ds if desig and desig in x), ds[0])
        cl = list(q.allClasses(interna, tipo, d))
        info = th.createThreadInfo(interna, tipo, d, cl[0] if cl else '')
        caras = caras_cilindro(body, radio, eje, centros)
        if not caras: raise RuntimeError('cara no encontrada')
        col = adsk.core.ObjectCollection.create()
        for f in caras: col.add(f)
        ti = th.createInput(col, info); ti.isFullLength = True; ti.isModeled = False
        th.add(ti)
    except Exception as e:
        avisos.append('Rosca %s: %s' % (nombre, str(e)[:120]))



def agujero_lateral(comp, plano, centro, d, largo, cuerpo):
    """agujero recto simétrico perpendicular a un plano de origen (para alambre de seguridad)."""
    sk = comp.sketches.add(plano); circulo(sk, centro, d)
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(sk.profiles.item(0), CUT)
    ei.setSymmetricExtent(VR(cm(largo / 2)), True)
    ei.participantBodies = [cuerpo]
    ext.add(ei)



def agujero_lateral(comp, plano, centro, d, largo, cuerpo):
    sk = comp.sketches.add(plano); circulo(sk, centro, d)
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(sk.profiles.item(0), CUT)
    ei.setSymmetricExtent(VR(cm(largo / 2)), True)
    ei.participantBodies = [cuerpo]
    ext.add(ei)


# ================================================================= ELEMENTO v4
def el_cuerpo(comp, z0):
    Z = lambda v: z0 + v
    T12 = math.tan(math.radians(E['ANG_CONO']))
    # espiga macho M12x1,5 + garganta (revolución)
    b = poligono_rz(comp, [(0, Z(0)), (E['R_M12'] - 0.5, Z(0)), (E['R_M12'], Z(0.5)), (E['R_M12'], Z(E['Z_ROSCA12_FIN'])),
                           (E['R_UND0'], Z(E['Z_ROSCA12_FIN'])), (E['R_UND0'], Z(E['Z_HEX0'] + 0.1)), (0, Z(E['Z_HEX0'] + 0.1))],
                    NEW, nombre='Cuerpo').bodies.item(0)
    # hexágono 30
    sk = comp.sketches.add(plano_z(comp, Z(E['Z_HEX0']))); hexagono(sk, (0, 0, Z(E['Z_HEX0'])), E['HEX_AF'])
    extruir(comp, sk.profiles.item(0), E['Z_HEX1'] - E['Z_HEX0'], JOIN, b)
    rc, ro = E['HEX_AF'] / 2 - 0.5, E['HEX_AF'] / 2 + 4
    dz = (ro - rc) * math.tan(math.radians(30))
    zh0, zh1 = Z(E['Z_HEX0']), Z(E['Z_HEX1'])
    poligono_rz(comp, [(rc, zh0 - 0.01), (ro, zh0 - 0.01), (ro, zh0 + dz)], CUT, b)
    poligono_rz(comp, [(rc, zh1 + 0.01), (ro, zh1 - dz), (ro, zh1 + 0.01)], CUT, b)
    # garganta, M24, frente liso
    R1, R24, RF = E['R_UND1'], E['R_M24'], E['R_FRENTE']
    poligono_rz(comp, [(0, Z(E['Z_HEX1'] - 0.1)), (R1, Z(E['Z_HEX1'] - 0.1)), (R1, Z(E['Z_UND1'])), (R24 - 0.6, Z(E['Z_UND1'])),
                       (R24, Z(E['Z_UND1'] + 0.6)), (R24, Z(E['Z_M24_FIN'])), (RF, Z(E['Z_M24_FIN'] + 1.0)),
                       (RF, Z(E['Z_FRENTE'] - 0.5)), (RF - 0.5, Z(E['Z_FRENTE'])), (0, Z(E['Z_FRENTE']))], JOIN, b)
    # canal: cono 24° + alojamiento del tubo + Ø4 + cono 45° + reparto + alojamiento Ø16 + rosca interior M18
    zc = (E['D_CONO_ENT'] - E['D_TUBO']) / 2 / T12
    rp, rpl = E['D_PASO'] / 2, E['D_PLEN'] / 2
    zp0 = E['Z_SW0'] - E['P_PLEN']; zq = zp0 - (rpl - rp)
    taladro(comp, (0, z0 - 0.01), (0, 1), [(0, E['D_CONO_ENT'] / 2), (zc, E['D_TUBO'] / 2), (E['Z_TOPE'], E['D_TUBO'] / 2),
                                            (E['Z_TOPE'] + 0.01, rp), (zq, rp), (zp0, rpl), (E['Z_SW0'] + 0.01, rpl),
                                            (E['Z_SW0'] + 0.01, E['D_SW'] / 2), (E['Z_RI0'] + 0.01, E['D_SW'] / 2),
                                            (E['Z_RI0'] + 0.01, E['R_M18_INT']), (E['Z_FRENTE'] + 0.02, E['R_M18_INT'])], CUT, b)
    rosca(comp, b, E['R_M12'], 'z', [(0, 0)], MET, '12', 'M12x1.5', False, 'M12x1,5 entrada')
    rosca(comp, b, R24, 'z', [(0, 0)], MET, '24', 'M24x1.5', False, 'M24x1,5 montaje')
    rosca(comp, b, E['R_M18_INT'], 'z', [(0, 0)], MET, '18', 'M18x1.5', True, 'M18x1,5 interior')
    return b


def el_remolinador(comp, z0):
    zs, zf = z0 + E['Z_SW_A'], z0 + E['Z_RI0']
    rs, ch = E['D_SW'] / 2, E['CH_SW']
    b = poligono_rz(comp, [(0, zs), (rs - ch, zs), (rs, zs + ch), (rs, zf), (0, zf)], NEW, nombre='Remolinador_h%.2f' % E['H_SLOT']).bodies.item(0)
    cortes_z(comp, zs, [(po[0], po[1], E['D_HC']) for po, pt in E['RANURAS']], E['L_SW'], b)
    sk = comp.sketches.add(plano_z(comp, zf))
    for po, pt in E['RANURAS']: capsula(sk, zf, po, pt, E['B_SLOT'] / 2)
    extruir(comp, perfiles(sk), -E['H_SLOT'], CUT, b)
    return b


def el_punta(comp, z0):
    Z = lambda v: z0 + v
    r1, rs, R18, RB = E['D_O'] / 2, E['D_S'] / 2, E['R_M18'], E['R_BRIDA']
    zr, zc1, zk1, zc, zb = E['Z_RI0'], E['Z_CAM1'], E['Z_CONO1'], E['Z_CARA'], E['Z_BRIDA0']
    pts = [(rs, Z(zr)), (R18 - 0.4, Z(zr)), (R18, Z(zr + 0.4)), (R18, Z(zb)), (RB - 0.3, Z(zb)), (RB, Z(zb + 0.3)),
           (RB, Z(zc - 0.4)), (RB - 0.4, Z(zc)), (r1, Z(zc)), (r1, Z(zk1)), (rs, Z(zc1))]
    b = poligono_rz(comp, pts, NEW, nombre='Punta').bodies.item(0)
    a = E['AF_BRIDA'] / 2
    sk = comp.sketches.add(plano_z(comp, Z(zb)))
    for sx in (1, -1): poligono_xy(sk, Z(zb), [(sx * a, -RB - 1), (sx * (RB + 1), -RB - 1), (sx * (RB + 1), RB + 1), (sx * a, RB + 1)])
    extruir(comp, perfiles(sk), zc - zb + 0.01, CUT, b)
    rosca(comp, b, R18, 'z', [(0, 0)], MET, '18', 'M18x1.5', False, 'M18x1,5 punta')
    return b


def el_juntas(comp, z0):
    anillo(comp, z0 + E['Z_SW0'], E['D_PLEN'] / 2 + 0.1, E['D_SW'] / 2 - 0.05, E['JUNTA_SW'], NEW).bodies.item(0).name = 'Junta_Cu_remolinador'
    anillo(comp, z0 + E['Z_FRENTE'], E['AR_P_I'] / 2, E['AR_P_E'] / 2, E['AR_P_T'], NEW).bodies.item(0).name = 'Arandela_Cu_punta'


def el_arandela(comp, z0):
    anillo(comp, z0 + E['Z_HEX1'], E['AR_I'] / 2, E['AR_E'] / 2, E['AR_T'], NEW).bodies.item(0).name = 'Arandela_Cu_24x30x2'


def elemento(root, z0, prefijo=''):
    occ = {}
    for nombre, fn in (('Cuerpo', el_cuerpo), ('Remolinador', el_remolinador), ('Punta', el_punta),
                       ('Juntas_Cu', el_juntas), ('Arandela_montaje', el_arandela)):
        o = nuevo_comp(root, prefijo + nombre)
        try: fn(o.component, z0); occ[nombre] = o
        except Exception: avisos.append('%s falló:\n%s' % (nombre, traceback.format_exc()[-500:]))
    return occ


def soporte_banco(comp, z0):
    za = z0 + E['Z_HEX1'] + E['AR_T']
    sk = comp.sketches.add(plano_z(comp, za))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(sk.modelToSketchSpace(P3(-30, -20, za)), sk.modelToSketchSpace(P3(30, 20, za)))
    b = extruir(comp, sk.profiles.item(0), 14.0, NEW).bodies.item(0); b.name = 'Soporte_banco'
    cortes_z(comp, za, [(0, 0, 22.376), (-22, 0, 8.5), (22, 0, 8.5)], 14.0, b)
    rosca(comp, b, 22.376 / 2, 'z', [(0, 0)], MET, '24', 'M24x1.5', True, 'M24 soporte')


def racor_y_tubo(comp, z_espiga, largo_tubo=40.0):
    z = z_espiga
    sk = comp.sketches.add(plano_z(comp, z - 4.0)); hexagono(sk, (0, 0, z - 4.0), 14.0, 'z', 12.0)
    extruir(comp, perfiles(sk, 2), 12.0, NEW).bodies.item(0).name = 'Tuerca_tubo_6L_M12x1,5'
    sk = comp.sketches.add(plano_z(comp, z - largo_tubo))
    circulo(sk, (0, 0, z - largo_tubo), 6.0); circulo(sk, (0, 0, z - largo_tubo), 4.0)
    extruir(comp, perfiles(sk, 2), largo_tubo + E['Z_TOPE'], NEW).bodies.item(0).name = 'Tubo_acero_6x1'


def interferencias(design, occs, esperados):
    try:
        ents = adsk.core.ObjectCollection.create()
        for o in occs: ents.add(o)
        ii = design.createInterferenceInput(ents); ii.areCoincidentFacesIncluded = False
        res = design.analyzeInterference(ii)
        malos, ok = [], []
        for r in res:
            par = '%s <-> %s' % (r.entityOne.name, r.entityTwo.name)
            if any(a in par and b in par for a, b in esperados): ok.append(par)
            else: malos.append(par)
        txt = 'Interferencias inesperadas: %s' % ('NINGUNA' if not malos else '; '.join(malos))
        if ok: txt += '\n(superposición de rosca esperada: %s)' % '; '.join(ok)
        return txt
    except Exception as e:
        return 'Análisis de interferencias no disponible (%s)' % str(e)[:100]


def nuevo_doc(app):
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    return d


# ================================================================= MINI MOTOR v3
RF = M['R_FL']; RV = M['R_VAR']; ANGV = (45, 135, 225, 315); RM5 = M['R_M5']; ANG5 = (90, 210, 330)


def mo_colector(comp):
    T = M['T_COL']; b = disco(comp, 0, 2 * RF, T, 'Colector_GOX')
    taladro(comp, (0, -0.01), (0, 1), [(0, 11.188 + 0.6), (0.61, 11.188), (M['Z_ROSCA_COL'], 11.188),
                                        (M['Z_ROSCA_COL'] + 0.01, 11.2), (T + 0.02, 11.2)], CUT, b)
    for (r0, r1, p) in (M['OR_I'], M['GAS'], M['OR_E']): anillo(comp, T, r0, r1, -p, CUT, b)
    zg = T / 2; xs = M['X_SPOT_COL']
    taladro(comp, (xs, zg), (1, 0), [(0, 10.5), (RF + 2 - xs, 10.5)], CUT, b)
    rg, rr = 11.445 / 2, 3.0
    u1 = 12.0; u2 = u1 + (rg - rr) / T59; u3 = xs - (M['R_GAS_ENT'] - 2.0)
    taladro(comp, (xs + 0.01, zg), (-1, 0), [(0, rg), (u1, rg), (u2, rr), (u3, rr), (u3 + rr / T59, 0.0)], CUT, b)
    taladro(comp, (M['R_GAS_ENT'], T + 0.01), (0, -1), [(0, 2.0), (T - zg + 0.01, 2.0), (T - zg + 0.01 + 2.0 / T59, 0.0)], CUT, b)
    p5 = [polar(RM5, a) for a in ANG5]
    cortes_z(comp, 0, [(x, y, 5.5) for x, y in p5], T, b)
    cortes_z(comp, 0, [(x, y, 9.5) for x, y in p5], T - 8.0, b)
    cortes_z(comp, 0, [(x, y, 9.0) for x, y in (polar(RV, a) for a in ANGV)], T, b)
    rosca(comp, b, 11.188, 'z', [(0, 0)], MET, '24', 'M24x1.5', True, 'M24 colector')
    rosca(comp, b, rg, 'x', [(0, zg)], BSP, '1/4', None, True, 'G1/4 GOX')
    for (r0, r1, p), nm in ((M['OR_I'], 'ORing_26x2'), (M['OR_E'], 'ORing_45x2')):
        sk = comp.sketches.add(comp.xZConstructionPlane); circulo(sk, ((r0 + r1) / 2, 0, T - p / 2), p - 0.05)
        revolver(comp, sk, comp.zConstructionAxis, NEW, nombre=nm)


def mo_placa(comp):
    z0, T = M['T_COL'], M['T_PL']; zt = z0 + T
    b = disco(comp, z0, 2 * RF, T, 'Placa_inyectora')
    cortes_z(comp, z0, [(0, 0, 22.4)], T, b)
    cortes_z(comp, M['Z_CARA'] - M['PROF_AV'], [(0, 0, M['D_AV'])], M['PROF_AV'] + 0.01, b)
    anillo(comp, zt, M['R_CAM_I'], M['R_RAN_E'], -1.0, CUT, b)
    cortes_z(comp, z0, [(x, y, 4.2) for x, y in (polar(RM5, a) for a in ANG5)], 8.0, b)
    cortes_z(comp, z0, [(x, y, 9.0) for x, y in (polar(RV, a) for a in ANGV)], T, b)
    ang = math.radians(20); d = (-math.sin(ang), math.cos(ang))
    L = (T + 0.6) / math.cos(ang); o = (M['R_GAS_ENT'] + 0.3 * math.tan(ang), z0 - 0.3)
    uf = L - 5.0 - 0.3
    hb = taladro(comp, o, d, [(0, 2.0), (uf, 2.0), (uf + 1.0 / T59, 1.0), (L, 1.0)], NEW).bodies.item(0)
    pats = comp.features.circularPatternFeatures
    ents = adsk.core.ObjectCollection.create(); ents.add(hb)
    pi = pats.createInput(ents, comp.zConstructionAxis); pi.quantity = VR(M['N_GAS'])
    pi.totalAngle = adsk.core.ValueInput.createByString('360 deg'); pi.isSymmetric = False
    pats.add(pi)
    tools = adsk.core.ObjectCollection.create()
    for bb in cuerpos(comp):
        if bb != b: tools.add(bb)
    ci = comp.features.combineFeatures.createInput(b, tools); ci.operation = CUT; ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci)
    rosca(comp, b, 2.1, 'z', [polar(RM5, a) for a in ANG5], MET, '5', 'M5x0.8', True, 'M5 placa')


def mo_camara_tobera(root):
    zc = M['Z_CARA']; zt0 = zc; zt1 = zt0 + M['L_TUBO']; znb = zt1
    rci, rce = M['R_CAM_I'], M['R_CAM_E']
    o = nuevo_comp(root, 'Junta_inyector'); anillo(o.component, zc - 1.0, rci + 0.2, M['R_RAN_E'] - 0.05, 1.0, NEW).bodies.item(0).name = 'Junta_grafito'
    o = nuevo_comp(root, 'Camara'); c = o.component
    b = anillo(c, zt0, rci, rce, M['L_TUBO'], NEW).bodies.item(0); b.name = 'Camara'
    o = nuevo_comp(root, 'Junta_tobera'); anillo(o.component, zt1, rci + 0.2, M['R_RAN_E'] - 0.05, 1.0, NEW).bodies.item(0).name = 'Junta_grafito'
    o = nuevo_comp(root, 'Tobera'); t = o.component
    K = M['CONT']; P = lambda k: (K[k][1], znb + K[k][0]); ex = P('ex'); TF = M['T_FL_TOB']; RBS = M['R_BOSS']
    sk = t.sketches.add(t.xZConstructionPlane); S = lambda p: sk.modelToSketchSpace(P3(p[0], 0, p[1]))
    ln, ar = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
    ln.addByTwoPoints(S((RF, znb)), S(P('p0'))); ln.addByTwoPoints(S(P('p0')), S(P('a1')))
    ar.addByThreePoints(S(P('a1')), S(P('m1')), S(P('e1'))); ln.addByTwoPoints(S(P('e1')), S(P('s2')))
    ar.addByThreePoints(S(P('s2')), S(P('m2')), S(P('th'))); ar.addByThreePoints(S(P('th')), S(P('m3')), S(P('e3')))
    ln.addByTwoPoints(S(P('e3')), S(ex)); ln.addByTwoPoints(S(ex), S((RBS, ex[1])))
    ln.addByTwoPoints(S((RBS, ex[1])), S((RBS, znb + TF))); ln.addByTwoPoints(S((RBS, znb + TF)), S((RF, znb + TF)))
    ln.addByTwoPoints(S((RF, znb + TF)), S((RF, znb)))
    tb = revolver(t, sk, t.zConstructionAxis, NEW, nombre='Tobera_Cu').bodies.item(0)
    anillo(t, znb, rci - 0.5, M['R_RAN_E'], 1.0, CUT, tb)
    cortes_z(t, znb, [(x, y, 9.0) for x, y in (polar(RV, a) for a in ANGV)], TF, tb)
    o = nuevo_comp(root, 'Varillas_M8'); v = o.component
    za, zb = -2.0 - 6.5 - 2.0, znb + TF + 2.0 + 6.5 + 2.0
    for a in ANGV:
        x, y = polar(RV, a)
        sk = v.sketches.add(plano_z(v, za)); circulo(sk, (x, y, za), 8.0)
        extruir(v, sk.profiles.item(0), zb - za, NEW).bodies.item(0).name = 'Varilla_M8'
        for zr, s in ((0.0, -1), (znb + TF, 1)):
            zw = zr if s > 0 else zr - 2.0
            sk = v.sketches.add(plano_z(v, zw)); circulo(sk, (x, y, zw), 16.0); circulo(sk, (x, y, zw), 8.4)
            extruir(v, perfiles(sk, 2), 2.0, NEW)
            zn = zw + 2.0 if s > 0 else zw - 6.5
            sk = v.sketches.add(plano_z(v, zn)); hexagono(sk, (x, y, zn), 13.0, 'z', 8.0)
            extruir(v, perfiles(sk, 2), 6.5, NEW)


def mo_tornillos(root):
    o = nuevo_comp(root, 'Tornillos_M5x14'); c = o.component
    zc = M['T_COL'] - 8.0
    for a in ANG5:
        x, y = polar(RM5, a)
        sk = c.sketches.add(plano_z(c, zc - 5.0)); circulo(sk, (x, y, zc - 5.0), 8.5)
        bb = extruir(c, sk.profiles.item(0), 5.0, NEW).bodies.item(0)
        sk = c.sketches.add(plano_z(c, zc)); circulo(sk, (x, y, zc), 4.1)
        extruir(c, sk.profiles.item(0), 14.0, JOIN, bb)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        d1 = nuevo_doc(app); r1 = d1.rootComponent
        occ = elemento(r1, 0.0)
        o = nuevo_comp(r1, 'Soporte_banco')
        try: soporte_banco(o.component, 0.0); occ['Soporte'] = o
        except Exception: avisos.append('Soporte falló:\n' + traceback.format_exc()[-400:])
        o = nuevo_comp(r1, 'Racor_banco')
        try: racor_y_tubo(o.component, 0.0)
        except Exception: avisos.append('Racor falló:\n' + traceback.format_exc()[-400:])
        msg1 = interferencias(d1, list(occ.values()), [('Cuerpo', 'Punta'), ('Cuerpo', 'Soporte')])
        d2 = nuevo_doc(app); r2 = d2.rootComponent
        z_el = -(E['Z_HEX1'] + E['AR_T'])
        occ2 = elemento(r2, z_el, 'Elemento_')
        piezas = {}
        for nombre, fn in (('Colector_GOX', mo_colector), ('Placa_inyectora', mo_placa)):
            o = nuevo_comp(r2, nombre)
            try: fn(o.component); piezas[nombre] = o
            except Exception: avisos.append('%s falló:\n%s' % (nombre, traceback.format_exc()[-400:]))
        try: mo_camara_tobera(r2)
        except Exception: avisos.append('Cámara/tobera falló:\n' + traceback.format_exc()[-400:])
        try: mo_tornillos(r2)
        except Exception: avisos.append('Tornillos falló:\n' + traceback.format_exc()[-400:])
        o = nuevo_comp(r2, 'Racor_combustible')
        try: racor_y_tubo(o.component, z_el, 40.0)
        except Exception: avisos.append('Racor comb. falló')
        est = list(occ2.values()) + list(piezas.values())
        for i in range(r2.occurrences.count):
            oc = r2.occurrences.item(i)
            if oc.component.name in ('Camara', 'Tobera', 'Junta_inyector', 'Junta_tobera'): est.append(oc)
        msg2 = interferencias(d2, est, [('Cuerpo', 'Punta'), ('Cuerpo', 'Colector')])
        msg = ('Doc 1 (Elemento v5): ' + msg1 + '\n\nDoc 2 (Mini motor, bosquejo): ' + msg2 +
               '\n\nElemento v5: largo %.1f mm, 15 g/s a 7,5 bar (teórico), herramienta mínima Ø2.' % E['Z_CARA'])
        if avisos: msg += '\n\nAvisos:\n- ' + '\n- '.join(avisos)
        ui.messageBox(msg)
    except Exception:
        if ui: ui.messageBox('Error:\n{}'.format(traceback.format_exc()))
