"""Insertos de datos (termómetro, manómetro, contador, reloj, comparativas,
diagramas), partículas y subtítulos palabra por palabra."""
import math
import random
import re

import cairo

from .dibujo import (NEGRO, hex2rgb, mezcla, color, relleno_contorno, rect_redondo, elipse,
                     linea, curva, poligono, texto, ease_out_back, ease_in_out, ease_out, clamp)
from .formula import ESTILO

W, H = 1080, 1920
INSERTOS = ["termometro", "manometro", "contador", "reloj", "comparativa", "flechas",
            "texto", "capas", "regla", "ficha"]
EFECTOS = ["nieve", "lluvia", "chispas", "polvo", "vapor", "escarcha", "velocidad",
           "impacto", "destello", "calor", "hojas", "burbujas", "oscuro"]


def _fmt(v, dec):
    s = f"{v:.{dec}f}"
    return s.replace("-", "−")


def _panel(ctx, cx, cy, w, h, k):
    """Tarjeta con rebote al aparecer."""
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    rect_redondo(ctx, -w / 2 + 10, -h / 2 + 14, w, h, 46)
    color(ctx, (0, 0, 0), 0.25)
    ctx.fill()
    rect_redondo(ctx, -w / 2, -h / 2, w, h, 46)
    relleno_contorno(ctx, (1, 0.99, 0.96), 9)


