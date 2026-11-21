"""Música por tramos y efectos sintetizados (stems music.wav y sfx.wav para mix.py). Se adapta en cada vídeo.
Uso (desde la carpeta del vídeo): python3 audio.py  ->  music.wav + sfx.wav
Luego: python3 ../../herramientas/mix.py voice.mp3 music.wav sfx.wav              (con música)
       python3 ../../herramientas/mix.py voice.mp3 - sfx.wav out/mix_sin_musica.wav (sin música, para CapCut)
Técnicas (del submarino): la música cambia por TRAMOS según el guion (tema, silencio antes del golpe, tramo cómico,
solemne, fanfarria), un «whoosh» en cada corte de plano (barridos) y un efecto en cada golpe (cifras, remates).
Los fotogramas salen de web/tiempos.js (los escribe tiempos_es.py): en("palabra") = segundo de esa palabra."""
import numpy as np, subprocess, wave, re, json

SR = 48000
TJS = open("web/tiempos.js", encoding="utf-8").read()
TOTAL_F = int(re.search(r"DURACION\s*=\s*(\d+)", TJS).group(1))
PAL = json.loads(re.search(r"^export const PAL\s*=\s*(\[.*?\]);", TJS, re.S | re.M).group(1))
DUR = TOTAL_F / 30
N = int(DUR * SR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR
F = lambda f: f / 30
import unicodedata
_n = lambda w: re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", w.lower()) if unicodedata.category(c) != "Mn"))
def en(w, n=1):
    """segundo en que empieza la palabra w (n-ésima vez)"""
    k = 0
    for p, f0, f1 in PAL:
        if _n(p) == _n(w):
            k += 1
            if k == n: return F(f0)
    raise SystemExit("palabra no está en tiempos.js: " + w)

def load_voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "voice.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).copy()
    out = np.zeros(N, np.float32); out[:min(N, len(v))] = v[:N]; return out

def env(n, a=0.005, r=0.2, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e

def lp(x, k):  # one-pole low-pass, k in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y

def lp_fast(x, cutoff):
    # FFT brick-ish low-pass (fast, fine for beds)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i < N and j > i: buf[i:j] += sig[: j - i] * gain

midi = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------------- music ----------------
music = np.zeros(N, np.float32)
BPM = 104; beat = 60 / BPM
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 56, 59])]  # Am F G E
def pluck(f, dur=0.35, bright=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) / (k + 1) for k in range(6))
    return (s * env(n, 0.003, dur * 0.35)).astype(np.float32)
def brass(fs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        ph = 2 * np.pi * f * t + 0.003 * np.sin(2 * np.pi * 5 * t)
        s += sum(np.sin((k + 1) * ph) / (k + 1) ** 1.3 for k in range(8))
    a = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.15).clip(0)
    return lp_fast((s * a).astype(np.float32), 1800) / len(fs)
def drum(kind):
    if kind == "kick":
        n = int(0.35 * SR); t = np.arange(n) / SR; f = 50 + 90 * np.exp(-t * 30)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)
    n = int(0.18 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n) * np.exp(-t * 28) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20) * 0.5
    return hp_fast(s.astype(np.float32), 300)

def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def thunk(f0=90, d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t * (1 + 0.6 * np.exp(-t * 40))) * np.exp(-t * 14) + lp_fast(noise(d), 1200) * np.exp(-t * 30) * 0.5).astype(np.float32)
def rumble(d):
    n = int(d * SR); t = np.arange(n) / SR
    s = lp_fast(noise(d), 160) * 3 * np.minimum(1, t / 0.15) * np.exp(-t / (d * 0.45))
    return s.astype(np.float32)
def crash(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n, np.float32)
    for k in range(14):
        tk = rng.uniform(0, d * 0.6); i = int(tk * SR); g = thunk(rng.uniform(60, 160), 0.35) * rng.uniform(0.3, 0.9)
        s[i:i + len(g)] += g[: n - i]
    s += lp_fast(noise(d), 2500) * np.exp(-t * 3) * 0.25
    return s
def cuckoo():
    out = []
    for f, d in [(740, 0.16), (587, 0.24)]:
        n = int(d * SR); t = np.arange(n) / SR
        out.append(np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t * 6)); out.append(np.zeros(int(0.06 * SR)))
    return np.concatenate(out).astype(np.float32)
def scrape(d=0.8):
    n = int(d * SR); t = np.arange(n) / SR
    s = noise(d) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * np.sin(np.pi * t / d)
    s = hp_fast(lp_fast(s, 5000), 1500)
    ring = np.sin(2 * np.pi * 1870 * t) * np.exp(-t * 3) * 0.2
    return (s * 0.6 + ring).astype(np.float32)
