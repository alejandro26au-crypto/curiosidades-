"""Personajes procedurales: cabeza blanca redonda, contorno negro grueso,
cuerpo de palito con torso de ropa, accesorios que los diferencian.

Coordenadas locales: origen en los pies, y crece hacia abajo (cairo),
así que el cuerpo vive en y negativas. Escala 1 = personaje en plano medio
a 1080 px de ancho.
"""
import math

import cairo

from .dibujo import (NEGRO, BLANCO_CARA, hex2rgb, oscurecer, aclarar, color,
                     relleno_contorno, rect_redondo, elipse, linea, curva,
                     sombra_suelo, poligono)

R = 100            # radio de la cabeza
LW = 7             # contorno
LW_MIEMBRO = 9     # grosor de brazos y piernas
CABEZA_Y = -560
HOMBRO_Y = -440
CADERA_Y = -272
LARGO_BRAZO = 88
LARGO_PIERNA = 136

EXPRESIONES = ["neutral", "confiado", "burla", "asombro", "preocupado", "enojado",
               "feliz", "triste", "determinado", "panico", "presumido", "dormido"]
POSES = ["idle", "manos_cadera", "brazos_cruzados", "señalar", "saludar", "sorpresa",
         "trabajar", "reir", "pensar", "cargar", "caminar", "correr", "agachado",
         "temblar", "rascarse", "celebrar", "empujar", "sentado"]
SOMBREROS = ["ninguno", "gorra", "vaquero", "boina", "gorro_lana", "paja", "casco",
             "capitan", "pañuelo", "copa", "militar"]
PEINADOS = ["ninguno", "calvo_lados", "flequillo", "moño", "canas", "rizos"]
ROPAS = ["camisa", "overol", "hawaiana", "chaleco", "abrigo", "vestido", "uniforme", "bata"]
ACCESORIOS = ["bufanda", "lentes", "lentes_sol", "mochila", "tirantes", "corbata", "delantal"]
OBJETOS = ["balde", "martillo", "brocha", "reloj", "fosforo", "barra", "lata",
           "termometro", "trapo", "farol", "carton", "rama", "pala", "libreta", "pez"]


# --- Poses -----------------------------------------------------------------------
def _pose(nombre, t, mira):
    """Devuelve ángulos de brazos/piernas (rad, desde abajo, + = hacia afuera),
    desplazamiento vertical y temblor."""
    s = math.sin
    p = {
        "bi": (0.16, -0.08), "bd": (0.16, -0.08),     # brazo izq/der: hombro, codo
        "pi": (0.06, 0.0), "pd": (0.06, 0.0),         # pierna izq/der: cadera, rodilla
        "bob": 2.5 * s(t * 2.2), "lean": 0.0, "agache": 0.0, "temblor": 0.0,
        "cruzados": False, "sentado": False,
    }
    frente = "bd" if mira > 0 else "bi"
    atras = "bi" if mira > 0 else "bd"
    if nombre == "manos_cadera":
        p["bi"] = p["bd"] = (0.95, -2.3)
    elif nombre == "brazos_cruzados":
        p["cruzados"] = True
    elif nombre == "señalar":
        p[frente] = (1.62, 0.0)
        p[atras] = (0.95, -2.3)
    elif nombre == "saludar":
        p[frente] = (2.5, 0.35 * s(t * 12))
    elif nombre == "sorpresa":
        p["bi"] = p["bd"] = (2.35, 0.45)
        p["bob"] = -6 + 3 * s(t * 20)
    elif nombre == "trabajar":
        p[frente] = (1.15 + 0.55 * s(t * 9), -0.9 + 0.3 * s(t * 9))
        p[atras] = (0.8, -1.4)
        p["bob"] = 4 * abs(s(t * 9))
    elif nombre == "reir":
        p["bi"] = p["bd"] = (0.7, -2.5)
        p["bob"] = 7 * abs(s(t * 14))
        p["lean"] = -0.04 * mira
    elif nombre == "pensar":
        p[frente] = (0.55, -2.65)
        p[atras] = (0.75, -2.35)
    elif nombre == "cargar":
        p["bi"] = p["bd"] = (1.05, -0.65)
    elif nombre in ("caminar", "correr"):
        v, a = (7.0, 0.32) if nombre == "caminar" else (13.0, 0.6)
        f = s(t * v)
        p["pi"] = (0.05 + a * f, 0.0)
        p["pd"] = (0.05 - a * f, 0.0)
        p["bi"] = (0.25 - a * 0.8 * f, -0.3)
        p["bd"] = (0.25 + a * 0.8 * f, -0.3)
        p["bob"] = (6 if nombre == "caminar" else 12) * abs(math.cos(t * v))
        p["lean"] = (0.03 if nombre == "caminar" else 0.1) * mira
    elif nombre == "agachado":
        p["agache"] = 80
        p["pi"] = p["pd"] = (0.55, -1.1)
        p[frente] = (1.25, -0.4)
    elif nombre == "temblar":
        p["bi"] = p["bd"] = (0.45, -2.6)
        p["temblor"] = 4.0
    elif nombre == "rascarse":
        p[frente] = (2.45, 2.2)
    elif nombre == "celebrar":
        k = abs(s(t * 9))
        p["bi"] = p["bd"] = (2.5 - 0.3 * k, 0.4)
        p["bob"] = -14 * k
    elif nombre == "empujar":
        p["bi"] = p["bd"] = (1.45, -0.25)
        p["lean"] = 0.18 * mira
        p["pi"], p["pd"] = (0.35, 0), (-0.2, 0)
    elif nombre == "sentado":
        p["sentado"] = True
        p["agache"] = 120
    return p