def dibujar_inserto(ctx, ins, p, t, dur):
    """p = progreso del plano 0..1; t = segundos desde inicio del plano."""
    tipo = ins.get("tipo")
    entrada = ease_out_back(clamp(t / 0.35))
    salida = 1 - ease_in_out(clamp((t - (dur - 0.18)) / 0.18)) if dur > 0.6 else 1
    k = max(0.001, entrada * salida)
    anim = ease_in_out(clamp((t - 0.25) / max(0.3, dur * 0.8 - 0.25)))
    de, a = float(ins.get("de", 0)), float(ins.get("a", 0))
    v = de + (a - de) * anim
    dec = int(ins.get("decimales", 0 if abs(a - de) >= 3 or float(a).is_integer() else 1))
    unidad = ins.get("unidad", "")
    etiqueta = ins.get("etiqueta", "")
    pos = ins.get("posicion", "arriba")
    cy = H * {"arriba": 0.30, "abajo": 0.86}.get(pos, 0.45)
    ctx.save()
    if tipo == "termometro":
        _panel(ctx, W * 0.5, cy, 640, 620, k)
        lo, hi = float(ins.get("min", min(de, a) - 5)), float(ins.get("max", max(de, a) + 5))
        f = clamp((v - lo) / (hi - lo))
        x0, y0, hgt = -150, -240, 400
        rect_redondo(ctx, x0 - 34, y0 - 10, 68, hgt + 40, 34)
        relleno_contorno(ctx, (1, 1, 1), 8)
        frio, cal = (0.3, 0.6, 1.0), (0.95, 0.22, 0.15)
        cc = mezcla(frio, cal, f)
        rect_redondo(ctx, x0 - 18, y0 + hgt * (1 - f), 36, hgt * f + 30, 18)
        color(ctx, cc)
        ctx.fill()
        ctx.arc(x0, y0 + hgt + 50, 56, 0, 2 * math.pi)
        relleno_contorno(ctx, cc, 8)
        for i in range(9):
            yy = y0 + i * hgt / 8
            linea(ctx, [(x0 + 40, yy), (x0 + 62, yy)], 5)
        texto(ctx, _fmt(v, dec) + unidad, 110, -20, 120, peso=cairo.FONT_WEIGHT_BOLD, relleno=cc,
              trazo=NEGRO, grosor=10)
        if etiqueta:
            texto(ctx, etiqueta, 110, 130, 46, relleno=(0.15, 0.15, 0.18))
    elif tipo == "manometro":
        _panel(ctx, W * 0.5, cy, 640, 620, k)
        lo, hi = float(ins.get("min", 0)), float(ins.get("max", max(de, a) * 1.25 or 1))
        ctx.arc(0, 20, 230, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.97, 0.97, 0.95), 10)
        for i in range(11):
            ang = math.radians(225 - i * 27)
            r0 = 190 if i % 5 else 170
            linea(ctx, [(math.cos(ang) * r0, 20 - math.sin(ang) * r0),
                        (math.cos(ang) * 214, 20 - math.sin(ang) * 214)], 6)
        f = clamp((v - lo) / (hi - lo))
        ang = math.radians(225 - f * 270)
        linea(ctx, [(0, 20), (math.cos(ang) * 175, 20 - math.sin(ang) * 175)], 12, (0.9, 0.15, 0.12))
        ctx.arc(0, 20, 22, 0, 2 * math.pi)
        relleno_contorno(ctx, NEGRO, 0)
        texto(ctx, _fmt(v, dec) + (" " + unidad if unidad else ""), 0, 150, 84, relleno=(0.1, 0.1, 0.12))
        if etiqueta:
            texto(ctx, etiqueta, 0, -250, 46, relleno=(0.15, 0.15, 0.18))
    elif tipo in ("contador", "texto", "regla"):
        val = ins.get("texto") if tipo == "texto" else _fmt(v, dec) + (" " + unidad if unidad else "")
        tam = 150 if len(str(val)) < 8 else 110
        _panel(ctx, W * 0.5, cy, 800, 380, k)
        cc = hex2rgb(ins.get("color"), (0.12, 0.12, 0.14))
        texto(ctx, str(val), 0, 20 if etiqueta else 0, tam, relleno=cc, trazo=NEGRO, grosor=0)
        if etiqueta:
            texto(ctx, etiqueta, 0, -125, 48, relleno=(0.35, 0.35, 0.4))
        if tipo == "regla":
            f = clamp((v - float(ins.get("min", 0))) / max(1e-6, float(ins.get("max", max(de, a)))))
            rect_redondo(ctx, -340, 120, 680, 30, 15)
            relleno_contorno(ctx, (0.9, 0.9, 0.9), 5)
            rect_redondo(ctx, -340, 120, 680 * f, 30, 15)
            color(ctx, (0.95, 0.35, 0.2))
            ctx.fill()
    elif tipo == "reloj":
        _panel(ctx, W * 0.5, cy, 620, 620, k)
        ctx.arc(0, 0, 240, 0, 2 * math.pi)
        relleno_contorno(ctx, (1, 1, 0.97), 10)
        for i in range(12):
            ang = i * math.pi / 6
            linea(ctx, [(math.sin(ang) * 200, -math.cos(ang) * 200), (math.sin(ang) * 222, -math.cos(ang) * 222)], 8)
        horas = v  # 'de'/'a' en horas decimales (p. ej. 0 -> 3 = medianoche a las 3)
        am = (horas % 12) / 12 * 2 * math.pi
        mm = (horas % 1) * 2 * math.pi
        linea(ctx, [(0, 0), (math.sin(am) * 120, -math.cos(am) * 120)], 16)
        linea(ctx, [(0, 0), (math.sin(mm) * 190, -math.cos(mm) * 190)], 9, (0.85, 0.15, 0.12))
        ctx.arc(0, 0, 16, 0, 2 * math.pi)
        relleno_contorno(ctx, NEGRO, 0)
        hh = int(horas) % 24
        texto(ctx, ins.get("texto") or f"{hh}:{int((horas % 1) * 60):02d}", 0, 360, 70, relleno=(1, 1, 1), grosor=12)
    elif tipo == "comparativa":
        _panel(ctx, W * 0.5, cy, 860, 640, k)
        items = ins.get("items") or [{"etiqueta": "Él", "valor": a, "color": "#3CB371"},
                                     {"etiqueta": "Vecino", "valor": de, "color": "#E04B3A"}]
        mx = max(float(i.get("valor", 0)) for i in items) or 1
        n = len(items)
        for j, it in enumerate(items):
            x = -300 + j * (600 / max(1, n - 1)) if n > 1 else 0
            val = float(it.get("valor", 0))
            hh = 360 * (val / mx) * anim
            rect_redondo(ctx, x - 70, 200 - hh, 140, hh + 1, 18)
            relleno_contorno(ctx, hex2rgb(it.get("color"), (0.3, 0.6, 0.9)), 8)
            texto(ctx, _fmt(val * anim, 0) + (it.get("unidad") or unidad), x, 160 - hh - 40, 64, relleno=(0.1, 0.1, 0.12))
            texto(ctx, it.get("etiqueta", ""), x, 255, 44, relleno=(0.2, 0.2, 0.24))
        if etiqueta:
            texto(ctx, etiqueta, 0, -270, 46, relleno=(0.3, 0.3, 0.35))
    elif tipo == "flechas":
        # izquierda: fuerza concentrada (se clava); derecha: fuerza repartida (flota)
        _panel(ctx, W * 0.5, cy, 900, 600, k)
        izq, der = ins.get("izq", "Concentrado"), ins.get("der", "Repartido")
        linea(ctx, [(-400, 140), (400, 140)], 8, (0.55, 0.42, 0.25))
        for i in range(2):
            x = -250 + (i - 0.5) * 50
            yb = 140 + 40 * anim
            linea(ctx, [(x, -120), (x, yb)], 16, (0.88, 0.18, 0.15))
            poligono(ctx, [(x - 24, yb - 10), (x + 24, yb - 10), (x, yb + 30)])
            relleno_contorno(ctx, (0.88, 0.18, 0.15), 0)
        for i in range(7):
            x = 110 + i * 40
            linea(ctx, [(x, 0), (x, 110)], 9, (0.98, 0.6, 0.15))
            poligono(ctx, [(x - 14, 104), (x + 14, 104), (x, 130)])
            relleno_contorno(ctx, (0.98, 0.6, 0.15), 0)
        texto(ctx, izq, -250, -210, 56, relleno=(0.88, 0.18, 0.15))
        texto(ctx, der, 230, -210, 56, relleno=(0.9, 0.5, 0.05))
        linea(ctx, [(0, -240), (0, 200)], 4, (0.7, 0.7, 0.7))
    elif tipo == "ficha":
        # ficha técnica: título, subtítulo, filas etiqueta/valor e iconos (☢) que aparecen uno a uno
        filas = ins.get("filas") or []
        n_ic = int(ins.get("iconos", 0))
        alto = 250 + 120 * len(filas) + (170 if n_ic else 0)
        _panel(ctx, W * 0.5, cy, 880, alto, k)
        y = -alto / 2 + 95
        texto(ctx, ins.get("titulo", ""), 0, y, 84, peso=cairo.FONT_WEIGHT_BOLD, relleno=(0.1, 0.12, 0.16))
        if ins.get("subtitulo"):
            texto(ctx, ins["subtitulo"], 0, y + 78, 50, relleno=(0.45, 0.47, 0.52))
        y += 150
        amarillo = hex2rgb(ESTILO["color_destacado"])
        for j, (et, val) in enumerate(filas):
            kj = ease_out_back(clamp((t - 0.25 - 0.22 * j) / 0.3))
            if kj <= 0:
                continue
            rect_redondo(ctx, -380, y - 48, 760, 96, 24)
            color(ctx, (0.93, 0.93, 0.9))
            ctx.fill()
            texto(ctx, et, -170, y, 52, relleno=(0.3, 0.32, 0.36))
            ctx.save()
            ctx.translate(190, y)
            ctx.scale(kj, kj)
            texto(ctx, val, 0, 0, 76, peso=cairo.FONT_WEIGHT_BOLD, relleno=amarillo, trazo=NEGRO, grosor=10)
            ctx.restore()
            y += 120
        if n_ic:
            paso = 760 / n_ic
            for i in range(n_ic):
                ki = ease_out_back(clamp((t - 0.45 - 0.11 * i) / 0.22), 2.2)
                if ki <= 0:
                    continue
                x = -380 + paso * (i + 0.5)
                ctx.save()
                ctx.translate(x, y + 40)
                ctx.scale(ki, ki)
                rr = min(42, paso * 0.45)
                ctx.arc(0, 0, rr, 0, 2 * math.pi)
                relleno_contorno(ctx, (1, 0.84, 0.0), 5)
                for a in range(3):
                    a0 = -math.pi / 2 + a * 2 * math.pi / 3 - 0.52
                    ctx.move_to(0, 0)
                    ctx.arc(0, 0, rr * 0.8, a0, a0 + 1.04)
                    ctx.close_path()
                    color(ctx, NEGRO)
                    ctx.fill()
                ctx.arc(0, 0, rr * 0.22, 0, 2 * math.pi)
                relleno_contorno(ctx, (1, 0.84, 0.0), 3)
                ctx.restore()
    elif tipo == "capas":
        _panel(ctx, W * 0.5, cy, 680, 680, k)
        capas = ins.get("capas") or [{"color": "#BFE6FF", "etiqueta": "hielo"},
                                     {"color": "#F28C28", "etiqueta": "fruta 0°C"}]
        n = len(capas)
        for j, cp in enumerate(capas):
            rr = 250 * (1 - j / (n + 0.4)) * (0.6 + 0.4 * anim)
            ctx.arc(0, 0, rr, 0, 2 * math.pi)
            relleno_contorno(ctx, hex2rgb(cp.get("color")), 8)
        for j, cp in enumerate(capas):
            rr = 250 * (1 - j / (n + 0.4))
            yy = -rr + 40
            texto(ctx, cp.get("etiqueta", ""), 0, yy + (j * 10), 46, relleno=(1, 1, 1), grosor=10)
    ctx.restore()


