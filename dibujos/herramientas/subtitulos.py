#!/usr/bin/env python3
"""Subtítulos acordes al contenido, no muy grandes ni exagerados (estilo del usuario, 21 nov 2026, su prueba de CapCut):
una palabra cada vez, en minúsculas y sin puntuación, letra blanca gruesa con borde negro fino, a ~73 % de la altura,
tamaño medio y sin amarillo. Opciones: --zingo (estilo anterior: 1-2 palabras, grandes, cifras en amarillo) o --amarillo. Salen dos archivos desde tiempos.json (de tiempos_es.py):
  out/subtitulos.srt  -> para subirlo aparte a YouTube (siempre útil)
  out/subtitulos.ass  -> para quemarlos en el vídeo:  SUBS=1 bash ../../herramientas/terminar.sh "Titulo"
Uso (desde la carpeta del vídeo):  python3 ../../herramientas/subtitulos.py [--zingo | --amarillo]"""
import json, os, re, sys

ZINGO = "--zingo" in sys.argv; AMARILLO = ZINGO or "--amarillo" in sys.argv
maxp = 2 if ZINGO else 1
T = json.load(open("tiempos.json", encoding="utf-8"))
P = [(p["p"], p["f0"] / 30, p["f1"] / 30) for p in T["palabras"] if p["f1"] > p["f0"]]
NUM = {"uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "veinte", "treinta",
       "cuarenta", "cincuenta", "cien", "ciento", "doscientos", "trescientos", "quinientos", "mil", "millón", "millones", "mitad", "doble"}
grupos, act = [], []
for w in P:
    act.append(w)
    if len(act) >= maxp or w[0][-1:] in ".,?!:;…" or (len(act) >= 2 and sum(len(x[0]) for x in act) > 13):
        grupos.append(act); act = []
if act: grupos.append(act)
G = [(" ".join(x[0] for x in g), g[0][1], max(g[-1][2], g[0][1] + 0.25)) for g in grupos]
for i in range(len(G) - 1):  # sin huecos cortos: cada grupo dura hasta el siguiente si están a menos de 0,3 s
    if G[i + 1][1] - G[i][2] < 0.3: G[i] = (G[i][0], G[i][1], G[i + 1][1])
ts = lambda s, sep: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}{sep}{int(round(s % 1 * 1000)) if sep == ',' else int(round(s % 1 * 100)):0{3 if sep == ',' else 2}d}"
os.makedirs("out", exist_ok=True)
with open("out/subtitulos.srt", "w", encoding="utf-8") as fh:
    for i, (t, a, b) in enumerate(G, 1): fh.write(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{t}\n\n")
limpia = lambda w: re.sub(r"[^\wáéíóúñü]", "", w.lower())
def color(t):
    if not ZINGO: t = re.sub(r"[^\wáéíóúñü\s-]", "", t).lower()  # minúsculas y sin puntuación
    if not AMARILLO: return t
    return " ".join(("{\\c&H3AD2FF&}" + w + "{\\c&HFFFFFF&}") if re.search(r"\d", w) or limpia(w) in NUM else w for w in t.split())
cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,{tam},&H00FFFFFF,&H00FFFFFF,&H00261724,&H73000000,-1,0,0,0,100,100,{esp},0,1,{borde},{sombra},2,60,60,{margen},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("out/subtitulos.ass", "w", encoding="utf-8") as fh:
    fh.write(cab.format(**({"tam": 124, "esp": 2, "borde": 11, "sombra": 6, "margen": 560} if ZINGO else {"tam": 96, "esp": 1, "borde": 6, "sombra": 3, "margen": 518})))
    for t, a, b in G: fh.write(f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},Sub,,0,0,0,,{'{\\fscx80\\fscy80\\t(0,120,\\fscx100\\fscy100)}' if ZINGO else ''}{color(t)}\n")
print(f"out/subtitulos.srt y out/subtitulos.ass ({len(G)} grupos)")