def ting():
    n = int(1.2 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(2093, 4), (3136, 6), (4186, 8)]) * 0.3).astype(np.float32)
def sting():
    n = int(2.0 * SR); t = np.arange(n) / SR
    low = np.sin(2 * np.pi * 41 * t) * np.exp(-t * 1.5) * 1.2
    hit = lp_fast(noise(2.0), 900) * np.exp(-t * 6) * 0.8
    stab = brass([midi(45), midi(48), midi(51)], 1.4); s = low + hit; s[: len(stab)] += stab * 2.2 * np.exp(-np.arange(len(stab)) / SR * 2)
    return s.astype(np.float32)
def creak(d=0.6, f0=140):
    n = int(d * SR); t = np.arange(n) / SR
    rate = f0 * (1 + 0.35 * np.sin(2 * np.pi * 1.3 * t / d))
    ph = np.cumsum(rate) / SR; pulses = (np.mod(ph, 1) < 0.08).astype(np.float32)
    s = lp_fast(pulses * (0.6 + 0.4 * rng.random(n).astype(np.float32)), 2200) * np.sin(np.pi * t / d)
    return hp_fast(s, 200) * 2.5
def snap():
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 800) * np.exp(-t * 18) * 1.4 + np.pad(thunk(120, 0.4), (0, n - int(0.4 * SR))) * 0.6).astype(np.float32)
def splash(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    s = lp_fast(noise(d), 4000) * (np.exp(-t * 4) * np.minimum(1, t / 0.01)) + lp_fast(noise(d), 400) * np.exp(-t * 7) * 1.5
    return s.astype(np.float32)
def whoosh(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1500) * np.sin(np.pi * t / d) ** 2 * 0.6).astype(np.float32)
def snore(d=1.1):
    n = int(d * SR); t = np.arange(n) / SR
    buzz = (np.mod(np.cumsum(60 + 25 * np.sin(np.pi * t / d)) / SR, 1) < 0.3).astype(np.float32)
    return (lp_fast(buzz * 0.5 + noise(d) * 0.15, 700) * np.sin(np.pi * t / d) ** 2).astype(np.float32)
def leaves(d):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 6000), 2500) * (0.3 + 0.3 * np.sin(2 * np.pi * 0.7 * t) ** 2) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)).astype(np.float32)
def water(d):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 900) * 0.5 + hp_fast(lp_fast(noise(d), 3000), 1200) * 0.15 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))).astype(np.float32)



# ---------------- MÚSICA POR TRAMOS (ejemplo de la plantilla: cámbialo en cada vídeo) ----------------
BPM = 112; beat = 60 / BPM
def timp(f0=73.4, d=0.9):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t * (1 + 0.04 * np.exp(-t * 20))) * np.exp(-t * 4) + lp_fast(rng.standard_normal(n).astype(np.float32), 300) * np.exp(-t * 25) * 0.4).astype(np.float32)
def section(t0, t1, chords, gain=1.0, drums=True, ost=True, brassg=0.08):
    tt, bar = t0, 0
    while tt < t1 - 0.05:
        root, ch = chords[bar % len(chords)]
        L = min(beat * 4, t1 - tt)
        place(music, brass([midi(m) for m in ch], L * 0.98), tt, brassg * gain)
        for b in range(8):
            tb = tt + b * beat / 2
            if tb >= t1: break
            if ost: place(music, pluck(midi(root - 12 + (7 if b % 4 == 3 else 0)), 0.22, 0.5), tb, 0.32 * gain)
            if drums and b % 4 == 0: place(music, drum("kick"), tb, 0.5 * gain)
            if drums and b % 4 == 2: place(music, drum("snare"), tb, 0.22 * gain)
        bar += 1; tt += beat * 4

TEMA = [(50, [50, 53, 57]), (46, [46, 50, 53]), (48, [48, 52, 55]), (45, [45, 49, 52])]      # Rem Sib Do La (tenso, empuja)
ALEGRE = [(50, [50, 54, 57]), (55, [55, 59, 62]), (57, [57, 61, 64]), (50, [50, 54, 57])]    # Re mayor (fanfarria)
def comico(t0, t1, gain=0.22):  # pizzicato saltarín
    for k in range(int((t1 - t0) / (beat / 2))):
        tb = t0 + k * beat / 2; m = [62, 69, 65, 69, 62, 69, 67, 69][k % 8]
        place(music, pluck(midi(m), 0.16, 0.7), tb, gain)
        if k % 2 == 0: place(music, pluck(midi(50), 0.2, 0.4), tb, gain * 1.1)
