"""Escenarios 2.5D: cielo, cerros low-poly, suelo en perspectiva y props con
sombreado cel (luz desde arriba-izquierda). Cada capa tiene profundidad para
que la cámara genere parallax."""
import math
import random

import cairo

from .dibujo import (NEGRO, hex2rgb, mezcla, oscurecer, aclarar, color, relleno_contorno,
                     rect_redondo, elipse, linea, curva, sombra_suelo, poligono, gradiente_v)

W, H = 1080, 1920
HORIZONTE = 0.50     # fracción de H
LW = 5               # contorno de props (más fino que personajes, como en el original)

HORAS = {
    "dia":       dict(cielo=("#5FA8E8", "#CFE8F7"), tinte=None, sol=True),
    "atardecer": dict(cielo=("#5A4E8C", "#F6A66B"), tinte=("#FF9A5A", 0.10), sol=True),
    "amanecer":  dict(cielo=("#7DA0D6", "#FBD3A6"), tinte=("#FFC08A", 0.06), sol=True),
    "noche":     dict(cielo=("#0E1233", "#3A3D7A"), tinte=("#1B1F55", 0.42), sol=False),
    "nublado":   dict(cielo=("#8C9AAB", "#D5DBE2"), tinte=("#6E7B8C", 0.12), sol=False),
}

LUGARES = {
    "campo":    dict(suelo=("#9DBE5C", "#6E9440"), cerros=("#7FA6B8", "#5E8C7A"), detalle="pasto"),
    "huerto":   dict(suelo=("#B79A6A", "#8E7148"), cerros=("#7FA6B8", "#6A9A6E"), detalle="tierra"),
    "playa":    dict(suelo=("#F1DDA6", "#E2C384"), cerros=("#8DB5C8", "#77A88C"), detalle="arena", mar=True),
    "sabana":   dict(suelo=("#D9B866", "#B8933F"), cerros=("#C7A88A", "#A88A60"), detalle="pasto_seco"),
    "desierto": dict(suelo=("#E8C48A", "#CFA066"), cerros=("#D8A27A", "#BF8458"), detalle="arena"),
    "nieve":    dict(suelo=("#F4F7FB", "#CBD8E6"), cerros=("#A8BCD6", "#8EA6C6"), detalle="nieve"),
    "hielo":    dict(suelo=("#E3F0FA", "#B8D4EA"), cerros=("#C9DDF0", "#A9C7E3"), detalle="grietas"),
    "pueblo":   dict(suelo=("#C9B48E", "#A68F68"), cerros=("#8FA9BC", "#7A9A86"), detalle="tierra", casas=True),
    "ciudad":   dict(suelo=("#9A938A", "#77706A"), cerros=None, detalle="adoquin", edificios=True),
    "mar":      dict(suelo=("#3D8FC4", "#21649A"), cerros=("#9DB9CC", "#88A9BF"), detalle="olas"),
    "interior": dict(suelo=("#A87A4E", "#7E5634"), cerros=None, detalle="tablas", pared=True),
}


def _rnd(*k):
    return random.Random(hash(k) & 0xFFFFFFFF)


# --- Cielo ----------------------------------------------------------------------------
def dibujar_cielo(ctx, hora, t, semilla=0):
    h = HORAS.get(hora, HORAS["dia"])
    c0, c1 = hex2rgb(h["cielo"][0]), hex2rgb(h["cielo"][1])
    gradiente_v(ctx, -W, -H * 0.6, W * 3, H * 1.25, c0, c1)
    hy = H * HORIZONTE
    if hora == "noche":
        r = _rnd("estrellas", semilla)
        for _ in range(170):
            x, y = r.uniform(-W, 2 * W), r.uniform(-H * 0.6, hy - 40)
            tw = 0.55 + 0.45 * math.sin(t * r.uniform(1, 3) + r.uniform(0, 6))
            ctx.arc(x, y, r.uniform(1.2, 3.2), 0, 2 * math.pi)
            color(ctx, (1, 1, 0.92), tw)
            ctx.fill()
        # vía láctea suave
        pat = cairo.LinearGradient(-W, -200, 2 * W, hy)
        pat.add_color_stop_rgba(0, 0.8, 0.7, 1, 0)
        pat.add_color_stop_rgba(0.5, 0.8, 0.7, 1, 0.10)
        pat.add_color_stop_rgba(1, 0.8, 0.7, 1, 0)
        ctx.set_source(pat)
        ctx.rectangle(-W, -H * 0.6, 3 * W, hy + H * 0.6)
        ctx.fill()
        ctx.arc(W * 0.78, H * 0.12, 54, 0, 2 * math.pi)
        color(ctx, (1, 0.98, 0.86))
        ctx.fill()
        ctx.arc(W * 0.78 + 22, H * 0.12 - 10, 50, 0, 2 * math.pi)
        color(ctx, c0)
        ctx.fill()
    elif h["sol"]:
        sx, sy = W * 0.22, H * (0.1 if hora == "dia" else 0.36)
        for k, a in ((150, 0.10), (100, 0.18)):
            ctx.arc(sx, sy, k, 0, 2 * math.pi)
            color(ctx, (1, 0.97, 0.8), a)
            ctx.fill()
        ctx.arc(sx, sy, 62, 0, 2 * math.pi)
        color(ctx, (1, 0.97, 0.82) if hora == "dia" else (1, 0.8, 0.5))
        ctx.fill()
    # nubes infladas (estilo "3D" con sombra inferior)
    if hora != "noche":
        r = _rnd("nubes", semilla)
        for i in range(5):
            x = (r.uniform(-W, 2 * W) + t * r.uniform(6, 14)) % (3 * W) - W
            y = r.uniform(-H * 0.2, hy * 0.55)
            s = r.uniform(0.6, 1.2)
            _nube(ctx, x, y, s)


