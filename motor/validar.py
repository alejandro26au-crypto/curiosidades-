"""Valida un guion contra la fórmula y normaliza valores desconocidos del catálogo."""
import re

from . import camara, efectos, escenarios, personajes
from .audio import SFX
from .efectos import NUM_PAL
from .formula import BEATS, PALABRAS_OBJETIVO, PLANOS_OBJETIVO

ORDEN_BEATS = [b[0] for b in BEATS]


def _palabras(t):
    return [w for w in re.split(r"\s+", t.strip()) if w]


def normalizar(g):
    """Corrige silenciosamente valores fuera de catálogo. Devuelve lista de avisos."""
    avisos = []
    for pid, sp in g.get("personajes", {}).items():
        for campo, lista, defecto in (("sombrero", personajes.SOMBREROS, "ninguno"),
                                      ("peinado", personajes.PEINADOS, "ninguno"),
                                      ("ropa", personajes.ROPAS, "camisa")):
            if sp.get(campo) and sp[campo] not in lista:
                avisos.append(f"personaje {pid}: {campo} '{sp[campo]}' -> '{defecto}'")
                sp[campo] = defecto
        sp["accesorios"] = [a for a in sp.get("accesorios", []) if a in personajes.ACCESORIOS]
    for i, pl in enumerate(g.get("planos", [])):
        f = pl.setdefault("fondo", {})
        if f.get("lugar") not in escenarios.LUGARES:
            avisos.append(f"plano {i}: lugar '{f.get('lugar')}' -> 'campo'")
            f["lugar"] = "campo"
        if f.get("hora") not in escenarios.HORAS:
            f["hora"] = "dia"
        f["props"] = [p for p in f.get("props", []) if p.get("tipo") in escenarios.PROPS]
        for a in pl.get("actores", []):
            if a.get("id") not in g.get("personajes", {}):
                avisos.append(f"plano {i}: actor '{a.get('id')}' no definido (se omite)")
            if a.get("expresion") not in personajes.EXPRESIONES:
                a["expresion"] = "neutral"
            if a.get("pose") not in personajes.POSES:
                a["pose"] = "idle"
            if a.get("objeto") and a["objeto"] not in personajes.OBJETOS:
                a["objeto"] = None
        pl["actores"] = [a for a in pl.get("actores", []) if a.get("id") in g.get("personajes", {})]
        cam = pl.setdefault("camara", {})
        if cam.get("mov") not in camara.MOVIMIENTOS:
            cam["mov"] = "push_in"
        if cam.get("encuadre") and cam["encuadre"] not in camara.ENCUADRES:
            cam["encuadre"] = "medio"
        if pl.get("inserto") and pl["inserto"].get("tipo") not in efectos.INSERTOS:
            pl["inserto"] = None
        pl["efectos"] = [e for e in pl.get("efectos", []) if e in efectos.EFECTOS]
        pl["sfx"] = [s for s in pl.get("sfx", []) if (s if isinstance(s, str) else s.get("nombre")) in SFX]
        if pl.get("voz", "narrador") != "narrador" and pl["voz"] not in g.get("personajes", {}):
            pl["voz"] = "narrador"
    return avisos


def revisar(g):
    """Devuelve (puntaje 0-100, lista de fallas) según la fórmula."""
    fallas = []
    planos = g.get("planos", [])
    textos = [p.get("texto", "") for p in planos]
    todas = [w for t in textos for w in _palabras(t)]
    n = len(todas)
    apodo = (g.get("apodo") or "").lower()

    lo, hi = PALABRAS_OBJETIVO
    if not lo <= n <= hi:
        fallas.append(f"Largo: {n} palabras (objetivo {lo}-{hi}, ~66 s de voz).")
    lo, hi = PLANOS_OBJETIVO
    if not lo <= len(planos) <= hi:
        fallas.append(f"Planos: {len(planos)} (objetivo {lo}-{hi}, un corte cada 2-3 s).")
    for i, t in enumerate(textos):
        if len(_palabras(t)) > 16:
            fallas.append(f"Plano {i}: {len(_palabras(t))} palabras; pártelo (máx. 16 por plano).")
    if planos and len(_palabras(textos[0])) > 16:
        fallas.append("Gancho demasiado largo: la primera frase debe caber en ~3 s.")
    if apodo:
        veces = sum(t.lower().count(apodo) for t in textos)
        if veces < 3:
            fallas.append(f"El apodo '{g.get('apodo')}' aparece {veces} veces (mínimo 3: burla, escalada, remate).")
        if planos and apodo not in textos[-1].lower() and apodo not in (textos[-2].lower() if len(textos) > 1 else ""):
            fallas.append("El remate no reutiliza el apodo (callback).")
    else:
        fallas.append("Falta 'apodo' (el mote burlón que da la gente al protagonista).")
    nums = [w for w in todas if re.search(r"\d", w) or re.sub(r"\W", "", w.lower()) in NUM_PAL]
    if len(nums) < 4:
        fallas.append(f"Solo {len(nums)} números; la fórmula canta cifras (mín. 4, con cuenta regresiva).")
    # posición de la explicación
    idx = None
    acum = 0
    for p in planos:
        t = p.get("texto", "").lower()
        if "el truco" in t or "¿por qué?" in t:
            idx = acum
            break
        acum += len(_palabras(t))
    if idx is None:
        fallas.append("Falta la bisagra 'El truco es que...' / '¿Por qué?'.")
    elif not 0.55 <= idx / max(1, n) <= 0.85:
        fallas.append(f"La explicación llega al {idx / max(1, n):.0%} del guion (ideal 65-80%).")
    # orden de beats
    vistos = [p.get("beat") for p in planos if p.get("beat") in ORDEN_BEATS]
    pos = [ORDEN_BEATS.index(b) for b in vistos]
    if pos != sorted(pos):
        fallas.append("Los beats no siguen el orden gancho→burla→apuesta→rival→proceso→escalada→giro→truco→desenlace→remate.")
    faltan = [b for b in ORDEN_BEATS if b not in vistos]
    if faltan:
        fallas.append(f"Faltan beats: {', '.join(faltan)}.")
    if not any(p.get("voz", "narrador") != "narrador" for p in planos):
        fallas.append("No hay ninguna línea con voz de personaje (la burla y el remate van citados).")
    if not any(p.get("inserto") for p in planos):
        fallas.append("No hay insertos de datos (termómetro/manómetro/contador...).")
    rivales = [k for k, v in g.get("personajes", {}).items() if v.get("rol") == "rival"]
    if not rivales:
        fallas.append("No hay rival definido (rol: 'rival').")
    puntaje = max(0, 100 - 9 * len(fallas))
    return puntaje, fallas
