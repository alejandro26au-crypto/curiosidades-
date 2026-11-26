"""Convierte un guion JSON (storyboard) en un MP4 vertical 1080x1920.

Fondo: escenario 3D low-poly (three.js en Chromium headless, motor/escena3d).
Encima: personajes 2D (cairo) proyectados sobre el suelo 3D, insertos de datos,
efectos y subtítulos palabra por palabra. Audio: voz + música + SFX."""
import base64
import io
import json
import math
import os
import subprocess
import sys
import time

import cairo
import numpy as np
from PIL import Image, ImageFilter

from . import audio, camara3d, efectos
from .dibujo import clamp, ease_in_out
from .formula import ESTILO
from .personajes import dibujar_personaje

W, H = 1080, 1920
FPS = ESTILO["fps"]
SUELO_FRENTE = 0.86
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TINTE_PERSONAJES = {"noche": ((0.16, 0.2, 0.5), 0.42), "atardecer": ((0.95, 0.55, 0.35), 0.16),
                    "amanecer": ((1.0, 0.75, 0.55), 0.10), "nublado": ((0.5, 0.55, 0.62), 0.12)}


# --- estado de actores -----------------------------------------------------------------------
def _x_actor(a, p):
    x = float(a.get("x", 0.5))
    acc = a.get("accion")
    k = ease_in_out(clamp(p / 0.6))
    caminando = False
    if acc == "entrar_izq":
        x, caminando = -0.35 + (x + 0.35) * k, k < 1
    elif acc == "entrar_der":
        x, caminando = 1.35 + (x - 1.35) * k, k < 1
    elif acc in ("salir_izq", "salir_der"):
        dst = -0.45 if acc == "salir_izq" else 1.45
        k2 = ease_in_out(clamp((p - 0.3) / 0.7))
        x, caminando = x + (dst - x) * k2, 0 < k2 < 1
    elif acc == "mover":
        x2 = float(a.get("x2", x))
        x, caminando = x + (x2 - x) * ease_in_out(p), 0 < p < 1
    return x, caminando


def _foco(plano, p):
    cam = plano.get("camara", {})
    enc = cam.get("encuadre", "medio")
    f = cam.get("foco")
    actores = {a["id"]: a for a in plano.get("actores", [])}
    alt = camara3d.ALTURA_FOCO.get(enc, 1.05)
    if isinstance(f, str) and f in actores:
        a = actores[f]
        x, _ = _x_actor(a, p)
        X, _, Z = camara3d.actor_mundo(x, float(a.get("y", SUELO_FRENTE)))
        return (X, alt * float(a.get("escala", 1)), Z)
    if isinstance(f, (list, tuple)) and len(f) == 2:
        return camara3d.foco_lista(f)
    if actores:
        pts = []
        for a in actores.values():
            x, _ = _x_actor(a, p)
            pts.append(camara3d.actor_mundo(x, float(a.get("y", SUELO_FRENTE))))
        return (sum(q[0] for q in pts) / len(pts), alt, sum(q[2] for q in pts) / len(pts))
    return (0.0, 1.0, -1.0)


# --- planificación ------------------------------------------------------------------------------
def planificar(guion, sin_voz=False, carpeta="salida/tmp"):
    """Genera la voz y calcula inicio/fin de cada plano a partir de los tiempos de palabra."""
    planos = guion["planos"]
    personajes = guion.get("personajes", {})
    voz_narr = guion.get("voz_narrador", ESTILO["voz_narrador"])
    segs = []
    for pl in planos:
        quien = pl.get("voz", "narrador")
        spec = personajes.get(quien, {}) if quien != "narrador" else {}
        seg = {"texto": pl["texto"].strip(), "voz": spec.get("voz", voz_narr),
               "velocidad": spec.get("velocidad", guion.get("velocidad_voz", ESTILO["velocidad_voz"])),
               "tono": spec.get("tono", "+0Hz")}
        if pl.get("pausa") is not None:  # silencio tras la frase (remates, impactos)
            seg["pausa"] = float(pl["pausa"])
        segs.append(seg)
    if sin_voz:
        voz, tiempos = audio.estimar(segs)
    else:
        try:
            voz, tiempos = audio.sintetizar(segs, carpeta)
        except Exception as e:  # sin red: render igual con tiempos estimados
            print(f"[voz] no se pudo sintetizar ({e.__class__.__name__}: {e}); uso tiempos estimados", file=sys.stderr)
            voz, tiempos = audio.estimar(segs)
    inicios = []
    for i, ps in enumerate(tiempos):
        inicios.append(0.0 if i == 0 else max(0.0, ps[0][1] - 0.06) if ps else inicios[-1] + 1.5)
    fin_total = len(voz) / audio.SR + float(guion.get("cola", 0.35))
    for i, pl in enumerate(planos):
        pl["_i"], pl["_t0"] = i, inicios[i]
        pl["_t1"] = inicios[i + 1] if i + 1 < len(planos) else fin_total
    subs = []
    for i, ps in enumerate(tiempos):
        for txt, a, b in efectos.agrupar_palabras([tuple(x) for x in ps]):
            subs.append((a, b, txt, i))
    return voz, subs, fin_total