def _nube(ctx, x, y, s):
    bolas = [(-70, 10, 48), (-20, -20, 62), (40, -8, 54), (85, 14, 40), (10, 18, 50)]
    for dx, dy, rr in bolas:
        ctx.arc(x + dx * s, y + dy * s + 8 * s, rr * s, 0, 2 * math.pi)
        color(ctx, (0.75, 0.8, 0.92))
        ctx.fill()
    for dx, dy, rr in bolas:
        ctx.arc(x + dx * s, y + dy * s, rr * s, 0, 2 * math.pi)
        color(ctx, (1, 1, 1))
        ctx.fill()


# --- Cerros low-poly --------------------------------------------------------------------
def dibujar_lejos(ctx, lugar, hora, t, semilla=0):
    L = LUGARES.get(lugar, LUGARES["campo"])
    hy = H * HORIZONTE
    if L.get("pared"):
        return
    if L.get("edificios"):
        r = _rnd("edif", semilla)
        x = -W
        while x < 2 * W:
            w_ = r.uniform(140, 260)
            h_ = r.uniform(260, 520)
            c = hex2rgb(r.choice(["#B5654A", "#A8836A", "#C29A6B", "#8E6E5C", "#B07B5F"]))
            ctx.rectangle(x, hy - h_, w_, h_ + 4)
            relleno_contorno(ctx, c, LW)
            ctx.rectangle(x + w_ * 0.65, hy - h_, w_ * 0.35, h_ + 4)
            color(ctx, (0, 0, 0), 0.12)
            ctx.fill()
            for fy in range(int(hy - h_ + 40), int(hy - 60), 90):
                for fx in (x + 30, x + w_ - 70):
                    rect_redondo(ctx, fx, fy, 40, 56, 6)
                    relleno_contorno(ctx, (0.22, 0.24, 0.3) if hora != "noche" else (1, 0.85, 0.45), 4)
            poligono(ctx, [(x - 10, hy - h_), (x + w_ / 2, hy - h_ - 70), (x + w_ + 10, hy - h_)])
            relleno_contorno(ctx, (0.45, 0.25, 0.2), LW)
            x += w_ + r.uniform(0, 20)
        return
    if not L.get("cerros"):
        return
    for capa, (base, alto, n) in enumerate(((0.0, 260, 9), (0.0, 170, 13))):
        r = _rnd("cerro", semilla, capa)
        c = hex2rgb(L["cerros"][capa])
        pts = [(-W * 1.2, hy + 10)]
        for i in range(n + 1):
            x = -W * 1.2 + i * (W * 3.4 / n)
            pts.append((x, hy - r.uniform(alto * 0.35, alto)))
        pts.append((W * 2.2, hy + 10))
        poligono(ctx, pts)
        color(ctx, c)
        ctx.fill()
        # facetas low-poly: cada triángulo alterna luz/sombra
        for i in range(1, len(pts) - 2):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            mid = ((x0 + x1) / 2, hy + 10)
            poligono(ctx, [(x0, y0), (x1, y1), mid])
            color(ctx, aclarar(c, 0.12) if y1 < y0 else oscurecer(c, 0.10), 0.85)
            ctx.fill()
    if L.get("mar"):
        _mar(ctx, hy - 30, hy + 120, t)
    if L.get("casas"):
        r = _rnd("casas", semilla)
        for i in range(7):
            x = -W * 0.6 + i * 330 + r.uniform(-60, 60)
            dibujar_prop(ctx, "casa", x, hy + 20, 0.45, t, {"color": r.choice(["#E7D3B0", "#D9A779", "#F0E6D2"])})