# --- Partículas / efectos de pantalla -------------------------------------------------
def dibujar_efecto(ctx, nombre, t, dur, semilla=0):
    r = random.Random(hash((nombre, semilla)) & 0xFFFFFF)
    if nombre in ("nieve", "lluvia", "hojas", "chispas", "polvo", "burbujas"):
        n = {"nieve": 90, "lluvia": 140, "hojas": 18, "chispas": 40, "polvo": 50, "burbujas": 30}[nombre]
        for i in range(n):
            x0, y0 = r.uniform(0, W), r.uniform(0, H)
            sp = r.uniform(0.6, 1.4)
            if nombre == "nieve":
                x = (x0 + 30 * math.sin(t * sp + i)) % W
                y = (y0 + t * 120 * sp) % H
                ctx.arc(x, y, 4 + 4 * sp, 0, 2 * math.pi)
                color(ctx, (1, 1, 1), 0.85)
                ctx.fill()
            elif nombre == "lluvia":
                x = (x0 - t * 200) % W
                y = (y0 + t * 1800 * sp) % H
                linea(ctx, [(x, y), (x - 8, y + 40)], 3, (0.75, 0.85, 1), 0.6)
            elif nombre == "hojas":
                x = (x0 + t * 160 * sp) % W
                y = (y0 + t * 90 * sp + 40 * math.sin(t * 2 + i)) % H
                elipse(ctx, x, y, 14, 7)
                color(ctx, (0.85, 0.55, 0.15))
                ctx.fill()
            elif nombre == "chispas":
                k = (t * sp * 0.7 + i / n) % 1
                x = x0 + 40 * math.sin(i + t * 3)
                y = H * 0.9 - k * H * 0.8
                ctx.arc(x, y, 5 * (1 - k) + 1, 0, 2 * math.pi)
                color(ctx, (1, 0.7, 0.2), 1 - k)
                ctx.fill()
            elif nombre == "polvo":
                x = (x0 + t * 60 * sp) % W
                y = y0 + 10 * math.sin(t + i)
                ctx.arc(x, y, 3 + 3 * sp, 0, 2 * math.pi)
                color(ctx, (0.9, 0.8, 0.6), 0.4)
                ctx.fill()
            elif nombre == "burbujas":
                k = (t * sp * 0.4 + i / n) % 1
                ctx.arc(x0, H - k * H, 8 + 10 * sp, 0, 2 * math.pi)
                relleno_contorno(ctx, None, 3, (1, 1, 1), alpha=0.6 * (1 - k))
    elif nombre == "vapor":
        for i in range(10):
            k = (t * 0.3 + i / 10) % 1
            x = W * (0.2 + 0.6 * r.random()) + 40 * math.sin(t + i)
            curva(ctx, (x, H * 0.75 - k * 500), (x - 30, H * 0.72 - k * 500), (x, H * 0.69 - k * 500), 10,
                  (1, 1, 1), 0.5 * (1 - k))
    elif nombre == "calor":
        ctx.save()
        pat = cairo.LinearGradient(0, 0, 0, H)
        pat.add_color_stop_rgba(0, 1, 0.55, 0.1, 0.22)
        pat.add_color_stop_rgba(0.6, 1, 0.55, 0.1, 0.0)
        ctx.set_source(pat)
        ctx.paint()
        ctx.restore()
        for i in range(8):
            y = H * 0.55 + i * 40
            curva(ctx, (0, y + 10 * math.sin(t * 4 + i)), (W / 2, y - 14), (W, y + 10 * math.cos(t * 4 + i)),
                  3, (1, 1, 1), 0.12)
    elif nombre == "escarcha":
        ctx.save()
        for rr, a in ((W * 1.05, 0.0), (W * 0.75, 0.35)):
            pass
        pat = cairo.RadialGradient(W / 2, H / 2, W * 0.45, W / 2, H / 2, W * 1.15)
        pat.add_color_stop_rgba(0, 0.85, 0.95, 1, 0)
        pat.add_color_stop_rgba(1, 0.85, 0.95, 1, 0.75)
        ctx.set_source(pat)
        ctx.paint()
        ctx.restore()
    elif nombre == "velocidad":
        for i in range(26):
            y = r.uniform(0, H)
            x = (r.uniform(0, W) - t * 3000) % (W + 600) - 300
            linea(ctx, [(x, y), (x + r.uniform(120, 300), y)], r.uniform(3, 8), (1, 1, 1), 0.5)
    elif nombre == "impacto":
        k = clamp(t / 0.25)
        if k < 1:
            for i in range(16):
                a = i * math.pi / 8
                r0, r1 = 120 + 300 * k, 200 + 420 * k
                linea(ctx, [(W / 2 + math.cos(a) * r0, H * 0.45 + math.sin(a) * r0),
                            (W / 2 + math.cos(a) * r1, H * 0.45 + math.sin(a) * r1)], 10, (1, 1, 1), 1 - k)
    elif nombre == "destello":
        k = clamp(t / 0.2)
        if k < 1:
            color(ctx, (1, 1, 1), 0.85 * (1 - k))
            ctx.paint()
    elif nombre == "oscuro":
        color(ctx, (0.02, 0.02, 0.08), 0.45)
        ctx.paint()