def _escenas3d(planos):
    escenas = []
    for pl in planos:
        f = json.loads(json.dumps(pl.get("fondo", {})))
        for pr in f.get("props", []):
            pr["_pos"], pr["_escala"] = camara3d.prop_mundo(pr)
        escenas.append(f)
    return escenas


# --- composición 2D sobre el fondo 3D ----------------------------------------------------------
def _fondo_bgra(b64, blur, ancho, alto):
    im = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
    if im.size != (ancho, alto):
        im = im.resize((ancho, alto))
    if blur > 0.3:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    rgb = np.asarray(im, dtype=np.uint8)
    bgra = np.empty((alto, ancho, 4), dtype=np.uint8)
    bgra[..., 0], bgra[..., 1], bgra[..., 2], bgra[..., 3] = rgb[..., 2], rgb[..., 1], rgb[..., 0], 255
    return bgra


def componer(ctx, guion, pl, tp, dur, cam, sub, t_abs, escala):
    p = clamp(tp / max(dur, 1e-3))
    fondo = pl.get("fondo", {})
    hora = fondo.get("hora", "dia")
    personajes = guion.get("personajes", {})
    ctx.save()
    ctx.scale(escala, escala)
    fuentes = []
    for pr in fondo.get("props", []):
        if pr.get("tipo") == "fogata" and not pr.get("apagada"):
            pos, esc = camara3d.prop_mundo(pr)
            q = camara3d.proyectar(cam, (pos[0], 0.8 * esc, pos[2]))
            if q:
                fuentes.append((q[0], q[1], 2600 / q[2] * esc, 0.8 if hora == "noche" else 0.35))
    actores = []
    for a in pl.get("actores", []):
        x, caminando = _x_actor(a, p)
        q = camara3d.proyectar(cam, camara3d.actor_mundo(x, float(a.get("y", SUELO_FRENTE))))
        if q:
            actores.append((q[2], q, a, caminando))
    actores.sort(key=lambda z: -z[0])
    ctx.push_group()
    for prof, q, a, caminando in actores:
        spec = personajes.get(a["id"], {})
        s = camara3d.escala_personaje(cam, prof) * float(a.get("escala", 1))
        mira = 1 if a.get("mira", "der") in ("der", 1, "derecha") else -1
        if caminando and a.get("accion") in ("entrar_der", "salir_izq"):
            mira = -1
        if caminando and a.get("accion") in ("entrar_izq", "salir_der"):
            mira = 1
        pose = "caminar" if caminando and a.get("pose") != "correr" else a.get("pose", "idle")
        ctx.save()
        ctx.translate(q[0], q[1])
        ctx.rotate(cam["roll"])
        dibujar_personaje(ctx, spec, 0, 0, s, mira, a.get("expresion", "neutral"), pose,
                          tp + hash(a["id"]) % 7, pl.get("voz") == a["id"], a.get("objeto"),
                          semilla=hash(a["id"]) % 5, sudor=a.get("sudor", False))
        ctx.restore()
        if a.get("objeto") in ("farol", "fosforo"):
            fuentes.append((q[0], q[1] - 420 * s, 900 * s, 0.5))
    tinte = TINTE_PERSONAJES.get(hora)
    if tinte:
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.set_source_rgba(*tinte[0], tinte[1])
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint()
    if fuentes:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        for (x, y, r, k) in fuentes:
            fl = 1 + 0.06 * math.sin(t_abs * 11 + x)
            g = cairo.RadialGradient(x, y, 0, x, y, max(10, r * fl))
            g.add_color_stop_rgba(0, 1, 0.55, 0.2, 0.5 * k)
            g.add_color_stop_rgba(0.45, 1, 0.45, 0.15, 0.16 * k)
            g.add_color_stop_rgba(1, 1, 0.4, 0.1, 0)
            ctx.set_source(g)
            ctx.paint()
        ctx.restore()
    for ef in pl.get("efectos", []):
        efectos.dibujar_efecto(ctx, ef, tp, dur, pl.get("_i", 0))
    if pl.get("camara", {}).get("entrada") == "whip" and tp < 0.16:
        efectos.dibujar_efecto(ctx, "velocidad", tp, dur)
    if pl.get("inserto"):
        efectos.dibujar_inserto(ctx, pl["inserto"], p, tp, dur)
    efectos.vineta(ctx, 0.4 if hora == "noche" else 0.26)
    if sub:
        txt, t0 = sub
        efectos.dibujar_subtitulo(ctx, txt, t_abs - t0, list(pl.get("destacar", [])) + [guion.get("apodo", "")])
    ctx.restore()