def _brazo(ctx, x, y, lado, ang, largo):
    h, c = ang
    dx1 = lado * math.sin(h) * largo
    dy1 = math.cos(h) * largo
    codo = (x + dx1, y + dy1)
    a2 = h + c
    mano = (codo[0] + lado * math.sin(a2) * largo, codo[1] + math.cos(a2) * largo)
    linea(ctx, [(x, y), codo, mano], LW_MIEMBRO)
    ctx.arc(mano[0], mano[1], 11, 0, 2 * math.pi)
    color(ctx, NEGRO)
    ctx.fill()
    return mano


def _pierna(ctx, x, y, lado, ang, largo, zapato, flex=0.0):
    h, c = ang
    rod = (x + lado * math.sin(h) * largo, y + math.cos(h) * largo)
    a2 = h + c
    pie = (rod[0] + lado * math.sin(a2) * largo, rod[1] + math.cos(a2) * largo + flex)
    linea(ctx, [(x, y), rod, pie], LW_MIEMBRO)
    elipse(ctx, pie[0] + lado * 9, pie[1] + 2, 23, 12)
    relleno_contorno(ctx, zapato, 5)


# --- Cara -------------------------------------------------------------------------
def _ojo_abierto(ctx, x, y, rx=9, ry=13):
    elipse(ctx, x, y, rx, ry)
    color(ctx, NEGRO)
    ctx.fill()


