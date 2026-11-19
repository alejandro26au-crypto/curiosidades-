"""Convierte un guion JSON (storyboard) en un MP4 vertical 1080x1920 con voz,
subtítulos, música y SFX."""
import json
import math
import os
import subprocess
import sys
import time

import cairo
import numpy as np

from . import audio, camara, efectos, escenarios
from .dibujo import clamp, ease_in_out
from .formula import ESTILO
from .personajes import dibujar_personaje

W, H = 1080, 1920
FPS = ESTILO["fps"]
SUELO_FRENTE = 0.84


def _escala_por_y(y):
    hy = escenarios.HORIZONTE
    return clamp(0.32 + 0.68 * (y - hy) / (SUELO_FRENTE - hy), 0.25, 1.4)


def _posicion_actor(a, p, t):
    x, y = float(a.get("x", 0.5)), float(a.get("y", SUELO_FRENTE))
    acc = a.get("accion")
    k = ease_in_out(clamp(p / 0.6))
    caminando = False
    if acc == "entrar_izq":
        x = -0.25 + (x + 0.25) * k
        caminando = k < 1
    elif acc == "entrar_der":
        x = 1.25 + (x - 1.25) * k
        caminando = k < 1
    elif acc in ("salir_izq", "salir_der"):
        dst = -0.35 if acc == "salir_izq" else 1.35
        k2 = ease_in_out(clamp((p - 0.3) / 0.7))
        x = x + (dst - x) * k2
        caminando = 0 < k2 < 1
    elif acc == "mover":
        x2 = float(a.get("x2", x))
        x = x + (x2 - x) * ease_in_out(p)
        caminando = 0 < p < 1
    salto = 0
    if acc == "saltar":
        salto = -abs(math.sin(t * 5)) * 120
    return x * W, y * H + salto, caminando


def _foco(plano, actores_pos):
    cam = plano.get("camara", {})
    f = cam.get("foco")
    if isinstance(f, str) and f in actores_pos:
        x, y, s = actores_pos[f]
        return x, y - 560 * s * 0.75
    if isinstance(f, (list, tuple)) and len(f) == 2:
        return f[0] * W, f[1] * H
    if actores_pos:
        xs = [v[0] for v in actores_pos.values()]
        ys = [v[1] - 560 * v[2] * 0.7 for v in actores_pos.values()]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    return W / 2, H * 0.58