def _mar(ctx, y0, y1, t):
    gradiente_v(ctx, -W * 1.2, y0, W * 3.4, y1 - y0 + 10, hex2rgb("#2F86C6"), hex2rgb("#5FB4DE"))
    for k in range(6):
        y = y0 + 12 + k * (y1 - y0) / 6
        ctx.new_path()
        for i in range(0, 60):
            x = -W * 1.2 + i * 60
            yy = y + 4 * math.sin(i * 0.9 + t * 2 + k)
            if i == 0:
                ctx.move_to(x, yy)
            else:
                ctx.line_to(x, yy)
        color(ctx, (1, 1, 1), 0.35)
        ctx.set_line_width(3)
        ctx.stroke()


def bruma(ctx, hora):
    """Perspectiva atmosférica: los cerros se lavan hacia el color del horizonte."""
    c = hex2rgb(HORAS.get(hora, HORAS["dia"])["cielo"][1])
    hy = H * HORIZONTE
    pat = cairo.LinearGradient(0, hy - 320, 0, hy + 10)
    pat.add_color_stop_rgba(0, c[0], c[1], c[2], 0)
    pat.add_color_stop_rgba(1, c[0], c[1], c[2], 0.55)
    ctx.set_source(pat)
    ctx.rectangle(-W * 1.2, hy - 320, W * 3.4, 340)
    ctx.fill()


# --- Suelo en perspectiva ---------------------------------------------------------
def dibujar_suelo(ctx, lugar, t, semilla=0, mar_sube=0.0):
    L = LUGARES.get(lugar, LUGARES["campo"])
    hy = H * HORIZONTE
    if L.get("pared"):
        gradiente_v(ctx, -W, -H * 0.6, W * 3, hy + H * 0.6, hex2rgb("#C79A63"), hex2rgb("#A97B48"))
        for i in range(-10, 30):
            linea(ctx, [(i * 110, -H * 0.6), (i * 110, hy)], 4, (0.45, 0.3, 0.18), 0.6)
    c0, c1 = hex2rgb(L["suelo"][0]), hex2rgb(L["suelo"][1])
    gradiente_v(ctx, -W * 1.2, hy, W * 3.4, H * 1.2, c0, c1)
    hz = hex2rgb(HORAS["dia"]["cielo"][1])
    pat = cairo.LinearGradient(0, hy, 0, hy + 220)
    pat.add_color_stop_rgba(0, hz[0], hz[1], hz[2], 0.35)
    pat.add_color_stop_rgba(1, hz[0], hz[1], hz[2], 0)
    ctx.set_source(pat)
    ctx.rectangle(-W * 1.2, hy, W * 3.4, 220)
    ctx.fill()
    if L.get("mar") and mar_sube > 0:
        _mar(ctx, hy + 110, hy + 110 + mar_sube * (H * 0.4), t)
    r = _rnd("suelo", lugar, semilla)
    det = L["detalle"]
    for _ in range(220):
        # más densidad y tamaño cerca de la cámara
        v = r.random() ** 0.7
        y = hy + 20 + v * (H * 0.62)
        x = r.uniform(-W * 1.1, W * 2.1)
        s = 0.3 + v * 1.2
        if det in ("pasto", "pasto_seco"):
            col = oscurecer(c1, 0.25) if det == "pasto" else hex2rgb("#A2802F")
            for k in (-1, 0, 1):
                linea(ctx, [(x + k * 6 * s, y), (x + k * 14 * s, y - 26 * s)], 3.5 * s, col)
        elif det in ("tierra", "arena"):
            elipse(ctx, x, y, 10 * s, 4 * s)
            color(ctx, oscurecer(c1, 0.18), 0.6)
            ctx.fill()
        elif det == "nieve":
            elipse(ctx, x, y, 22 * s, 6 * s)
            color(ctx, (1, 1, 1), 0.8)
            ctx.fill()
        elif det == "grietas":
            linea(ctx, [(x, y), (x + 30 * s, y + 6 * s), (x + 50 * s, y + 2 * s)], 2.5 * s, (0.6, 0.75, 0.88))
        elif det == "olas":
            curva(ctx, (x, y), (x + 20 * s, y - 10 * s), (x + 40 * s, y), 3 * s, (1, 1, 1), 0.6)
        elif det == "adoquin":
            rect_redondo(ctx, x, y, 40 * s, 18 * s, 4 * s)
            color(ctx, oscurecer(c1, 0.15), 0.5)
            ctx.fill()
        elif det == "tablas":
            linea(ctx, [(-W, y), (2 * W, y)], 2 * s, oscurecer(c1, 0.3), 0.3)
    if det in ("pasto", "tierra", "arena", "pasto_seco", "nieve"):
        for _ in range(28):
            v = r.random() ** 0.6
            y = hy + 40 + v * H * 0.6
            x = r.uniform(-W, W * 2)
            s = 0.4 + v
            elipse(ctx, x, y, 16 * s, 9 * s)
            relleno_contorno(ctx, mezcla(c1, (0.5, 0.5, 0.55), 0.5), 3 * s)