def _cara(ctx, exp, fx, t, hablando, semilla):
    ey = -6
    ox = 31
    parpadeo = ((t + semilla * 0.37) % 3.4) < 0.11
    boca_abierta = hablando and (math.sin(t * 26 + semilla) > -0.1)
    lw = 6

    def cejas(ang_i, ang_d, alto=-40, largo=24):
        for sx, a in ((-1, ang_i), (1, ang_d)):
            cx = fx + sx * ox
            dx = math.cos(a) * largo
            dy = math.sin(a) * largo * sx
            linea(ctx, [(cx - dx, ey + alto - dy), (cx + dx, ey + alto + dy)], lw + 1)

    def boca_d(ancho=34, alto=26, dientes=True):
        y0 = 30
        ctx.new_path()
        ctx.move_to(fx - ancho, y0)
        ctx.curve_to(fx - ancho * 0.8, y0 + alto * 1.4, fx + ancho * 0.8, y0 + alto * 1.4, fx + ancho, y0)
        ctx.close_path()
        color(ctx, (0.55, 0.12, 0.15))
        ctx.fill_preserve()
        ctx.save()
        ctx.clip_preserve()
        if dientes:
            color(ctx, (1, 1, 1))
            ctx.rectangle(fx - ancho, y0 - 2, ancho * 2, alto * 0.35)
            ctx.fill()
        ctx.restore()
        color(ctx, NEGRO)
        ctx.set_line_width(lw)
        ctx.stroke()

    def boca_o(r=14):
        elipse(ctx, fx, 42, r * 0.85, r)
        relleno_contorno(ctx, (0.45, 0.1, 0.12), lw)

    def ojos_normales(rx=9, ry=13):
        if parpadeo:
            for sx in (-1, 1):
                linea(ctx, [(fx + sx * ox - 10, ey), (fx + sx * ox + 10, ey)], lw)
        else:
            for sx in (-1, 1):
                _ojo_abierto(ctx, fx + sx * ox, ey, rx, ry)

    if exp == "confiado":
        # párpados a media asta + ceja levantada + sonrisa ladeada (la cara "sabelotodo")
        for sx in (-1, 1):
            cx = fx + sx * ox
            ctx.new_path()
            ctx.arc(cx, ey - 2, 12, 0, math.pi)
            color(ctx, NEGRO)
            ctx.fill()
            linea(ctx, [(cx - 17, ey - 3), (cx + 17, ey - 3)], lw)
        linea(ctx, [(fx - ox - 20, ey - 30), (fx - ox + 18, ey - 30)], lw + 1)
        curva(ctx, (fx + ox - 18, ey - 34), (fx + ox, ey - 52), (fx + ox + 18, ey - 36), lw + 1)
        if boca_abierta:
            boca_o(10)
        else:
            curva(ctx, (fx - 14, 38), (fx + 4, 50), (fx + 20, 34), lw)
    elif exp in ("burla", "feliz", "reir"):
        for sx in (-1, 1):
            cx = fx + sx * ox
            curva(ctx, (cx - 13, ey + 4), (cx, ey - 14), (cx + 13, ey + 4), lw)
        if exp == "burla" or boca_abierta:
            boca_d(38 if exp == "burla" else 30, 30 if exp == "burla" else 22)
        else:
            curva(ctx, (fx - 26, 30), (fx, 56), (fx + 26, 30), lw)
    elif exp == "asombro":
        for sx in (-1, 1):
            cx = fx + sx * ox
            elipse(ctx, cx, ey, 19, 23)
            relleno_contorno(ctx, (1, 1, 1), 5)
            _ojo_abierto(ctx, cx + fx * 0.25, ey + 2, 7, 9)
        cejas(-0.15, -0.15, -48, 18)
        boca_o(18)
    elif exp == "panico":
        for sx in (-1, 1):
            cx = fx + sx * ox
            elipse(ctx, cx, ey, 21, 25)
            relleno_contorno(ctx, (1, 1, 1), 5)
            _ojo_abierto(ctx, cx, ey, 4, 5)
        cejas(0.35, 0.35, -52, 18)
        boca_d(30, 34, dientes=False)
    elif exp == "preocupado":
        ojos_normales(8, 11)
        cejas(0.35, 0.35, -34, 20)
        ctx.new_path()
        ctx.move_to(fx - 24, 40)
        for i in range(1, 7):
            ctx.line_to(fx - 24 + i * 8, 40 + (5 if i % 2 else -2))
        color(ctx, NEGRO)
        ctx.set_line_width(lw)
        ctx.stroke()
    elif exp == "enojado":
        ojos_normales(9, 10)
        cejas(-0.45, -0.45, -28, 22)
        rect_redondo(ctx, fx - 28, 30, 56, 22, 6)
        relleno_contorno(ctx, (1, 1, 1), lw)
        for i in range(1, 4):
            linea(ctx, [(fx - 28 + i * 14, 31), (fx - 28 + i * 14, 51)], 3)
        linea(ctx, [(fx - 28, 41), (fx + 28, 41)], 3)
    elif exp == "triste":
        ojos_normales(8, 11)
        cejas(0.4, 0.4, -32, 18)
        curva(ctx, (fx - 22, 48), (fx, 30), (fx + 22, 48), lw)
    elif exp == "determinado":
        ojos_normales(9, 11)
        cejas(-0.18, -0.18, -30, 22)
        linea(ctx, [(fx - 18, 40), (fx + 18, 40)], lw)
    elif exp == "presumido":
        for sx in (-1, 1):
            cx = fx + sx * ox
            curva(ctx, (cx - 14, ey - 2), (cx, ey + 10), (cx + 14, ey - 2), lw)
        cejas(-0.1, -0.1, -40, 18)
        curva(ctx, (fx - 26, 32), (fx, 54), (fx + 26, 32), lw)
    elif exp == "dormido":
        for sx in (-1, 1):
            cx = fx + sx * ox
            curva(ctx, (cx - 13, ey), (cx, ey + 9), (cx + 13, ey), lw)
        boca_o(8)
    else:  # neutral
        ojos_normales()
        if boca_abierta:
            boca_o(12)
        else:
            linea(ctx, [(fx - 14, 40), (fx + 14, 40)], lw)

    if hablando and exp in ("neutral", "determinado", "preocupado", "triste", "enojado"):
        # flap de boca simple al hablar
        if boca_abierta:
            elipse(ctx, fx, 44, 10, 7)
            relleno_contorno(ctx, (0.45, 0.1, 0.12), 4)


# --- Cabeza: pelo, sombreros, vello -------------------------------------------------
def _pelo_atras(ctx, spec, fx, mira):
    if spec.get("sombrero") == "pañuelo":
        c = hex2rgb(spec.get("color_sombrero"), (0.55, 0.42, 0.75))
        ctx.new_path()
        ctx.arc(0, 0, R * 1.08, math.pi * 0.75, math.pi * 2.25)
        ctx.line_to(R * 0.6, R * 1.15)
        ctx.line_to(-R * 0.6, R * 1.15)
        ctx.close_path()
        relleno_contorno(ctx, c, LW)
    p = spec.get("peinado", "ninguno")
    cp = hex2rgb(spec.get("color_pelo"), (0.15, 0.12, 0.1))
    if p == "moño":
        ctx.arc(-mira * 30, -R * 0.95, 34, 0, 2 * math.pi)
        relleno_contorno(ctx, cp, LW)
    elif p == "rizos":
        for a in range(0, 360, 30):
            r = math.radians(a)
            if math.sin(r) < 0.35:
                ctx.arc(math.cos(r) * R * 0.98, math.sin(r) * R * 0.98, 26, 0, 2 * math.pi)
                relleno_contorno(ctx, cp, 5)


