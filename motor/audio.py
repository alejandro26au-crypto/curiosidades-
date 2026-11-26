"""Voz (edge-tts con tiempos palabra por palabra), música procedural, SFX
procedurales y mezcla con ducking."""
import asyncio
import json
import os
import re
import subprocess
import wave

import numpy as np

from .formula import ESTILO

SR = 44100
SFX = ["whoosh", "pop", "tick", "impacto", "fuego", "agua", "viento", "motor", "hielo",
       "ding", "error", "risa", "tictac", "golpe", "aire", "olas", "campana"]


# --- utilidades WAV -------------------------------------------------------------------
def leer_audio(ruta):
    """Decodifica cualquier audio a mono float32 44.1 kHz usando ffmpeg."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def escribir_wav(ruta, x):
    x = np.clip(x, -1, 1)
    est = np.stack([x, x], axis=1) if x.ndim == 1 else x
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((est * 32767).astype("<i2").tobytes())


# --- Voz --------------------------------------------------------------------------------
async def _tts_uno(texto, voz, velocidad, tono, ruta):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=velocidad, pitch=tono, boundary="WordBoundary")
    palabras = []
    with open(ruta, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                t0 = ch["offset"] / 1e7
                palabras.append([ch["text"], t0, t0 + ch["duration"] / 1e7])
    return palabras


def _norm(s):
    return re.sub(r"[^\wáéíóúñü]", "", s.lower())


def _alinear_puntuacion(texto, palabras):
    """edge-tts devuelve palabras sin signos; las reemplaza por los tokens del texto
    original (con comas, puntos y signos de pregunta) para cortar bien los subtítulos."""
    tokens = texto.split()
    out, j = [], 0
    for w, a, b in palabras:
        nw = _norm(w)
        k = j
        while k < len(tokens) and _norm(tokens[k]) != nw and k < j + 3:
            k += 1
        if k < len(tokens) and _norm(tokens[k]) == nw:
            out.append([tokens[k], a, b])
            j = k + 1
        else:
            out.append([w, a, b])
    return out


def sintetizar(segmentos, carpeta, cache=True):
    """segmentos: [{texto, voz, velocidad, tono}] -> (audio np, [palabras por segmento]).
    Concatena los segmentos sin silencios largos (ritmo sin aire, como el formato)."""
    os.makedirs(carpeta, exist_ok=True)
    pistas, tiempos = [], []
    cursor = 0.0
    for i, seg in enumerate(segmentos):
        ruta = os.path.join(carpeta, f"voz_{i:03d}.mp3")
        meta = ruta + ".json"
        clave = json.dumps({k: v for k, v in seg.items() if k != "pausa"}, sort_keys=True, ensure_ascii=False)
        if cache and os.path.exists(meta) and json.load(open(meta)).get("clave") == clave:
            palabras = json.load(open(meta))["palabras"]
        else:
            for intento in range(4):
                try:
                    palabras = asyncio.run(_tts_uno(seg["texto"], seg["voz"], seg.get("velocidad", ESTILO["velocidad_voz"]),
                                                    seg.get("tono", "+0Hz"), ruta))
                    break
                except Exception:
                    if intento == 3:
                        raise
            json.dump({"clave": clave, "palabras": palabras}, open(meta, "w"), ensure_ascii=False)
        x = leer_audio(ruta)
        # recorta silencios de cola/cabeza
        umbral = 0.01
        idx = np.where(np.abs(x) > umbral)[0]
        ini = max(0, idx[0] - int(0.02 * SR)) if len(idx) else 0
        fin = min(len(x), idx[-1] + int(0.06 * SR)) if len(idx) else len(x)
        x = x[ini:fin]
        corr = ini / SR
        pausa = seg.get("pausa", 0.08 if seg["texto"].rstrip()[-1:] in ".?!" else 0.02)
        palabras = _alinear_puntuacion(seg["texto"], palabras)
        tiempos.append([[w, cursor + a - corr, cursor + b - corr] for w, a, b in palabras])
        pistas.append(x)
        pistas.append(np.zeros(int(pausa * SR), dtype=np.float32))
        cursor += len(x) / SR + pausa
    return np.concatenate(pistas), tiempos


def estimar(segmentos, ppm=178):
    """Sin red/voz: tiempos estimados y pista muda (para previsualizar o doblar después)."""
    tiempos, cursor = [], 0.0
    spw = 60.0 / ppm
    for seg in segmentos:
        ps = []
        for w in seg["texto"].split():
            d = spw * (0.6 + 0.08 * len(re.sub(r"\W", "", w)))
            ps.append([w, cursor, cursor + d])
            cursor += d + (0.12 if w[-1:] in ",;:" else 0.22 if w[-1:] in ".?!" else 0)
        tiempos.append(ps)
    return np.zeros(int((cursor + 0.3) * SR), dtype=np.float32), tiempos


# --- Música procedural ------------------------------------------------------------------
def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def musica(duracion, bpm=112, semilla=0, animo="curioso"):
    """Pista instrumental ligera tipo 'storytelling': pluck pentatónico, bajo, bombo y hi-hat.
    animo: 'curioso' | 'tension' | 'triunfo' (cambia escala y densidad)."""
    rng = np.random.default_rng(semilla)
    n = int(duracion * SR) + SR
    out = np.zeros(n, dtype=np.float32)
    beat = 60 / bpm
    raiz = 220.0 if animo != "tension" else 196.0
    escala = [0, 2, 4, 7, 9, 12, 14] if animo != "tension" else [0, 1, 3, 7, 8, 12, 13]
    progr = [0, 5, 3, 4] if animo != "tension" else [0, 1, 0, -2]
    paso = 0
    t = 0.0
    while t < duracion:
        compas = int(t / (beat * 4)) % 4
        i0 = int(t * SR)
        # bombo en 1 y 3, hat en contratiempo
        if paso % 4 in (0, 2):
            k = int(0.25 * SR)
            tt = np.arange(k) / SR
            f = 50 + 90 * np.exp(-tt * 30)
            out[i0:i0 + k] += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 12)
        k = int(0.05 * SR)
        hat_t = t + beat / 2
        j0 = int(hat_t * SR)
        if j0 + k < n:
            out[j0:j0 + k] += 0.05 * rng.standard_normal(k) * _env(k, 0.001, 0.015)
        # bajo
        if paso % 2 == 0:
            k = int(beat * 0.9 * SR)
            tt = np.arange(k) / SR
            fb = raiz / 2 * 2 ** (progr[compas] / 12)
            out[i0:i0 + k] += 0.16 * np.tanh(2 * np.sin(2 * np.pi * fb * tt)) * _env(k, 0.01, 0.3)
        # pluck melódico (corcheas con huecos)
        for sub in (0, 0.5):
            if rng.random() < (0.55 if animo == "curioso" else 0.7):
                nota = escala[rng.integers(len(escala))] + progr[compas]
                fq = raiz * 2 ** (nota / 12)
                k = int(0.35 * SR)
                j0 = int((t + sub * beat) * SR)
                if j0 + k < n:
                    tt = np.arange(k) / SR
                    tono = np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(4 * np.pi * fq * tt)
                    out[j0:j0 + k] += 0.09 * tono * _env(k, 0.002, 0.12)
        t += beat
        paso += 1
    out = out[: int(duracion * SR)]
    return out / (np.max(np.abs(out)) + 1e-6) * 0.6


# --- SFX procedurales ---------------------------------------------------------------------
def sfx(nombre, semilla=0):
    rng = np.random.default_rng(abs(hash(nombre)) % 9999 + semilla)

    def ruido(seg):
        return rng.standard_normal(int(seg * SR)).astype(np.float32)

    def lp(x, a):
        y = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += a * (x[i] - acc)
            y[i] = acc
        return y

    if nombre == "whoosh":
        x = ruido(0.4)
        e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
        return lp(x * e, 0.18) * 0.9
    if nombre == "pop":
        k = int(0.09 * SR)
        tt = np.arange(k) / SR
        return 0.7 * np.sin(2 * np.pi * (500 + 900 * np.exp(-tt * 40)) * tt) * _env(k, 0.001, 0.04)
    if nombre in ("tick", "tictac"):
        k = int(0.03 * SR)
        clic = ruido(0.03) * _env(k, 0.0005, 0.005) * 0.6
        if nombre == "tick":
            return clic
        out = np.zeros(int(2.0 * SR), dtype=np.float32)
        for i in range(4):
            j = int(i * 0.5 * SR)
            out[j:j + k] += clic
        return out
    if nombre in ("impacto", "golpe"):
        k = int(0.5 * SR)
        tt = np.arange(k) / SR
        s = np.sin(2 * np.pi * (45 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 7)
        return 0.9 * s + 0.3 * lp(ruido(0.5), 0.2) * np.exp(-tt * 18)
    if nombre == "fuego":
        x = lp(ruido(2.0), 0.05) * 0.4
        for _ in range(30):
            j = rng.integers(0, len(x) - 300)
            x[j:j + 300] += ruido(300 / SR) * _env(300, 0.0005, 0.003)
        return x
    if nombre == "agua":
        out = np.zeros(int(1.2 * SR), dtype=np.float32)
        for i in range(3):
            k = int(0.12 * SR)
            tt = np.arange(k) / SR
            j = int(i * 0.38 * SR)
            out[j:j + k] += 0.5 * np.sin(2 * np.pi * (900 + 1400 * tt / 0.12) * tt) * _env(k, 0.001, 0.03)
        return out
    if nombre in ("viento", "aire"):
        x = lp(ruido(1.6), 0.03 if nombre == "viento" else 0.4)
        return x * np.sin(np.linspace(0, np.pi, len(x))) * (1.6 if nombre == "viento" else 0.35)
    if nombre == "olas":
        x = lp(ruido(2.5), 0.04)
        return x * (0.5 + 0.5 * np.sin(np.linspace(0, 2 * np.pi, len(x)))) * 1.5
    if nombre == "motor":
        k = int(1.6 * SR)
        tt = np.arange(k) / SR
        f = 40 + 30 * np.minimum(1, tt * 2)
        return 0.5 * np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.minimum(1, tt * 4) * np.exp(-tt * 0.6)
    if nombre == "hielo":
        out = ruido(0.6) * 0.0
        for _ in range(8):
            j = rng.integers(0, len(out) - 500)
            out[j:j + 500] += ruido(500 / SR) * _env(500, 0.0002, 0.004) * 0.9
        return out
    if nombre in ("ding", "campana"):
        k = int(1.2 * SR)
        tt = np.arange(k) / SR
        f = 1318 if nombre == "ding" else 660
        return 0.45 * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt)) * _env(k, 0.002, 0.35)
    if nombre == "error":
        k = int(0.45 * SR)
        tt = np.arange(k) / SR
        return 0.35 * np.sign(np.sin(2 * np.pi * 110 * tt)) * _env(k, 0.005, 0.3)
    if nombre == "risa":
        out = np.zeros(int(0.9 * SR), dtype=np.float32)
        for i in range(5):
            k = int(0.11 * SR)
            tt = np.arange(k) / SR
            j = int(i * 0.16 * SR)
            f = 260 - i * 12
            out[j:j + k] += 0.35 * np.sin(2 * np.pi * f * tt + 3 * np.sin(2 * np.pi * 6 * tt)) * np.sin(np.pi * tt / tt[-1])
        return out
    return np.zeros(1, dtype=np.float32)


def mezclar(voz, eventos_sfx, duracion, ruta_musica=None, animo="curioso", semilla=0):
    n = int(duracion * SR)
    v = np.zeros(n, dtype=np.float32)
    v[: min(n, len(voz))] = voz[:n]
    m = leer_audio(ruta_musica) if ruta_musica else musica(duracion, semilla=semilla, animo=animo)
    if len(m) < n:
        m = np.tile(m, n // max(1, len(m)) + 1)
    m = m[:n]
    # ducking: baja la música cuando hay voz
    envv = np.convolve(np.abs(v), np.ones(2205) / 2205, mode="same")
    duck = 1 - 0.55 * np.clip(envv / (envv.max() + 1e-6) * 3, 0, 1)
    gm = 10 ** (ESTILO["musica_db"] / 20) * 2.2
    out = v * 0.95 + m * gm * duck
    for (t0, nombre, vol) in eventos_sfx:
        s = sfx(nombre, int(t0 * 10))
        j = int(t0 * SR)
        if j >= n:
            continue
        k = min(len(s), n - j)
        out[j:j + k] += s[:k] * 0.32 * vol
    pico = np.max(np.abs(out)) + 1e-6
    return out / pico * 0.92