# --- Props ---------------------------------------------------------------------------
def _copa_cel(ctx, x, y, rads, c):
    """Copa de árbol low-poly: bolas con lado iluminado y lado en sombra."""
    for dx, dy, rr in rads:
        ctx.arc(x + dx, y + dy, rr, 0, 2 * math.pi)
        relleno_contorno(ctx, c, LW)
    for dx, dy, rr in rads:
        ctx.arc(x + dx, y + dy, rr - LW / 2, 0, 2 * math.pi)
        color(ctx, c)
        ctx.fill()
    for dx, dy, rr in rads:
        ctx.save()
        ctx.arc(x + dx, y + dy, rr - 3, 0, 2 * math.pi)
        ctx.clip()
        ctx.arc(x + dx + rr * 0.45, y + dy + rr * 0.45, rr * 0.95, 0, 2 * math.pi)
        color(ctx, oscurecer(c, 0.22))
        ctx.fill()
        ctx.arc(x + dx - rr * 0.35, y + dy - rr * 0.4, rr * 0.35, 0, 2 * math.pi)
        color(ctx, aclarar(c, 0.22))
        ctx.fill()
        ctx.restore()


def dibujar_prop(ctx, tipo, x, y, s=1.0, t=0.0, prm=None):
    prm = prm or {}
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    c = hex2rgb(prm.get("color"), None)
    if tipo not in ("cerca", "mar", "humo"):
        sombra_suelo(ctx, 0, 0, 120, 26, 0.22)
    if tipo in ("arbol", "arbol_fruta", "pino", "arbusto"):
        if tipo == "pino":
            for k in range(3):
                poligono(ctx, [(-110 + k * 22, -120 - k * 110), (0, -330 - k * 110), (110 - k * 22, -120 - k * 110)])
                relleno_contorno(ctx, c or hex2rgb("#3E7D52"), LW)
            ctx.rectangle(-16, -125, 32, 125)
            relleno_contorno(ctx, hex2rgb("#7A5236"), LW)
        elif tipo == "arbusto":
            _copa_cel(ctx, 0, -50, [(-50, 0, 52), (20, -20, 60), (60, 10, 44)], c or hex2rgb("#5E9A45"))
        else:
            tronco = hex2rgb(prm.get("color_tronco"), hex2rgb("#7A5236"))
            if prm.get("pintado"):
                tronco = (0.96, 0.96, 0.94)
            poligono(ctx, [(-20, 0), (20, 0), (13, -230), (-13, -230)])
            relleno_contorno(ctx, tronco, LW)
            linea(ctx, [(0, -170), (-55, -250)], 13, tronco)
            linea(ctx, [(0, -150), (60, -240)], 13, tronco)
            _copa_cel(ctx, 0, -330, [(-95, 20, 85), (0, -40, 110), (95, 10, 90), (0, 50, 90)],
                      c or hex2rgb("#6FA64A"))
            if tipo == "arbol_fruta":
                fc = hex2rgb(prm.get("fruta"), hex2rgb("#F28C28"))
                r = _rnd("fruta", x)
                for _ in range(16):
                    a, d = r.uniform(0, 2 * math.pi), r.uniform(20, 150)
                    fx, fy = math.cos(a) * d, -330 + math.sin(a) * d * 0.7
                    ctx.arc(fx, fy, 15, 0, 2 * math.pi)
                    relleno_contorno(ctx, fc, 4)
                    if prm.get("hielo"):
                        ctx.arc(fx, fy, 22, 0, 2 * math.pi)
                        color(ctx, (0.85, 0.95, 1), 0.55)
                        ctx.fill()
    elif tipo == "palmera":
        ctx.new_path()
        ctx.move_to(-14, 0)
        ctx.curve_to(-10, -200, 30, -330, 40, -460)
        ctx.line_to(64, -460)
        ctx.curve_to(50, -330, 14, -200, 14, 0)
        ctx.close_path()
        relleno_contorno(ctx, hex2rgb("#9C7A4E"), LW)
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.55
            ex, ey = 52 + math.cos(a) * 190, -460 + math.sin(a) * 90 + 60
            ctx.new_path()
            ctx.move_to(52, -460)
            ctx.curve_to(52 + math.cos(a) * 80, -520, ex, ey - 40, ex, ey)
            ctx.curve_to(ex - 20, ey - 50, 52 + math.cos(a) * 60, -490, 52, -455)
            relleno_contorno(ctx, hex2rgb("#4E9A52"), LW)
    elif tipo == "acacia":
        tr = hex2rgb("#6B4A30")
        linea(ctx, [(0, 0), (-10, -200), (-90, -330)], 18, tr)
        linea(ctx, [(-10, -200), (70, -340)], 16, tr)
        elipse(ctx, -10, -350, 230, 55)
        relleno_contorno(ctx, hex2rgb("#7BA040"), LW)
        elipse(ctx, -30, -360, 160, 30)
        color(ctx, aclarar(hex2rgb("#7BA040"), 0.15))
        ctx.fill()
    elif tipo in ("granero", "casa"):
        cc = c or (hex2rgb("#B5402F") if tipo == "granero" else hex2rgb("#E7D3B0"))
        w_, h_ = (420, 300) if tipo == "granero" else (300, 220)
        ctx.rectangle(-w_ / 2, -h_, w_, h_)
        relleno_contorno(ctx, cc, LW)
        ctx.rectangle(w_ / 2 - w_ * 0.3, -h_, w_ * 0.3, h_)
        color(ctx, (0, 0, 0), 0.14)
        ctx.fill()
        techo = hex2rgb("#5A3A2E") if tipo == "granero" else hex2rgb("#B05A3C")
        poligono(ctx, [(-w_ / 2 - 30, -h_), (0, -h_ - (170 if tipo == "granero" else 140)), (w_ / 2 + 30, -h_)])
        relleno_contorno(ctx, techo, LW)
        if tipo == "granero":
            rect_redondo(ctx, -80, -190, 160, 190, 4)
            relleno_contorno(ctx, oscurecer(cc, 0.3), LW)
            linea(ctx, [(-80, -190), (80, 0)], 6, (1, 1, 1))
            linea(ctx, [(80, -190), (-80, 0)], 6, (1, 1, 1))
            if prm.get("vapor"):
                _humo(ctx, 0, -h_ - 170, t, gris=0.9)
        else:
            rect_redondo(ctx, -40, -130, 80, 130, 4)
            relleno_contorno(ctx, hex2rgb("#7A5236"), LW)
            rect_redondo(ctx, 70, -160, 60, 60, 4)
            relleno_contorno(ctx, hex2rgb("#9CC7E6"), LW)
    elif tipo == "cerca":
        largo = prm.get("largo", 900)
        cc = c or hex2rgb("#A07850")
        for i in range(int(largo // 120) + 1):
            rect_redondo(ctx, -largo / 2 + i * 120 - 9, -110, 18, 110, 4)
            relleno_contorno(ctx, cc, 4)
        for yy in (-85, -45):
            rect_redondo(ctx, -largo / 2, yy, largo, 14, 4)
            relleno_contorno(ctx, aclarar(cc, 0.1), 4)
    elif tipo == "fogata":
        apagada = prm.get("apagada", False)
        for k, a in enumerate((-0.5, 0.5, 0)):
            ctx.save()
            ctx.rotate(a)
            rect_redondo(ctx, -80, -18 - k * 4, 160, 26, 12)
            relleno_contorno(ctx, hex2rgb("#7A4E2E"), LW)
            ctx.restore()
        if not apagada:
            for k in range(3):
                f = 1 + 0.12 * math.sin(t * 13 + k * 2)
                hh = (150 - k * 40) * f
                ww = (70 - k * 18)
                ctx.new_path()
                ctx.move_to(-ww, -10)
                ctx.curve_to(-ww, -hh * 0.5, -ww * 0.2, -hh * 0.6, 8 * math.sin(t * 9 + k), -hh)
                ctx.curve_to(ww * 0.2, -hh * 0.6, ww, -hh * 0.5, ww, -10)
                ctx.close_path()
                color(ctx, [(0.95, 0.35, 0.1), (1, 0.62, 0.12), (1, 0.9, 0.45)][k])
                ctx.fill()
            for i in range(5):
                k = (t * 0.8 + i * 0.2) % 1
                ctx.arc(30 * math.sin(i * 3 + t), -150 - k * 260, 5 * (1 - k), 0, 2 * math.pi)
                color(ctx, (1, 0.7, 0.2), 1 - k)
                ctx.fill()
        else:
            _humo(ctx, 0, -40, t, gris=0.55)
    elif tipo == "roca":
        poligono(ctx, [(-90, 0), (-70, -70), (-10, -100), (60, -80), (95, 0)])
        relleno_contorno(ctx, c or hex2rgb("#8C8A86"), LW)
        poligono(ctx, [(-10, -100), (60, -80), (95, 0), (10, 0)])
        color(ctx, (0, 0, 0), 0.14)
        ctx.fill()
    elif tipo == "fardos":
        cc = hex2rgb("#E8C35A")
        for fila in range(prm.get("filas", 3)):
            for col_ in range(3 - (fila > 1)):
                x0 = -190 + col_ * 128 + fila * 30
                y0 = -82 - fila * 82
                ctx.rectangle(x0, y0, 124, 80)
                relleno_contorno(ctx, cc, LW)
                for k in (0.3, 0.7):
                    linea(ctx, [(x0 + 124 * k, y0), (x0 + 124 * k, y0 + 80)], 4, hex2rgb("#C0392B"))
                ctx.rectangle(x0 + 90, y0, 34, 80)
                color(ctx, (0, 0, 0), 0.12)
                ctx.fill()
        if prm.get("humo"):
            _humo(ctx, 0, -280, t, gris=0.85)
    elif tipo in ("camioneta", "auto"):
        cc = c or hex2rgb("#3E6FB0")
        hund = prm.get("hundida", 0) * 40
        ctx.translate(0, hund)
        rect_redondo(ctx, -230, -170, 460, 110, 22)
        relleno_contorno(ctx, cc, LW)
        rect_redondo(ctx, -60, -260, 200, 100, 22)
        relleno_contorno(ctx, cc, LW)
        rect_redondo(ctx, -40, -245, 75, 70, 10)
        relleno_contorno(ctx, hex2rgb("#BFE0F2"), 4)
        rect_redondo(ctx, 50, -245, 75, 70, 10)
        relleno_contorno(ctx, hex2rgb("#BFE0F2"), 4)
        for wx in (-140, 150):
            plana = prm.get("llantas_bajas", False)
            elipse(ctx, wx, -50, 62 if not plana else 72, 58 if not plana else 46)
            relleno_contorno(ctx, (0.15, 0.15, 0.17), LW)
            ctx.arc(wx, -50 + (6 if plana else 0), 24, 0, 2 * math.pi)
            relleno_contorno(ctx, (0.7, 0.7, 0.72), 4)
        if hund:
            gradiente_v(ctx, -280, -20, 560, 60, hex2rgb("#E8CF94"), hex2rgb("#D9B97A"))
    elif tipo == "carreta":
        rect_redondo(ctx, -170, -170, 340, 90, 8)
        relleno_contorno(ctx, hex2rgb("#9C6B3E"), LW)
        for wx in (-100, 100):
            ctx.arc(wx, -60, 58, 0, 2 * math.pi)
            relleno_contorno(ctx, hex2rgb("#6B4A30"), LW)
            for k in range(6):
                a = k * math.pi / 3 + t * prm.get("giro", 0)
                linea(ctx, [(wx, -60), (wx + math.cos(a) * 52, -60 + math.sin(a) * 52)], 4)
        if prm.get("carga") == "leña":
            for i in range(5):
                ctx.arc(-120 + i * 60, -190, 28, 0, 2 * math.pi)
                relleno_contorno(ctx, hex2rgb("#B98A5A"), 4)
    elif tipo == "estanque":
        elipse(ctx, 0, -10, 230, 60)
        relleno_contorno(ctx, hex2rgb("#4E8FC0"), LW)
        elipse(ctx, -40, -20, 120, 22)
        color(ctx, (1, 1, 1), 0.25)
        ctx.fill()
    elif tipo == "barco":
        mec = math.sin(t * 1.4) * 0.03
        ctx.rotate(mec)
        ctx.new_path()
        ctx.move_to(-300, -140)
        ctx.curve_to(-250, 10, 250, 10, 300, -140)
        ctx.close_path()
        relleno_contorno(ctx, c or hex2rgb("#6B4A30"), LW)
        linea(ctx, [(0, -140), (0, -560)], 12, hex2rgb("#5A3A22"))
        poligono(ctx, [(10, -540), (200, -200), (10, -200)])
        relleno_contorno(ctx, (0.96, 0.94, 0.88), LW)
    elif tipo == "lata_leche":
        rect_redondo(ctx, -50, -170, 100, 170, 16)
        relleno_contorno(ctx, hex2rgb("#C9CED6"), LW)
        rect_redondo(ctx, -32, -205, 64, 40, 10)
        relleno_contorno(ctx, hex2rgb("#AEB4BE"), LW)
        if prm.get("vendada"):
            ctx.save()
            rect_redondo(ctx, -50, -170, 100, 170, 16)
            ctx.clip()
            for k in range(9):
                yy = -165 + k * 20
                poligono(ctx, [(-60, yy), (60, yy - 10), (60, yy + 8), (-60, yy + 18)])
                relleno_contorno(ctx, (0.93, 0.93, 0.88), 3)
            ctx.restore()
            for i in range(3):
                k = (t * 0.5 + i / 3) % 1
                curva(ctx, (-20 + i * 20, -180 - k * 140), (-35 + i * 20, -200 - k * 140),
                      (-20 + i * 20, -225 - k * 140), 5, (1, 1, 1), 0.7 * (1 - k))
        else:
            ctx.rectangle(10, -170, 40, 170)
            color(ctx, (0, 0, 0), 0.10)
            ctx.fill()
    elif tipo == "torre_agua":
        for sx in (-1, 1):
            linea(ctx, [(sx * 70, 0), (sx * 50, -320)], 10, hex2rgb("#8A6A48"))
        rect_redondo(ctx, -100, -470, 200, 160, 20)
        relleno_contorno(ctx, hex2rgb("#B9A894"), LW)
        poligono(ctx, [(-110, -470), (0, -540), (110, -470)])
        relleno_contorno(ctx, hex2rgb("#8C7B68"), LW)
    elif tipo == "bomba_agua":
        rect_redondo(ctx, -30, -220, 60, 220, 10)
        relleno_contorno(ctx, hex2rgb("#3C4E5E"), LW)
        if not prm.get("sin_manija"):
            linea(ctx, [(20, -190), (130, -230)], 12)
        linea(ctx, [(-30, -150), (-90, -140)], 18, hex2rgb("#3C4E5E"))
    elif tipo == "puesto":
        rect_redondo(ctx, -180, -150, 360, 150, 6)
        relleno_contorno(ctx, hex2rgb("#B98A5A"), LW)
        for i in range(6):
            poligono(ctx, [(-200 + i * 66, -330), (-134 + i * 66, -330), (-134 + i * 66, -290), (-200 + i * 66, -290)])
            relleno_contorno(ctx, (0.95, 0.3, 0.25) if i % 2 else (1, 1, 1), 4)
        for sx in (-1, 1):
            linea(ctx, [(sx * 180, -150), (sx * 180, -290)], 8)
    elif tipo == "pasto_alto":
        r = _rnd("pastoalto", x)
        for i in range(40):
            xx = r.uniform(-260, 260)
            hh = r.uniform(120, 230)
            curva(ctx, (xx, 0), (xx + r.uniform(-20, 20), -hh / 2), (xx + r.uniform(-40, 40) + 8 * math.sin(t * 2 + i), -hh),
                  7, hex2rgb(prm.get("color", "#C8A24A")))
    elif tipo == "vaca":
        cc = c or hex2rgb("#8B5A3C")
        ctx.scale(prm.get("mira", 1), 1)
        for lx in (-110, -60, 70, 110):
            linea(ctx, [(lx, -110), (lx, 0)], 14, cc)
        rect_redondo(ctx, -160, -250, 300, 150, 60)
        relleno_contorno(ctx, cc, LW)
        elipse(ctx, -40, -190, 50, 35)
        color(ctx, (1, 1, 1))
        ctx.fill()
        rect_redondo(ctx, 110, -330, 110, 120, 40)
        relleno_contorno(ctx, cc, LW)
        elipse(ctx, 170, -230, 50, 30)
        relleno_contorno(ctx, hex2rgb("#F1B6A6"), LW)
        ctx.arc(150, -290, 8, 0, 2 * math.pi)
        color(ctx, NEGRO)
        ctx.fill()
        if prm.get("ojos_traseros"):
            for ex in (-150, -150):
                pass
            for dy in (-215, -160):
                elipse(ctx, -140, dy, 22, 18)
                relleno_contorno(ctx, (1, 1, 1), 4)
                ctx.arc(-138, dy, 9, 0, 2 * math.pi)
                color(ctx, (0.9, 0.65, 0.1))
                ctx.fill()
    elif tipo == "cañon":
        rect_redondo(ctx, -40, -150, 230, 60, 28)
        relleno_contorno(ctx, hex2rgb("#3A3A3E"), LW)
        ctx.arc(0, -70, 60, 0, 2 * math.pi)
        relleno_contorno(ctx, hex2rgb("#7A5236"), LW)
    elif tipo == "muro":
        largo = prm.get("largo", 700)
        cc = c or hex2rgb("#B79A6A")
        ctx.rectangle(-largo / 2, -220, largo, 220)
        relleno_contorno(ctx, cc, LW)
        for i in range(int(largo // 60)):
            linea(ctx, [(-largo / 2 + i * 60, -220), (-largo / 2 + i * 60, 0)], 3, oscurecer(cc, 0.3))
    elif tipo == "bandera":
        linea(ctx, [(0, 0), (0, -420)], 8)
        ctx.new_path()
        ctx.move_to(0, -420)
        for i in range(11):
            ctx.line_to(i * 16, -420 + 8 * math.sin(i * 0.8 + t * 6))
        for i in range(10, -1, -1):
            ctx.line_to(i * 16, -320 + 8 * math.sin(i * 0.8 + t * 6))
        ctx.close_path()
        relleno_contorno(ctx, c or hex2rgb("#2F5DA8"), 4)
    elif tipo == "poste":
        linea(ctx, [(0, 0), (0, -380)], 14, hex2rgb("#6B4A30"))
        linea(ctx, [(-60, -350), (60, -350)], 10, hex2rgb("#6B4A30"))
    elif tipo == "humo":
        _humo(ctx, 0, 0, t, gris=prm.get("gris", 0.7))
    ctx.restore()


def _humo(ctx, x, y, t, gris=0.7, n=7):
    for i in range(n):
        k = (t * 0.35 + i / n) % 1
        rr = 22 + k * 60
        ctx.arc(x + 30 * math.sin(i * 1.7 + t * 0.8) + k * 40, y - k * 380, rr, 0, 2 * math.pi)
        color(ctx, (gris, gris, gris + 0.05), 0.55 * (1 - k))
        ctx.fill()


def capa_luz(ctx, hora, fuentes, t):
    """Tinte de hora del día + resplandor aditivo de fuegos/faroles (coordenadas pantalla)."""
    h = HORAS.get(hora, HORAS["dia"])
    if h["tinte"]:
        c, a = hex2rgb(h["tinte"][0]), h["tinte"][1]
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_MULTIPLY)
        color(ctx, mezcla((1, 1, 1), c, min(1, a * 2.2)))
        ctx.paint()
        ctx.restore()
    if fuentes:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        for (x, y, r, intens) in fuentes:
            f = 1 + 0.06 * math.sin(t * 11 + x)
            pat = cairo.RadialGradient(x, y, 0, x, y, r * f)
            pat.add_color_stop_rgba(0, 1, 0.55, 0.2, 0.55 * intens)
            pat.add_color_stop_rgba(0.5, 1, 0.45, 0.15, 0.18 * intens)
            pat.add_color_stop_rgba(1, 1, 0.4, 0.1, 0)
            ctx.set_source(pat)
            ctx.paint()
        ctx.restore()


import json as _json
import os as _os
_CAT = _json.load(open(_os.path.join(_os.path.dirname(__file__), "escena3d", "catalogo.json"), encoding="utf-8"))
PROPS_MODELO = sorted(_CAT["props"])
PROPS = PROPS_MODELO + ["arbol_fruta", "granero", "fardos", "camioneta", "lata_leche", "torre_agua", "bomba_agua",
         "puesto", "pasto_alto", "vaca", "cañon", "muro", "bandera", "poste", "humo", "fogata", "cerca", "estanque", "fresal", "fresa_grande", "canasta",
         "barco", "carreta", "acacia"]
_PROPS_2D = ["arbol", "arbol_fruta", "pino", "arbusto", "palmera", "acacia", "granero", "casa",
         "cerca", "fogata", "roca", "fardos", "camioneta", "auto", "carreta", "estanque", "barco",
         "lata_leche", "torre_agua", "bomba_agua", "puesto", "pasto_alto", "vaca", "cañon",
         "muro", "bandera", "poste", "humo"]