def _pelo_frente(ctx, spec, fx, mira):
    p = spec.get("peinado", "ninguno")
    cp = hex2rgb(spec.get("color_pelo"), (0.15, 0.12, 0.1))
    if p in ("calvo_lados", "canas"):
        gris = cp if p == "calvo_lados" and spec.get("color_pelo") else (0.55, 0.55, 0.57)
        lado = -mira
        cx = lado * R * 0.9
        ctx.new_path()
        ctx.arc(cx, -10, 26, math.pi * 0.5, math.pi * 1.5)
        color(ctx, gris)
        ctx.fill()
        # oreja
        elipse(ctx, lado * R * 1.0, 8, 16, 22)
        relleno_contorno(ctx, BLANCO_CARA, 5)
    elif p == "flequillo":
        ctx.new_path()
        ctx.move_to(-R * 0.9, -R * 0.42)
        for i in range(7):
            x = -R * 0.9 + i * R * 0.3
            ctx.line_to(x + R * 0.15, -R * 0.68 + (12 if i % 2 else -6))
        ctx.line_to(R * 0.95, -R * 0.4)
        ctx.arc_negative(0, 0, R, -math.pi * 0.13, -math.pi * 0.87)
        relleno_contorno(ctx, cp, 5)


def _sombrero(ctx, spec, mira):
    s = spec.get("sombrero", "ninguno")
    c = hex2rgb(spec.get("color_sombrero"), (0.25, 0.45, 0.35))
    if s == "gorra":
        ctx.new_path()
        ctx.arc(0, -R * 0.08, R * 1.02, math.pi * 1.06, math.pi * 1.94)
        ctx.close_path()
        relleno_contorno(ctx, c, LW)
        ctx.new_path()
        ctx.move_to(mira * R * 0.55, -R * 0.38)
        ctx.curve_to(mira * R * 1.25, -R * 0.42, mira * R * 1.55, -R * 0.3, mira * R * 1.5, -R * 0.2)
        ctx.line_to(mira * R * 0.6, -R * 0.24)
        ctx.close_path()
        relleno_contorno(ctx, oscurecer(c, 0.2), LW)
        ctx.arc(0, -R * 1.08, 10, 0, 2 * math.pi)
        relleno_contorno(ctx, oscurecer(c, 0.2), 4)
    elif s in ("vaquero", "paja"):
        cc = c if s == "vaquero" else hex2rgb(spec.get("color_sombrero"), (0.93, 0.78, 0.38))
        rect_redondo(ctx, -R * 0.62, -R * 1.42, R * 1.24, R * 0.85, 26)
        relleno_contorno(ctx, cc, LW)
        ctx.rectangle(-R * 0.62, -R * 0.78, R * 1.24, R * 0.16)
        color(ctx, oscurecer(cc, 0.35))
        ctx.fill()
        elipse(ctx, 0, -R * 0.58, R * 1.38, R * 0.2)
        relleno_contorno(ctx, aclarar(cc, 0.08), LW)
    elif s == "boina":
        elipse(ctx, mira * 10, -R * 0.78, R * 0.98, R * 0.36)
        relleno_contorno(ctx, c, LW)
        linea(ctx, [(mira * 10, -R * 1.12), (mira * 14, -R * 1.25)], 6)
    elif s == "gorro_lana":
        ctx.new_path()
        ctx.arc(0, -R * 0.2, R * 1.0, math.pi, 2 * math.pi)
        ctx.close_path()
        relleno_contorno(ctx, c, LW)
        rect_redondo(ctx, -R * 1.04, -R * 0.4, R * 2.08, R * 0.3, 14)
        relleno_contorno(ctx, oscurecer(c, 0.15), LW)
        for i in range(-4, 5):
            linea(ctx, [(i * R * 0.22, -R * 0.36), (i * R * 0.22, -R * 0.14)], 3, oscurecer(c, 0.4))
    elif s == "casco":
        ctx.new_path()
        ctx.arc(0, -R * 0.3, R * 0.95, math.pi, 2 * math.pi)
        ctx.close_path()
        relleno_contorno(ctx, hex2rgb(spec.get("color_sombrero"), (0.98, 0.78, 0.15)), LW)
        rect_redondo(ctx, -R * 1.15, -R * 0.38, R * 2.3, R * 0.16, 8)
        relleno_contorno(ctx, hex2rgb(spec.get("color_sombrero"), (0.98, 0.78, 0.15)), LW)
    elif s == "capitan":
        rect_redondo(ctx, -R * 0.85, -R * 1.08, R * 1.7, R * 0.45, 18)
        relleno_contorno(ctx, (0.97, 0.97, 0.97), LW)
        ctx.rectangle(-R * 0.85, -R * 0.72, R * 1.7, R * 0.18)
        relleno_contorno(ctx, hex2rgb(spec.get("color_sombrero"), (0.12, 0.17, 0.32)), LW)
        elipse(ctx, mira * R * 0.55, -R * 0.52, R * 0.5, R * 0.1)
        relleno_contorno(ctx, NEGRO, 0)
        ctx.arc(0, -R * 0.88, 12, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.95, 0.75, 0.2), 4)
    elif s == "pañuelo":
        ctx.save()
        ctx.rectangle(-R * 1.4, -R * 1.4, R * 2.8, R * 0.95)
        ctx.clip()
        ctx.arc(0, 0, R * 1.07, 0, 2 * math.pi)
        relleno_contorno(ctx, c, LW)
        ctx.arc(0, 0, R * 1.0, 0, 2 * math.pi)
        ctx.clip()
        for i in range(-4, 5):
            for j in range(-4, 0):
                ctx.arc(i * 40 + (j % 2) * 20, j * 30, 6, 0, 2 * math.pi)
                color(ctx, aclarar(c, 0.45))
                ctx.fill()
        ctx.restore()
        linea(ctx, [(-R * 1.0, -R * 0.45), (R * 1.0, -R * 0.45)], LW)
    elif s == "copa":
        rect_redondo(ctx, -R * 0.55, -R * 1.75, R * 1.1, R * 1.05, 8)
        relleno_contorno(ctx, c, LW)
        elipse(ctx, 0, -R * 0.7, R * 1.05, R * 0.16)
        relleno_contorno(ctx, c, LW)
    elif s == "militar":
        ctx.new_path()
        ctx.move_to(-R * 1.25, -R * 0.62)
        ctx.curve_to(-R * 0.6, -R * 1.5, R * 0.6, -R * 1.5, R * 1.25, -R * 0.62)
        ctx.curve_to(R * 0.4, -R * 0.82, -R * 0.4, -R * 0.82, -R * 1.25, -R * 0.62)
        relleno_contorno(ctx, c, LW)
        ctx.arc(0, -R * 1.02, 13, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.95, 0.75, 0.2), 4)