def dron(t0, t1, gain=0.15):    # oscuridad / espera: dron grave
    n = int((t1 - t0) * SR); td = np.arange(n) / SR
    place(music, lp_fast(((np.sin(2 * np.pi * 36.7 * td) + 0.5 * np.sin(2 * np.pi * 55 * td)) * np.minimum(1, td / 0.6)).astype(np.float32), 400), t0, gain)

section(0.0, en("diez") - 0.25, TEMA, 1.0)                      # tema desde el gancho
# silencio de 0,25 s antes del golpe («¡Diez metros!») y vuelve el tema
place(music, timp(73.4, 1.2), en("diez"))
section(en("diez"), en("cien") - 0.2, TEMA, 1.0)
section(en("cien"), en("y"), ALEGRE, 1.1, brassg=0.12)          # «¡cien monedas!»: fanfarria
for k, m in enumerate([62, 66, 69, 74]): place(music, brass([midi(m)], 0.3), en("cien") + k * 0.12, 0.08)
comico(en("y"), en("silencio"))                                  # «se rió»: tramo cómico
dron(en("silencio"), DUR)                                        # «silencio»: solo dron
# (solemne: section(t0, t1, ACORDES, 0.8, drums=False, ost=False, brassg=0.11))

# ---------------- EFECTOS ----------------
sfx = np.zeros(N, np.float32)
def klaxon(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; f = 420 + 120 * (np.mod(t, 0.4) < 0.2)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4; return lp_fast(s.astype(np.float32), 2500) * np.minimum(1, (d - t) / 0.1).astype(np.float32)
def boom(d=2.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 34 * t * (1 + np.exp(-t * 6))) * np.exp(-t * 2.2) * 1.4 + lp_fast(noise(d), 500) * np.exp(-t * 2.5) * 1.6).astype(np.float32)
def groan(d=1.6, f0=70):
    n = int(d * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.25 * np.sin(2 * np.pi * 0.7 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * rng.random(n)) ; return lp_fast((s * np.sin(np.pi * t / d)).astype(np.float32), 900) * 1.5
def heart():
    return np.concatenate([thunk(55, 0.18) * 0.9, np.zeros(int(0.12 * SR), np.float32), thunk(50, 0.2) * 0.6])
def pingf(d=2.5):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 2.2) * np.minimum(1, t / 0.005)
    for k, dl in enumerate([0.35, 0.7]): i = int(dl * SR); s[i:] += s[:n - i] * (0.35 / (k + 1))
    return s.astype(np.float32)
def hiss(d):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 3000) * 0.5 * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3)).astype(np.float32)
def bubbles(d, dens=18):
    n = int(d * SR); s = np.zeros(n, np.float32)
    for k in range(int(d * dens)):
        i = int(rng.uniform(0, d - 0.1) * SR); m = int(0.06 * SR); tt = np.arange(m) / SR; f = rng.uniform(300, 900) * (1 + tt * 8)
        s[i:i + m] += (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * 0.4).astype(np.float32)[: n - i]
    return s
def strike():
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 2000) * np.exp(-t * 10) * 0.8 + lp_fast(noise(d), 1500) * np.exp(-t * 3) * 0.3).astype(np.float32)
def flush(d=1.8):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1800) * np.sin(np.pi * t / d) * 1.2 + thunk(140, 0.3).tolist().__len__() * 0).astype(np.float32)

# un «whoosh» en cada corte de plano (los barridos de cámara): las mismas palabras que PLANOS en story.js
CUTS = [en("el"), en("y")]
for c in CUTS: place(sfx, whoosh(0.3), c - 0.07 - 0.18, 0.45)
place(sfx, splash(0.8), en("metros") + 0.3, 0.5)                # el cubo cae al pozo
place(sfx, thunk(110, 0.3), en("diez"), 0.6)                     # golpe en la cifra
place(sfx, ting(), en("cien"), 0.35); place(sfx, strike(), en("cien"), 0.4)  # «¡cien!»: brillo + golpe
place(sfx, leaves(F(TOTAL_F) - en("y")), en("y"), 0.3)          # brisa de la tarde

def escribe(nombre, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(nombre, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
escribe("music.wav", music / max(1e-6, np.abs(music).max()) * 0.9)
escribe("sfx.wav", sfx / max(1e-6, np.abs(sfx).max()) * 0.9)
print("stems ok", DUR)