def vineta(ctx, fuerza=0.38):
    pat = cairo.RadialGradient(W / 2, H * 0.48, W * 0.5, W / 2, H * 0.48, H * 0.78)
    pat.add_color_stop_rgba(0, 0, 0, 0, 0)
    pat.add_color_stop_rgba(1, 0, 0, 0, fuerza)
    ctx.set_source(pat)
    ctx.paint()


# --- Subtítulos ----------------------------------------------------------------------------
NUM_PAL = {"uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
           "once", "doce", "trece", "catorce", "quince", "veinte", "treinta", "cuarenta", "cincuenta",
           "cien", "mil", "medianoche", "mediodía", "cero", "media", "menos"}


_NUM_A_DIG = {"uno": "1", "una": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5", "seis": "6",
              "siete": "7", "ocho": "8", "nueve": "9", "diez": "10", "cien": "100", "mil": "1000"}
_UNIDADES = {"m": "metros", "km": "kilometros", "kg": "kilos", "t": "toneladas", "h": "horas",
             "min": "minutos", "s": "segundos", "°c": "grados", "%": "por ciento"}


def _norm(w):
    import unicodedata
    w = unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode()
    w = re.sub(r"[^a-z0-9°%]", "", w)
    return _NUM_A_DIG.get(w, w)