def _vello(ctx, spec, fx):
    cp = hex2rgb(spec.get("color_pelo"), (0.15, 0.12, 0.1))
    if spec.get("barba"):
        ctx.new_path()
        ctx.arc(fx * 0.6, 8, R * 0.86, math.pi * 0.08, math.pi * 0.92)
        ctx.arc_negative(fx, 46, 26, math.pi * 0.95, math.pi * 0.05)
        ctx.close_path()
        color(ctx, cp)
        ctx.fill()
    if spec.get("bigote"):
        for sx in (-1, 1):
            ctx.new_path()
            ctx.move_to(fx, 20)
            ctx.curve_to(fx + sx * 16, 10, fx + sx * 40, 16, fx + sx * 44, 36)
            ctx.curve_to(fx + sx * 30, 28, fx + sx * 14, 32, fx, 28)
            ctx.close_path()
            color(ctx, cp)
            ctx.fill()


def _lentes(ctx, spec, fx):
    acc = spec.get("accesorios", [])
    if "lentes_sol" in acc:
        for sx in (-1, 1):
            rect_redondo(ctx, fx + sx * 31 - 22, -24, 44, 30, 10)
            relleno_contorno(ctx, (0.1, 0.1, 0.12), 5)
        linea(ctx, [(fx - 9, -12), (fx + 9, -12)], 5)
    elif "lentes" in acc:
        for sx in (-1, 1):
            ctx.arc(fx + sx * 31, -6, 21, 0, 2 * math.pi)
            relleno_contorno(ctx, None, 5)
        linea(ctx, [(fx - 10, -8), (fx + 10, -8)], 5)


