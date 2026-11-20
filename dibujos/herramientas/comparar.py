#!/usr/bin/env python3
"""Hoja lado a lado con los romanos (la referencia de calidad):
python3 ../../herramientas/comparar.py salida.jpg stills/a/f0040.jpg stills/a/f0140.jpg ...  (desde la carpeta del vídeo)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit", "example", "soldier", "stills.jpg")
rom = Image.open(K); W, H = rom.width // 7, rom.height // 2
ims = [("ROMANOS", rom.crop((0, H, W, 2 * H)))] + [(os.path.basename(f), Image.open(f)) for f in sys.argv[2:]]
sh = Image.new("RGB", (540 * len(ims), 1010), "white"); d = ImageDraw.Draw(sh)
try: fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except Exception: fnt = None
for i, (t, im) in enumerate(ims): sh.paste(im.resize((540, 960)), (i * 540, 50)); d.text((i * 540 + 12, 10), t, fill="black", font=fnt)
sh.save(sys.argv[1], quality=90); print(sys.argv[1])