def renderizar(guion, salida, preview=False, sin_voz=False, musica=None, solo_frame=None, max_seg=None):
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    base = os.path.splitext(salida)[0]
    tmp = base + "_tmp"
    os.makedirs(tmp, exist_ok=True)
    voz, subs, dur_total = planificar(guion, sin_voz, tmp)
    planos = guion["planos"]
    if max_seg:
        todos = [pl["_t0"] for pl in planos[1:]] + [dur_total]
        dur_total = min(todos, key=lambda c: abs(c - max_seg))
        planos = guion["planos"] = [pl for pl in planos if pl["_t0"] < dur_total]
        planos[-1]["_t1"] = dur_total
        voz = voz[: int(dur_total * audio.SR)]
        subs = [x for x in subs if x[0] < dur_total]
    escala = 0.5 if preview else 1.0
    ancho, alto = int(W * escala), int(H * escala)

    # 1) plan cuadro a cuadro: plano, tiempo y cámara
    frames = [int(solo_frame * FPS)] if solo_frame is not None else list(range(int(math.ceil(dur_total * FPS))))
    plan, ip = [], 0
    for f in frames:
        t = f / FPS
        while ip + 1 < len(planos) and t >= planos[ip + 1]["_t0"]:
            ip += 1
        if solo_frame is not None:
            ip = max(i for i, pl in enumerate(planos) if pl["_t0"] <= t)
        pl = planos[ip]
        tp, dur = t - pl["_t0"], pl["_t1"] - pl["_t0"]
        p = clamp(tp / max(dur, 1e-3))
        cam = camara3d.estado(pl.get("camara", {}), p, tp, _foco(pl, p), semilla=ip)
        plan.append((f, ip, tp, dur, p, cam))

    # 2) fondos 3D (Chromium headless) -> stdout base64, en paralelo con la composición
    trabajo = {"ancho": ancho, "alto": alto, "escenas": _escenas3d(planos),
               "cuadros": [{"e": ip, "cam": cam, "t": f / FPS, "p": p} for (f, ip, tp, dur, p, cam) in plan]}
    ruta_trabajo = os.path.join(tmp, "trabajo3d.json")
    with open(ruta_trabajo, "w") as fj:
        json.dump(trabajo, fj)
    nodo = subprocess.Popen(["node", os.path.join(RAIZ, "motor", "escena3d", "render3d.js"), ruta_trabajo],
                            stdout=subprocess.PIPE, cwd=RAIZ, bufsize=1 << 20)

    # 3) audio y codificador
    ff = None
    if solo_frame is None:
        eventos = []
        for pl in planos:
            for s_ in pl.get("sfx", []):
                nombre, off, vol = (s_, 0.0, 1.0) if isinstance(s_, str) else (s_.get("nombre"), s_.get("t", 0.0), s_.get("vol", 1.0))
                eventos.append((pl["_t0"] + off, nombre, vol))
            if pl.get("camara", {}).get("entrada") == "whip":
                eventos.append((pl["_t0"], "whoosh", 0.8))
            if pl.get("inserto"):
                eventos.append((pl["_t0"] + 0.05, "pop", 0.8))
        wav = os.path.join(tmp, "mezcla.wav")
        audio.escribir_wav(wav, audio.mezclar(voz, eventos, dur_total, musica, guion.get("animo_musica", "curioso")))
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                               "-s", f"{ancho}x{alto}", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                               "-crf", "23" if preview else "17", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida],
                              stdin=subprocess.PIPE)

    # 4) composición
    t_ini = time.time()
    for (f, ip, tp, dur, p, cam) in plan:
        linea = nodo.stdout.readline()
        if not linea:
            raise RuntimeError("el renderizador 3D terminó antes de tiempo (revisa node/playwright)")
        pl = planos[ip]
        enc = pl.get("camara", {}).get("encuadre", "medio")
        blur = camara3d.DESENFOQUE.get(enc, 1.4) * escala * (1.0 if pl.get("actores") else 0.5)
        bgra = _fondo_bgra(linea.strip(), blur, ancho, alto)
        surf = cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, ancho, alto)
        ctx = cairo.Context(surf)
        t = f / FPS
        sub = None
        for (a, b, txt, _) in subs:
            if a - 0.03 <= t < max(b, a + 0.25):
                sub = (txt, a)
        componer(ctx, guion, pl, tp, dur, cam, sub, t, escala)
        surf.flush()
        if solo_frame is not None:
            surf.write_to_png(salida)
            nodo.wait()
            return salida
        ff.stdin.write(bgra.tobytes())
        if f % (FPS * 2) == 0:
            print(f"  cuadro {f}/{len(plan)}  ({time.time() - t_ini:.0f}s)", file=sys.stderr)
    nodo.wait()
    ff.stdin.close()
    ff.wait()
    with open(base + ".srt", "w", encoding="utf-8") as fsrt:
        def ts(x):
            return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x * 1000 % 1000):03d}"
        for k, (a, b, txt, _) in enumerate(subs, 1):
            fsrt.write(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    print(f"listo: {salida}  ({dur_total:.1f}s, {len(planos)} planos)", file=sys.stderr)
    return salida


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)