# --- Torso ------------------------------------------------------------------------
def _torso(ctx, spec, mira, t):
    ropa = spec.get("ropa", "camisa")
    c1 = hex2rgb(spec.get("color_ropa"), (0.85, 0.3, 0.25))
    c2 = hex2rgb(spec.get("color_ropa2"), oscurecer(c1, 0.35))
    acc = spec.get("accesorios", [])
    x0, y0, w, h = -60, HOMBRO_Y - 22, 120, (CADERA_Y + 8) - (HOMBRO_Y - 22)
    if ropa in ("abrigo", "bata"):
        h += 36
    if "mochila" in acc:
        rect_redondo(ctx, -mira * 52 - 42, y0 + 20, 84, 120, 22)
        relleno_contorno(ctx, hex2rgb(spec.get("color_mochila"), (0.98, 0.8, 0.2)), LW)
    if ropa == "vestido":
        poligono(ctx, [(-50, y0), (50, y0), (88, CADERA_Y + 70), (-88, CADERA_Y + 70)])
        relleno_contorno(ctx, c1, LW)
        return
    rect_redondo(ctx, x0, y0, w, h, 44)
    relleno_contorno(ctx, c1, LW)
    ctx.save()
    rect_redondo(ctx, x0, y0, w, h, 44)
    ctx.clip()
    if ropa == "overol":
        ctx.rectangle(x0, y0 + h * 0.52, w, h)
        color(ctx, c2)
        ctx.fill()
        rect_redondo(ctx, -32, y0 + h * 0.3, 64, h * 0.4, 8)
        color(ctx, c2)
        ctx.fill()
        linea(ctx, [(-32, y0 + h * 0.3), (-24, y0)], 12, c2)
        linea(ctx, [(32, y0 + h * 0.3), (24, y0)], 12, c2)
        for sx in (-1, 1):
            ctx.arc(sx * 24, y0 + h * 0.34, 6, 0, 2 * math.pi)
            color(ctx, (0.95, 0.8, 0.3))
            ctx.fill()
    elif ropa == "hawaiana":
        import random
        rnd = random.Random(7)
        for _ in range(16):
            fx_, fy_ = rnd.uniform(x0, x0 + w), rnd.uniform(y0, y0 + h)
            for k in range(5):
                a = k * 2 * math.pi / 5
                ctx.arc(fx_ + math.cos(a) * 8, fy_ + math.sin(a) * 8, 6, 0, 2 * math.pi)
                color(ctx, (0.98, 0.85, 0.7))
                ctx.fill()
            ctx.arc(fx_, fy_, 4, 0, 2 * math.pi)
            color(ctx, (0.95, 0.75, 0.2))
            ctx.fill()
            elipse(ctx, fx_ + 14, fy_ + 10, 8, 4)
            color(ctx, (0.2, 0.5, 0.3))
            ctx.fill()
    elif ropa == "chaleco":
        poligono(ctx, [(-60, y0), (-12, y0), (-6, y0 + h), (-60, y0 + h)])
        color(ctx, c2)
        ctx.fill()
        poligono(ctx, [(60, y0), (12, y0), (6, y0 + h), (60, y0 + h)])
        color(ctx, c2)
        ctx.fill()
    elif ropa in ("abrigo", "uniforme", "bata"):
        linea(ctx, [(0, y0 + 10), (0, y0 + h)], 4, oscurecer(c1, 0.4))
        for i in range(4):
            ctx.arc(10 * mira, y0 + 30 + i * 36, 5, 0, 2 * math.pi)
            color(ctx, (0.95, 0.8, 0.3) if ropa == "uniforme" else oscurecer(c1, 0.5))
            ctx.fill()
        if ropa == "uniforme":
            ctx.rectangle(x0, y0 + h * 0.72, w, 12)
            color(ctx, (0.95, 0.85, 0.5))
            ctx.fill()
    # sombreado cel lateral
    ctx.rectangle(-mira * 60 - 26, y0, 52, h)
    color(ctx, (0.1, 0.05, 0.2), 0.16)
    ctx.fill()
    ctx.restore()
    if "tirantes" in acc:
        for sx in (-1, 1):
            linea(ctx, [(sx * 30, y0 + 4), (sx * 26, y0 + h - 6)], 10, hex2rgb(spec.get("color_tirantes"), (0.95, 0.75, 0.15)))
    if "delantal" in acc:
        rect_redondo(ctx, -42, y0 + 30, 84, h - 10, 12)
        relleno_contorno(ctx, (0.97, 0.97, 0.95), 5)
    if "corbata" in acc:
        poligono(ctx, [(-8, y0 + 4), (8, y0 + 4), (12, y0 + 80), (0, y0 + 96), (-12, y0 + 80)])
        relleno_contorno(ctx, hex2rgb(spec.get("color_corbata"), (0.75, 0.15, 0.2)), 4)
    if "bufanda" in acc:
        cb = hex2rgb(spec.get("color_bufanda"), (0.98, 0.8, 0.2))
        rect_redondo(ctx, -50, y0 - 14, 100, 34, 16)
        relleno_contorno(ctx, cb, 5)
        rect_redondo(ctx, mira * 18 - 15, y0 + 8, 30, 92, 10)
        relleno_contorno(ctx, cb, 5)
        for i in range(3):
            linea(ctx, [(mira * 18 - 13, y0 + 30 + i * 22), (mira * 18 + 13, y0 + 30 + i * 22)], 6, oscurecer(cb, 0.45))