def dibujar_plano(ctx, guion, plano, tp, dur, palabras_plano, sub_actual, frame_global):
    p = clamp(tp / max(dur, 1e-3))
    fondo = plano.get("fondo", {})
    lugar, hora = fondo.get("lugar", "campo"), fondo.get("hora", "dia")
    semilla = int(fondo.get("semilla", 1))
    personajes = guion.get("personajes", {})
    t_abs = frame_global / FPS

    # posiciones de actores (para el foco de cámara)
    actores_pos = {}
    for a in plano.get("actores", []):
        x, y, _ = _posicion_actor(a, p, tp)
        actores_pos[a["id"]] = (x, y, _escala_por_y(float(a.get("y", SUELO_FRENTE))) * float(a.get("escala", 1)))
    cam = camara.estado(plano.get("camara", {}), p, tp, _foco(plano, actores_pos), dur, semilla=plano.get("_i", 0))

    def capa(d, fn):
        ctx.save()
        camara.aplicar(ctx, cam, d)
        fn()
        ctx.restore()

    capa(0.05, lambda: escenarios.dibujar_cielo(ctx, hora, t_abs, semilla))
    capa(0.30, lambda: escenarios.dibujar_lejos(ctx, lugar, hora, t_abs, semilla))
    capa(0.30, lambda: escenarios.bruma(ctx, hora))
    capa(1.0, lambda: escenarios.dibujar_suelo(ctx, lugar, t_abs, semilla, float(fondo.get("mar_sube", 0)) * p
                                               if fondo.get("mar_sube") else 0))

    props = fondo.get("props", [])
    fuentes_luz = []

    def dibujar_props(filtro):
        for pr in props:
            plano_p = pr.get("plano", "medio")
            if plano_p != filtro:
                continue
            x = float(pr.get("x", 0.5)) * W
            y = float(pr.get("y", {"fondo": 0.56, "medio": 0.68, "frente": 0.86, "primer_plano": 1.02}[plano_p])) * H
            s = float(pr.get("escala", 1.0)) * {"fondo": 0.5, "medio": 0.78, "frente": 1.0, "primer_plano": 1.45}[plano_p]
            escenarios.dibujar_prop(ctx, pr["tipo"], x, y, s, t_abs, pr)
            if pr["tipo"] == "fogata" and not pr.get("apagada"):
                dx, dy = ctx.user_to_device(x, y - 80 * s)
                fuentes_luz.append((dx, dy, 520 * s * cam["zoom"], 1.0))

    capa(0.65, lambda: dibujar_props("fondo"))
    capa(1.0, lambda: dibujar_props("medio"))

    # actores + props de frente ordenados por profundidad (y)
    def frente():
        orden = []
        for pr in props:
            if pr.get("plano", "medio") == "frente":
                orden.append((float(pr.get("y", 0.86)), "prop", pr))
        for a in plano.get("actores", []):
            orden.append((float(a.get("y", SUELO_FRENTE)), "actor", a))
        orden.sort(key=lambda z: z[0])
        for _, tipo, obj in orden:
            if tipo == "prop":
                x, y = float(obj.get("x", 0.5)) * W, float(obj.get("y", 0.86)) * H
                s = float(obj.get("escala", 1.0))
                escenarios.dibujar_prop(ctx, obj["tipo"], x, y, s, t_abs, obj)
                if obj["tipo"] == "fogata" and not obj.get("apagada"):
                    dx, dy = ctx.user_to_device(x, y - 80 * s)
                    fuentes_luz.append((dx, dy, 560 * s * cam["zoom"], 1.0))
            else:
                a = obj
                spec = personajes.get(a["id"], {})
                x, y, caminando = _posicion_actor(a, p, tp)
                s = _escala_por_y(float(a.get("y", SUELO_FRENTE))) * float(a.get("escala", 1))
                mira = a.get("mira", "der")
                mira = 1 if mira in ("der", 1, "derecha") else -1
                if a.get("accion") in ("entrar_der", "salir_izq") and caminando:
                    mira = -1
                if a.get("accion") in ("entrar_izq", "salir_der") and caminando:
                    mira = 1
                pose = "caminar" if caminando and a.get("pose") not in ("correr",) else a.get("pose", "idle")
                hablando = plano.get("voz") == a["id"]
                dibujar_personaje(ctx, spec, x, y, s, mira, a.get("expresion", "neutral"), pose,
                                  tp + hash(a["id"]) % 7, hablando, a.get("objeto"),
                                  semilla=hash(a["id"]) % 5, sudor=a.get("sudor", False))
                if a.get("objeto") == "farol" or a.get("objeto") == "fosforo":
                    dx, dy = ctx.user_to_device(x, y - 400 * s)
                    fuentes_luz.append((dx, dy, 260 * s * cam["zoom"], 0.6))

    capa(1.0, frente)
    capa(1.25, lambda: dibujar_props("primer_plano"))

    escenarios.capa_luz(ctx, hora, fuentes_luz, t_abs)
    for ef in plano.get("efectos", []):
        efectos.dibujar_efecto(ctx, ef, tp, dur, plano.get("_i", 0))
    if plano.get("camara", {}).get("entrada") == "whip" and tp < 0.16:
        efectos.dibujar_efecto(ctx, "velocidad", tp, dur)
    if plano.get("inserto"):
        efectos.dibujar_inserto(ctx, plano["inserto"], p, tp, dur)
    efectos.vineta(ctx, 0.42 if hora == "noche" else 0.3)
    if sub_actual:
        txt, t0 = sub_actual
        destacar = list(plano.get("destacar", [])) + [guion.get("apodo", "")]
        efectos.dibujar_subtitulo(ctx, txt, frame_global / FPS - t0, destacar)


def planificar(guion, sin_voz=False, carpeta="salida/tmp"):
    """Genera la voz y calcula inicio/fin de cada plano a partir de los tiempos de palabra."""
    planos = guion["planos"]
    personajes = guion.get("personajes", {})
    voz_narr = guion.get("voz_narrador", ESTILO["voz_narrador"])
    segs = []
    for pl in planos:
        quien = pl.get("voz", "narrador")
        spec = personajes.get(quien, {})
        segs.append({"texto": pl["texto"].strip(),
                     "voz": spec.get("voz", voz_narr) if quien != "narrador" else voz_narr,
                     "velocidad": spec.get("velocidad", ESTILO["velocidad_voz"]) if quien != "narrador" else ESTILO["velocidad_voz"],
                     "tono": spec.get("tono", "+0Hz") if quien != "narrador" else "+0Hz"})
    if sin_voz:
        voz, tiempos = audio.estimar(segs)
    else:
        try:
            voz, tiempos = audio.sintetizar(segs, carpeta)
        except Exception as e:  # sin red: render igual con tiempos estimados
            print(f"[voz] no se pudo sintetizar ({e.__class__.__name__}: {e}); uso tiempos estimados", file=sys.stderr)
            voz, tiempos = audio.estimar(segs)
    # inicio de cada plano = primera palabra (un poco antes, para que el corte caiga en la voz)
    inicios = []
    for i, ps in enumerate(tiempos):
        inicios.append(0.0 if i == 0 else max(0.0, ps[0][1] - 0.06) if ps else inicios[-1] + 1.5)
    fin_total = len(voz) / audio.SR + 0.35
    for i, pl in enumerate(planos):
        pl["_i"] = i
        pl["_t0"] = inicios[i]
        pl["_t1"] = inicios[i + 1] if i + 1 < len(planos) else fin_total
    subs = []
    for i, ps in enumerate(tiempos):
        for txt, a, b in efectos.agrupar_palabras([tuple(x) for x in ps]):
            subs.append((a, b, txt, i))
    return voz, subs, fin_total


