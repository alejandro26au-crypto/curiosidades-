"""Efectos de sonido SINTETIZADOS para «¿Cuánto tardará GTA 6 Online?» (sin música: la pone el usuario en YouTube).
whoosh en cada barrido, golpe grave en cada golpe de plano, «pop» en cada cifra o rótulo clave, ruido digital en los
fallos de 2013, caja registradora en el dinero, latido en «vivo». Todo atado a tiempos.json → sfx.wav.
Uso: python3 sfx.py && python3 ../../herramientas/mix.py voice.mp3 - sfx.wav out/mix_sin_musica.wav"""
import json, unicodedata, re, wave
import numpy as np
SR = 48000
T = json.load(open("tiempos.json")); FR = T["frases"]; PAL = T["palabras"]
DUR = max(f[1] for f in FR) / 30 + 3; N = int(DUR * SR); rng = np.random.default_rng(3)
n_ = lambda w: re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", w.lower()) if unicodedata.category(c) != "Mn"))
def en(w, i):
    a = FR[i][0]; prev = None
    for x in PAL:
        if x["f0"] == 0 and prev is not None and n_(x["p"]) == n_(w) and prev["f1"] >= a - 1: return prev["f1"] / 30
        if x["f0"] >= a - 1 and n_(x["p"]) == n_(w): return x["f0"] / 30
        prev = x
    raise SystemExit("falta " + w)
fr = lambda i: max(0, FR[i][0] - 2) / 30
buf = np.zeros(N, np.float32)
def place(sig, t, g):
    i = int(t * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += sig[: j - i] * g
def lp(x, c):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / c) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)
def whoosh(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n).astype(np.float32)
    e = np.sin(np.pi * t / d) ** 2; out = np.zeros(n, np.float32)
    for k in range(8):  # barrido de filtro hacia arriba
        a, b = k * n // 8, (k + 1) * n // 8; out[a:b] = lp(x, 400 + 5000 * (k / 7) ** 2)[a:b]
    return out * e
def golpe():
    n = int(0.5 * SR); t = np.arange(n) / SR; f = 45 + 120 * np.exp(-t * 25)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + lp(rng.standard_normal(n).astype(np.float32), 2500) * np.exp(-t * 30) * 0.5).astype(np.float32)
def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 - 500 * t / 0.12
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)).astype(np.float32)
def glitch(d=0.45):
    n = int(d * SR); x = np.repeat(rng.standard_normal(n // 60 + 1), 60)[:n].astype(np.float32)
    sq = np.sign(np.sin(2 * np.pi * 180 * np.arange(n) / SR)) * (rng.random(n // 2400 + 1).repeat(2400)[:n] > 0.5)
    return (x * 0.6 + sq * 0.4).astype(np.float32) * np.linspace(1, 0.2, n).astype(np.float32)
def caja():  # «ching»: dos campanitas
    n = int(0.6 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 6) for f in (2093, 2637, 3136)) / 3
    s2 = np.zeros(n); k = int(0.08 * SR); s2[k:] = s[: n - k]
    return (0.5 * s + 0.5 * s2).astype(np.float32)
def latido():
    out = np.zeros(int(0.9 * SR), np.float32)
    for t0, g in ((0, 1), (0.22, 0.7)):
        n = int(0.18 * SR); t = np.arange(n) / SR; s = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 22); i = int(t0 * SR); out[i:i + n] += s * g
    return out
# cortes (los mismos de main.js)
PLANOS = [(0, 'golpe'), (2, 'barrido'), (3, 'barrido'), (5, 'barrido'), (6, 'golpe'), (7, 'barrido'), (9, 'golpe'), (10, 'barrido'), (11, 'golpe'),
          (12, 'golpe'), (13, 'barrido'), (14, 'barrido'), (15, 'golpe'), (16, 'barrido'), (18, 'barrido'), (20, 'golpe'), (21, 'barrido'), (22, 'golpe')]
for i, tipo in PLANOS:
    if tipo == 'barrido': place(whoosh(), fr(i) - 0.15, 0.55)
    else: place(golpe(), fr(i), 0.8)
for w, i in [('online', 0), ('catorce', 2), ('17', 5), ('octubre', 6), ('millones', 6), ('amigos', 6), ('precio', 7), ('19', 12), ('historia', 13),
             ('fecha', 14), ('bloomberg', 16), ('confirmado', 17), ('razon', 18), ('trece', 19), ('desde', 20), ('apuesta', 21), ('esperar', 21), ('2027', 22), ('nuevo', 22)]:
    place(pop(), en(w, i) - 0.1, 0.45)
for w, i in [('dinero', 10), ('coches', 10), ('personaje', 10)]: place(golpe()[: int(0.25 * SR)], en(w, i) + 0.15, 0.6)
for w, i, d in [('aguantaron', 9, 0.5), ('personaje', 10, 0.2), ('caos', 21, 0.35)]: place(glitch(d), en(w, i) - 0.07, 0.35)
for w, i in [('quinientos', 11), ('diez', 20)]: place(caja(), en(w, i), 0.4)
place(golpe(), en('2027', 16) - 0.05, 0.9); place(latido(), en('vivo', 19) - 0.1, 0.9)
buf = np.clip(buf, -1, 1)
with wave.open('sfx.wav', 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((buf * 32767).astype(np.int16).tobytes())
print(f"sfx.wav {DUR:.1f} s")