# --- Objetos en mano -----------------------------------------------------------------
def dibujar_objeto(ctx, nombre, x, y, mira, t=0.0, escala=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(escala * mira, escala)
    if nombre == "balde":
        poligono(ctx, [(-34, 0), (34, 0), (26, 62), (-26, 62)])
        relleno_contorno(ctx, (0.62, 0.66, 0.7), 6)
        curva(ctx, (-34, 0), (0, -40), (34, 0), 5)
        elipse(ctx, 0, 2, 32, 8)
        relleno_contorno(ctx, (0.35, 0.6, 0.85), 4)
    elif nombre == "martillo":
        linea(ctx, [(0, 10), (0, -80)], 12, (0.55, 0.36, 0.2))
        rect_redondo(ctx, -30, -100, 60, 26, 6)
        relleno_contorno(ctx, (0.45, 0.47, 0.5), 6)
    elif nombre == "brocha":
        linea(ctx, [(0, 10), (0, -60)], 12, (0.6, 0.4, 0.22))
        rect_redondo(ctx, -18, -96, 36, 40, 6)
        relleno_contorno(ctx, (0.97, 0.97, 0.95), 6)
    elif nombre == "reloj":
        ctx.arc(14, 0, 26, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.92, 0.75, 0.25), 6)
        ctx.arc(14, 0, 18, 0, 2 * math.pi)
        relleno_contorno(ctx, (1, 1, 0.96), 3)
        a = t * 3
        linea(ctx, [(14, 0), (14 + math.sin(a) * 14, -math.cos(a) * 14)], 3)
    elif nombre == "fosforo":
        linea(ctx, [(0, 0), (0, -60)], 7, (0.9, 0.78, 0.55))
        ctx.arc(0, -64, 8, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.8, 0.15, 0.1), 3)
        f = 1 + 0.15 * math.sin(t * 30)
        elipse(ctx, 0, -84, 11 * f, 20 * f)
        color(ctx, (1, 0.62, 0.1), 0.95)
        ctx.fill()
        elipse(ctx, 0, -80, 5, 10)
        color(ctx, (1, 0.95, 0.6))
        ctx.fill()
    elif nombre == "barra":
        linea(ctx, [(0, 60), (0, -150)], 11, (0.35, 0.36, 0.4))
    elif nombre == "lata":
        rect_redondo(ctx, -24, -10, 48, 64, 6)
        relleno_contorno(ctx, (0.75, 0.77, 0.8), 6)
        linea(ctx, [(-24, 6), (24, 6)], 3)
    elif nombre == "termometro":
        rect_redondo(ctx, -10, -96, 20, 100, 10)
        relleno_contorno(ctx, (1, 1, 1), 5)
        ctx.arc(0, 6, 16, 0, 2 * math.pi)
        relleno_contorno(ctx, (0.9, 0.15, 0.15), 5)
        linea(ctx, [(0, 0), (0, -60)], 6, (0.9, 0.15, 0.15))
    elif nombre == "trapo":
        ctx.new_path()
        ctx.move_to(-10, 0)
        ctx.curve_to(-30, 30, 20, 40, 0, 80 + 6 * math.sin(t * 6))
        ctx.line_to(30, 70)
        ctx.curve_to(40, 30, 20, 10, 20, 0)
        ctx.close_path()
        relleno_contorno(ctx, (0.93, 0.93, 0.88), 5)
        for i in range(3):
            ctx.arc(10 + i * 4, 90 + i * 14 + (t * 160 % 40), 4, 0, 2 * math.pi)
            color(ctx, (0.4, 0.7, 1), 0.8)
            ctx.fill()
    elif nombre == "farol":
        rect_redondo(ctx, -22, -20, 44, 60, 10)
        relleno_contorno(ctx, (0.98, 0.9, 0.6), 6)
        curva(ctx, (-14, -20), (0, -44), (14, -20), 5)
    elif nombre == "carton":
        rect_redondo(ctx, -10, -70, 110, 80, 4)
        relleno_contorno(ctx, (0.8, 0.65, 0.45), 6)
    elif nombre == "rama":
        linea(ctx, [(0, 0), (40, -50)], 7, (0.45, 0.3, 0.15))
        linea(ctx, [(25, -30), (45, -26)], 5, (0.45, 0.3, 0.15))
    elif nombre == "pala":
        linea(ctx, [(0, 30), (0, -110)], 10, (0.6, 0.42, 0.22))
        poligono(ctx, [(-22, 30), (22, 30), (16, 80), (0, 92), (-16, 80)])
        relleno_contorno(ctx, (0.6, 0.62, 0.66), 6)
    elif nombre == "libreta":
        rect_redondo(ctx, -6, -60, 64, 80, 6)
        relleno_contorno(ctx, (0.98, 0.96, 0.88), 6)
        for i in range(4):
            linea(ctx, [(4, -44 + i * 16), (48, -44 + i * 16)], 3, (0.5, 0.6, 0.8))
    elif nombre == "pez":
        elipse(ctx, 20, 0, 40, 18)
        relleno_contorno(ctx, (0.55, 0.7, 0.85), 6)
        poligono(ctx, [(60, 0), (84, -18), (84, 18)])
        relleno_contorno(ctx, (0.55, 0.7, 0.85), 6)
    ctx.restore()