def renderizar(guion, salida, preview=False, sin_voz=False, musica=None, solo_frame=None, max_seg=None):
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    base = os.path.splitext(salida)[0]
    tmp = base + "_tmp"
    voz, subs, dur_total = planificar(guion, sin_voz, tmp)
    if max_seg:
        # corta en el último corte de plano antes de max_seg (para clips de muestra)
        cortes = [pl["_t0"] for pl in guion["planos"] if pl["_t0"] <= max_seg + 0.01]
        todos = [pl["_t0"] for pl in guion["planos"][1:]] + [dur_total]
        fin = min(todos, key=lambda c: abs(c - max_seg))
        dur_total = fin if fin > 1 else max_seg
        guion["planos"] = [pl for pl in guion["planos"] if pl["_t0"] < dur_total]
        voz = voz[: int(dur_total * audio.SR)]
        subs = [x for x in subs if x[0] < dur_total]
    planos = guion["planos"]
    escala = 0.5 if preview else 1.0
    ancho, alto = int(W * escala), int(H * escala)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, ancho, alto)
    ctx = cairo.Context(surf)
    nframes = int(math.ceil(dur_total * FPS))

    if solo_frame is not None:
        rango = [int(solo_frame * FPS)]
    else:
        rango = range(nframes)

    # audio
    eventos = []
    for pl in planos:
        for s_ in pl.get("sfx", []):
            nombre, off, vol = (s_, 0.0, 1.0) if isinstance(s_, str) else (s_.get("nombre"), s_.get("t", 0.0), s_.get("vol", 1.0))
            eventos.append((pl["_t0"] + off, nombre, vol))
        if pl.get("camara", {}).get("entrada") == "whip":
            eventos.append((pl["_t0"], "whoosh", 0.8))
        if pl.get("inserto"):
            eventos.append((pl["_t0"] + 0.05, "pop", 0.8))
    wav = tmp + "_mezcla.wav"
    if solo_frame is None:
        mezcla = audio.mezclar(voz, eventos, dur_total, musica, guion.get("animo_musica", "curioso"))
        audio.escribir_wav(wav, mezcla)
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                               "-s", f"{ancho}x{alto}", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                               "-crf", "23" if preview else "18", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida],
                              stdin=subprocess.PIPE)
    t_ini = time.time()
    idx_plano = 0
    for f in rango:
        t = f / FPS
        while idx_plano + 1 < len(planos) and t >= planos[idx_plano + 1]["_t0"]:
            idx_plano += 1
        if solo_frame is not None:
            idx_plano = max(i for i, pl in enumerate(planos) if pl["_t0"] <= t)
        pl = planos[idx_plano]
        sub = None
        for (a, b, txt, i) in subs:
            if a - 0.03 <= t < max(b, a + 0.25):
                sub = (txt, a)
        ctx.save()
        ctx.scale(escala, escala)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        dibujar_plano(ctx, guion, pl, t - pl["_t0"], pl["_t1"] - pl["_t0"], None, sub, f)
        ctx.restore()
        surf.flush()
        if solo_frame is not None:
            surf.write_to_png(salida)
            return salida
        ff.stdin.write(surf.get_data())
        if f % (FPS * 5) == 0:
            el = time.time() - t_ini
            print(f"  frame {f}/{nframes}  ({el:.0f}s)", file=sys.stderr)
    ff.stdin.close()
    ff.wait()
    # subtítulos SRT de respaldo (para subir a YouTube/TikTok)
    with open(base + ".srt", "w", encoding="utf-8") as fsrt:
        for k, (a, b, txt, _) in enumerate(subs, 1):
            def ts(x):
                return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x * 1000 % 1000):03d}"
            fsrt.write(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    print(f"listo: {salida}  ({dur_total:.1f}s, {len(planos)} planos)", file=sys.stderr)
    return salida


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)