def palabras_en_pantalla(ins):
    """Palabras que ya muestra un inserto (recuadro, ficha, contador): no se repiten en subtítulos."""
    if not ins:
        return set()
    textos = [ins.get(k, "") for k in ("texto", "etiqueta", "titulo", "subtitulo", "izq", "der")]
    for f in ins.get("filas") or []:
        textos += [str(x) for x in f]
    for it in ins.get("items") or []:
        textos += [str(it.get("etiqueta", "")), str(it.get("valor", "")), str(it.get("unidad", ""))]
    for c in ins.get("capas") or []:
        textos.append(str(c.get("etiqueta", "")))
    if ins.get("tipo") in ("contador", "regla", "termometro", "manometro"):
        a = ins.get("a")
        if a is not None:
            textos.append(str(int(a)) if float(a).is_integer() else str(a))
        textos.append(ins.get("unidad", ""))
    toks = set()
    for t in textos:
        for w in re.split(r"[\s·/,()]+", str(t)):
            n = _norm(w)
            if n:
                toks.add(n)
                if n in _UNIDADES:
                    toks.add(_norm(_UNIDADES[n]))
    return toks


def quitar_palabras_en_pantalla(palabras, ins):
    """Filtra [(texto, t0, t1)] quitando las palabras que ya aparecen en el inserto del plano."""
    toks = palabras_en_pantalla(ins)
    if not toks:
        return palabras
    fuera = [_norm(w[0]) in toks for w in palabras]
    # conectores que quedarían colgando junto a una palabra quitada ("de [342 metros]", "con [ocho]")
    conectores = {"de", "del", "con", "el", "la", "los", "las", "y", "a", "en", "un", "una"}
    for i, w in enumerate(palabras):
        if not fuera[i] and _norm(w[0]) in conectores and i + 1 < len(palabras) and fuera[i + 1]:
            fuera[i] = True
    return [w for i, w in enumerate(palabras) if not fuera[i]]