# --- Personaje completo ------------------------------------------------------------
def dibujar_personaje(ctx, spec, x, y, escala=1.0, mira=1, expresion="neutral",
                      pose="idle", t=0.0, hablando=False, objeto=None, semilla=0,
                      sudor=False, sombra=True, alpha=1.0):
    mira = 1 if mira >= 0 else -1
    p = _pose(pose, t + semilla * 0.7, mira)
    if alpha < 1.0:
        ctx.push_group()
    if sombra:
        sombra_suelo(ctx, x, y, 95 * escala, 22 * escala)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(escala, escala)
    tx = p["temblor"] * math.sin(t * 70) if p["temblor"] else 0
    ctx.translate(tx, 0)
    zapato = hex2rgb(spec.get("color_zapatos"), (0.2, 0.18, 0.16))

    agache = p["agache"]
    # piernas
    if p["sentado"]:
        rect_redondo(ctx, -70 - mira * 10, CADERA_Y + agache + 4, 140, -CADERA_Y - agache - 4, 6)
        relleno_contorno(ctx, (0.62, 0.45, 0.28), LW)
        for lado in (-1, 1):
            linea(ctx, [(lado * 18, CADERA_Y + agache), (lado * 18 + mira * 90, CADERA_Y + agache + 6),
                        (lado * 18 + mira * 96, -6)], LW_MIEMBRO)
    else:
        largo = LARGO_PIERNA - agache / 2.6
        _pierna(ctx, -18, CADERA_Y + agache + p["bob"] * 0.2, -1, p["pi"], -CADERA_Y / 2 - agache / 2, zapato)
        _pierna(ctx, 18, CADERA_Y + agache + p["bob"] * 0.2, 1, p["pd"], -CADERA_Y / 2 - agache / 2, zapato)

    ctx.translate(0, agache - p["bob"])
    ctx.rotate(p["lean"])

    # brazo de atrás detrás del torso si cruzados
    _torso(ctx, spec, mira, t)
    # cuello
    linea(ctx, [(0, HOMBRO_Y - 22), (0, CABEZA_Y + R * 0.9)], LW_MIEMBRO)

    manos = {}
    if p["cruzados"]:
        y0 = HOMBRO_Y + 70
        linea(ctx, [(-52, HOMBRO_Y), (-60, y0), (40, y0 - 6)], LW_MIEMBRO)
        linea(ctx, [(52, HOMBRO_Y), (60, y0 + 10), (-40, y0 + 4)], LW_MIEMBRO)
        manos["bi"] = (-40, y0)
        manos["bd"] = (40, y0)
    else:
        manos["bi"] = _brazo(ctx, -54, HOMBRO_Y, -1, p["bi"], LARGO_BRAZO)
        manos["bd"] = _brazo(ctx, 54, HOMBRO_Y, 1, p["bd"], LARGO_BRAZO)

    if objeto:
        mano = manos["bd"] if mira > 0 else manos["bi"]
        dibujar_objeto(ctx, objeto, mano[0], mano[1], mira, t)

    # cabeza
    ctx.save()
    ctx.translate(0, CABEZA_Y)
    inclin = 0.05 * math.sin(t * 1.3 + semilla) if pose == "idle" else 0
    if expresion in ("presumido",):
        inclin -= 0.08 * mira
    ctx.rotate(inclin)
    fx = mira * 16
    _pelo_atras(ctx, spec, fx, mira)
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    relleno_contorno(ctx, hex2rgb(spec.get("color_piel"), BLANCO_CARA), LW)
    # sombreado suave de la cabeza (volumen)
    ctx.save()
    ctx.arc(0, 0, R - LW / 2, 0, 2 * math.pi)
    ctx.clip()
    ctx.arc(-mira * R * 0.35, -R * 0.25, R * 1.05, 0, 2 * math.pi)
    ctx.rectangle(-R * 2, -R * 2, R * 4, R * 4)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    color(ctx, (0.55, 0.5, 0.6), 0.12)
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.restore()
    _pelo_frente(ctx, spec, fx, mira)
    _vello(ctx, spec, fx)
    _cara(ctx, expresion, fx, t, hablando, semilla)
    _lentes(ctx, spec, fx)
    _sombrero(ctx, spec, mira)
    if sudor or expresion in ("panico", "preocupado"):
        k = (t * 0.9 + semilla) % 1.0
        sx = -mira * R * 0.8
        sy = -R * 0.3 + k * 50
        ctx.new_path()
        ctx.move_to(sx, sy - 22)
        ctx.curve_to(sx + 14, sy, sx + 12, sy + 14, sx, sy + 14)
        ctx.curve_to(sx - 12, sy + 14, sx - 14, sy, sx, sy - 22)
        relleno_contorno(ctx, (0.55, 0.8, 1.0), 4, alpha=1 - k * 0.6)
    ctx.restore()
    ctx.restore()
    if alpha < 1.0:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)
