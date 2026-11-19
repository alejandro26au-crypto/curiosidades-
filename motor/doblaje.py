"""Doblaje con voces externas (ElevenLabs, grabación propia...).

Recibe un audio por voz (narrador y cada personaje que habla) con sus líneas en el
orden del guion, lo transcribe con faster-whisper para obtener los tiempos de cada
palabra, lo corta en un clip por plano y anota el guion con "voz_externa". El render
usa esos clips en lugar de edge-tts.

    python -m motor doblar guiones/x.json --voz narrador=narrador.mp3 --voz vecino=vecino.mp3
"""
import json
import os
import re
import subprocess

import numpy as np

from . import audio


def _palabras_texto(texto):
    # quita etiquetas de emoción tipo [burlón] por si quedaron en el guion
    return re.sub(r"\[[^\]]*\]", " ", texto).split()


def _transcribir(ruta, modelo):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    segs, _ = modelo.transcribe(np.frombuffer(raw, np.float32), language="es", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]


def _emparejar(tokens, palabras):
    """Empareja las palabras del guion con las reconocidas (difflib) y devuelve
    [(inicio, fin, reconocida)] por palabra del guion; las no reconocidas se interpolan."""
    import difflib
    a = [audio._norm(t) for t in tokens]
    b = [audio._norm(w) for w, _, _ in palabras]
    res = [None] * len(tokens)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for d in range(blk.size):
            _, s0, e0 = palabras[blk.b + d]
            res[blk.a + d] = (s0, e0, True)
    conocidos = [k for k, r in enumerate(res) if r]
    for k in range(len(res)):
        if res[k] is None:
            prev = max([c for c in conocidos if c < k], default=None)
            nxt = min([c for c in conocidos if c > k], default=None)
            t0 = res[prev][1] if prev is not None else (palabras[0][1] if palabras else 0.0)
            t1 = res[nxt][0] if nxt is not None else (palabras[-1][2] if palabras else t0 + 0.3)
            n = (nxt if nxt is not None else len(res)) - (prev if prev is not None else -1)
            m = k - (prev if prev is not None else -1)
            a0 = t0 + (t1 - t0) * (m - 1) / n
            res[k] = (a0, a0 + (t1 - t0) / n, False)
    return res


def doblar(ruta_guion, audios, carpeta=None, modelo_whisper="small", acelerar=1.0, pausa_max=0.3):
    """audios: {id_voz: ruta}. id_voz = 'narrador' o el id del personaje.
    acelerar: velocidad (1.15 = 15 % más rápido, sin cambiar el tono).
    pausa_max: los silencios más largos que esto (s) se acortan a 0.2 s."""
    from faster_whisper import WhisperModel

    g = json.load(open(ruta_guion, encoding="utf-8"))
    nombre = os.path.splitext(os.path.basename(ruta_guion))[0]
    carpeta = carpeta or os.path.join("voces", nombre)
    os.makedirs(carpeta, exist_ok=True)
    modelo = WhisperModel(modelo_whisper, device="cpu", compute_type="int8")
    avisos = []
    for voz, ruta in audios.items():
        idx = [i for i, p in enumerate(g["planos"]) if p.get("voz", "narrador") == voz]
        if not idx:
            avisos.append(f"La voz '{voz}' no tiene líneas en el guion.")
            continue
        prep = os.path.join(carpeta, f"_{voz}.wav")
        filtro = f"silenceremove=stop_periods=-1:stop_duration={pausa_max}:stop_threshold=-40dB:stop_silence=0.2"
        if abs(acelerar - 1.0) > 1e-3:
            filtro += f",atempo={acelerar}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ruta, "-af", filtro, "-ac", "1", prep], check=True)
        ruta = prep
        palabras = _transcribir(ruta, modelo)
        x = audio.leer_audio(ruta)
        dur = len(x) / audio.SR
        # todas las palabras del guion de esta voz, con su plano
        toks = [(i, t) for i in idx for t in _palabras_texto(g["planos"][i]["texto"])]
        tiempos = _emparejar([t for _, t in toks], palabras)
        for i in idx:
            pos = [k for k, (ii, _) in enumerate(toks) if ii == i]
            ini = max(0.0, tiempos[pos[0]][0] - 0.06)
            k_sig = pos[-1] + 1
            sig = tiempos[k_sig][0] if k_sig < len(toks) else dur
            fin = min(sig - 0.03, tiempos[pos[-1]][1] + 0.15)
            if fin - ini < 0.3:
                avisos.append(f"Plano {i + 1} ({voz}): corte muy corto, revísalo.")
            clip = x[int(ini * audio.SR):int(fin * audio.SR)]
            base = os.path.join(carpeta, f"{i + 1:02d}")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(audio.SR), "-ac", "1", "-i", "-",
                            "-c:a", "libmp3lame", "-q:a", "2", base + ".mp3"], input=clip.astype(np.float32).tobytes(), check=True)
            json.dump([[toks[k][1], round(tiempos[k][0] - ini, 3), round(tiempos[k][1] - ini, 3)] for k in pos],
                      open(base + ".json", "w"), ensure_ascii=False)
        sin = sum(1 for t in tiempos if t[2] is False)
        if sin > len(toks) * 0.15:
            avisos.append(f"'{voz}': {sin} de {len(toks)} palabras no se reconocieron; ¿el audio trae el texto del guion?")
    for voz in audios:
        prep = os.path.join(carpeta, f"_{voz}.wav")
        if os.path.exists(prep):
            os.remove(prep)
    faltan = [i + 1 for i, p in enumerate(g["planos"]) if not os.path.exists(os.path.join(carpeta, f"{i + 1:02d}.mp3"))]
    if faltan:
        avisos.append(f"Planos sin audio externo (usarán edge-tts): {faltan}")
    g["voz_externa"] = carpeta
    json.dump(g, open(ruta_guion, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return avisos
