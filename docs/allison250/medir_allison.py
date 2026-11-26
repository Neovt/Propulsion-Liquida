"""Mide la geometría del documento activo y la escribe en medidas_allison.txt (carpeta del Allison)."""
import adsk.core, adsk.fusion, traceback, math

SALIDA = r'C:\Users\matia\Universidad de Concepción\Propelentes líquidos - Inyector Alisson250_files\user_files\medidas_allison.txt'


def mm(v): return v * 10.0


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        L = ['documento: ' + app.activeDocument.name]
        bodies = []
        root = design.rootComponent
        for b in root.bRepBodies: bodies.append(('root', b))
        for occ in root.allOccurrences:
            for b in occ.bRepBodies: bodies.append((occ.fullPathName, b))
        for path, b in bodies:
            bb = b.boundingBox
            L.append('\n=== CUERPO %s / %s  sólido=%s  volumen=%.1f mm3' % (path, b.name, b.isSolid, b.volume * 1000))
            L.append('bbox min (%.3f, %.3f, %.3f)  max (%.3f, %.3f, %.3f)' % tuple(
                [mm(bb.minPoint.x), mm(bb.minPoint.y), mm(bb.minPoint.z), mm(bb.maxPoint.x), mm(bb.maxPoint.y), mm(bb.maxPoint.z)]))
            for i in range(b.faces.count):
                f = b.faces.item(i); g = f.geometry; fb = f.boundingBox
                ext = 'bb[(%.3f,%.3f,%.3f)-(%.3f,%.3f,%.3f)] area=%.3f' % (mm(fb.minPoint.x), mm(fb.minPoint.y), mm(fb.minPoint.z),
                                                                     mm(fb.maxPoint.x), mm(fb.maxPoint.y), mm(fb.maxPoint.z), f.area * 100)
                t = g.surfaceType
                if t == adsk.core.SurfaceTypes.CylinderSurfaceType:
                    L.append('CIL r=%.4f D=%.4f eje(%.3f,%.3f,%.3f) org(%.3f,%.3f,%.3f) %s' % (
                        mm(g.radius), 2 * mm(g.radius), g.axis.x, g.axis.y, g.axis.z, mm(g.origin.x), mm(g.origin.y), mm(g.origin.z), ext))
                elif t == adsk.core.SurfaceTypes.PlaneSurfaceType:
                    n = g.normal
                    L.append('PLANO n(%.3f,%.3f,%.3f) org(%.3f,%.3f,%.3f) %s' % (n.x, n.y, n.z, mm(g.origin.x), mm(g.origin.y), mm(g.origin.z), ext))
                elif t == adsk.core.SurfaceTypes.ConeSurfaceType:
                    L.append('CONO semiang=%.2f° r=%.4f eje(%.3f,%.3f,%.3f) org(%.3f,%.3f,%.3f) %s' % (
                        math.degrees(g.halfAngle), mm(g.radius), g.axis.x, g.axis.y, g.axis.z, mm(g.origin.x), mm(g.origin.y), mm(g.origin.z), ext))
                elif t == adsk.core.SurfaceTypes.TorusSurfaceType:
                    L.append('TORO R=%.4f r=%.4f %s' % (mm(g.majorRadius), mm(g.minorRadius), ext))
                elif t == adsk.core.SurfaceTypes.SphereSurfaceType:
                    L.append('ESFERA r=%.4f %s' % (mm(g.radius), ext))
                else:
                    L.append('OTRA tipo=%d %s' % (t, ext))
        open(SALIDA, 'w', encoding='utf-8').write('\n'.join(L))
        ui.messageBox('Medidas escritas: %d cuerpos.' % len(bodies))
    except Exception:
        if ui: ui.messageBox('Error:\n' + traceback.format_exc())
