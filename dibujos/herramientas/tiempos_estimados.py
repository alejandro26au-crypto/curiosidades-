#!/usr/bin/env python3
"""Tiempos ESTIMADOS sin voz (del motor de Zingo): para planificar planos y saber cuánto durará el vídeo antes de grabar.
La duración NO es fija: sale del guion (fórmula de Citrino). Esto solo la calcula a ~170 palabras por minuto.
Uso (desde la carpeta del vídeo):  python3 ../../herramientas/tiempos_estimados.py script.txt [ppm]
-> tiempos.json + web/tiempos.js (los mismos formatos que tiempos_es.py; cuando llegue la voz real, se repite con tiempos_es.py)"""
import json, os, re, sys

guion = sys.argv[1]; ppm = float(sys.argv[2]) if len(sys.argv) > 2 else 170
txt = open(guion, encoding="utf-8").read().strip()
frases = re.split(r"(?<=[.!?…])\s+", txt)
spw, t, res, pal = 60 / ppm, 0.15, [], []
for fr in frases:
    t0 = t
    for w in fr.split():
        d = spw * (0.6 + 0.08 * len(re.sub(r"\W", "", w)))
        pal.append({"p": w, "f0": round(t * 30), "f1": round((t + d) * 30)})
        t += d + (0.12 if w[-1:] in ",;:" else 0.3 if w.endswith("...") or w.endswith("…") else 0.22 if w[-1:] in ".?!" else 0)
    res.append([round(t0 * 30), round(t * 30), fr])
fin = round(t * 30) + 15
json.dump({"frases": res, "palabras": pal, "estimado": True}, open("tiempos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if os.path.isdir("web"):
    with open("web/tiempos.js", "w", encoding="utf-8") as fh:
        fh.write(f"// ESTIMADO sin voz ({ppm:.0f} ppm) por tiempos_estimados.py. Repetir con tiempos_es.py cuando llegue la voz.\n")
        fh.write("export const FRASES = " + json.dumps(res, ensure_ascii=False) + ";\n")
        fh.write("export const PAL = " + json.dumps([[p["p"], p["f0"], p["f1"]] for p in pal], ensure_ascii=False) + ";\n")
        fh.write(f"export const DURACION = {fin}; // fotogramas\n")
n = len(txt.split())
print(f"{n} palabras · {len(frases)} frases · duración estimada {fin / 30:.1f} s a {ppm:.0f} ppm ({fin} fotogramas)")
