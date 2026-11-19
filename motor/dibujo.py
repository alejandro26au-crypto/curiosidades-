"""Utilidades de dibujo vectorial con cairo."""
import math
import random

import cairo

NEGRO = (0.07, 0.07, 0.08)
BLANCO_CARA = (0.985, 0.98, 0.965)


def hex2rgb(h, default=(0.5, 0.5, 0.5)):
    if h is None:
        return default
    if isinstance(h, (tuple, list)):
        return tuple(h[:3])
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return default


def mezcla(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def oscurecer(c, f=0.25):
    return mezcla(c, (0, 0, 0), f)


def aclarar(c, f=0.25):
    return mezcla(c, (1, 1, 1), f)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


# --- Easing -----------------------------------------------------------------
def ease_in_out(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.70158):
    t = clamp(t)
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def ruido1d(x, semilla=0):
    """Ruido suave determinista (value noise) en [-1, 1]."""
    i = math.floor(x)
    f = x - i

    def h(n):
        r = random.Random(n * 7919 + semilla * 104729)
        return r.uniform(-1, 1)

    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


# --- Primitivas ---------------------------------------------------------------
def color(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)


def relleno_contorno(ctx, fill, lw=7, stroke=NEGRO, alpha=1.0):
    if fill is not None:
        color(ctx, fill, alpha)
        if lw:
            ctx.fill_preserve()
        else:
            ctx.fill()
            return
    if lw:
        color(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    else:
        ctx.new_path()


def rect_redondo(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def elipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def linea(ctx, pts, lw, c=NEGRO, alpha=1.0):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    color(ctx, c, alpha)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def curva(ctx, p0, p1, p2, lw, c=NEGRO, alpha=1.0):
    """Curva cuadrática p0 -> p2 con control p1."""
    ctx.new_path()
    ctx.move_to(*p0)
    c1 = (p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1]))
    c2 = (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1]))
    ctx.curve_to(*c1, *c2, *p2)
    color(ctx, c, alpha)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def sombra_suelo(ctx, cx, cy, rx, ry, alpha=0.28):
    ctx.save()
    pat = cairo.RadialGradient(cx, cy, 0, cx, cy, rx)
    pat.add_color_stop_rgba(0, 0, 0, 0, alpha)
    pat.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.translate(cx, cy)
    ctx.scale(1, ry / rx)
    ctx.translate(-cx, -cy)
    ctx.set_source(pat)
    ctx.arc(cx, cy, rx, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def poligono(ctx, pts):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def gradiente_v(ctx, x, y, w, h, c0, c1):
    pat = cairo.LinearGradient(0, y, 0, y + h)
    pat.add_color_stop_rgb(0, *c0)
    pat.add_color_stop_rgb(1, *c1)
    ctx.set_source(pat)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


def texto(ctx, s, x, y, tam, fuente="Inter", peso=cairo.FONT_WEIGHT_BOLD,
          relleno=(1, 1, 1), trazo=NEGRO, grosor=0, centro=True, alpha=1.0):
    ctx.save()
    ctx.select_font_face(fuente, cairo.FONT_SLANT_NORMAL, peso)
    ctx.set_font_size(tam)
    ext = ctx.text_extents(s)
    tx = x - (ext.width / 2 + ext.x_bearing) if centro else x
    ty = y - (ext.height / 2 + ext.y_bearing) if centro else y
    ctx.new_path()
    ctx.move_to(tx, ty)
    ctx.text_path(s)
    if grosor:
        color(ctx, trazo, alpha)
        ctx.set_line_width(grosor)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    color(ctx, relleno, alpha)
    ctx.fill()
    ctx.restore()
    return ext