def agrupar_palabras(palabras, maxp=None):
    """palabras: [(texto, t0, t1)] -> grupos de 1-3 palabras que se muestran juntos."""
    maxp = maxp or ESTILO["subtitulo_max_palabras"]
    grupos, act = [], []
    for w in palabras:
        act.append(w)
        corta = sum(len(x[0]) for x in act)
        fin_frase = w[0].rstrip()[-1:] in ".,?!:;"
        if len(act) >= maxp or fin_frase or (len(act) >= 2 and corta > 13):
            grupos.append(act)
            act = []
    if act:
        grupos.append(act)
    return [(" ".join(x[0] for x in g), g[0][1], g[-1][2]) for g in grupos]


def dibujar_subtitulo(ctx, txt, t_desde_inicio, destacar=()):
    k = ease_out_back(clamp(t_desde_inicio / 0.12), 2.2)
    escala = 0.78 + 0.22 * k
    y = H * ESTILO["subtitulo_y"]
    tam = ESTILO["subtitulo_tamano"]
    palabras = txt.split()
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.scale(escala, escala)
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    fuente = "Inter Black"
    ctx.select_font_face(fuente, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)
    esp = ctx.text_extents(" ").x_advance + 14
    anchos = [ctx.text_extents(p).x_advance for p in palabras]
    total = sum(anchos) + esp * (len(palabras) - 1)
    if total > W * 0.86:
        f = W * 0.86 / total
        ctx.scale(f, f)
    x = -total / 2
    amarillo = hex2rgb(ESTILO["color_destacado"])
    dest = {d.lower() for d in destacar}
    for p, w in zip(palabras, anchos):
        limpia = re.sub(r"[^\wáéíóúñü°−-]", "", p.lower())
        es_dest = bool(re.search(r"\d", p)) or limpia in NUM_PAL or limpia in dest
        ctx.new_path()
        ctx.move_to(x + 6, 10 + 8)
        ctx.text_path(p)
        color(ctx, (0, 0, 0), 0.45)
        ctx.fill()
        ctx.new_path()
        ctx.move_to(x, 10)
        ctx.text_path(p)
        color(ctx, NEGRO)
        ctx.set_line_width(16)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
        color(ctx, amarillo if es_dest else (1, 1, 1))
        ctx.fill()
        x += w + esp
    ctx.restore()
