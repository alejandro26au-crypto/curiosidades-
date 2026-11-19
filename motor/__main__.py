"""CLI del motor.

  python -m motor guion  "tema o idea"   [--investigar] [-o guiones/x.json]
  python -m motor render guiones/x.json  [--preview] [--sin-voz] [--musica pista.mp3] [--max-seg 10]
  python -m motor todo   "tema o idea"   [--investigar] [--preview]
  python -m motor validar guiones/x.json
  python -m motor ideas  [-n 15]
"""
import argparse
import json
import os
import re
import sys
import unicodedata

from . import render, validar


def _slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "video"


def _guardar(g, ruta):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=2)
    print(f"guion: {ruta}")


def _reporte(g):
    avisos = validar.normalizar(g)
    puntaje, fallas = validar.revisar(g)
    for a in avisos:
        print(f"  aviso: {a}")
    print(f"fórmula: {puntaje}/100")
    for f in fallas:
        print(f"  - {f}")
    return puntaje


def main(argv=None):
    ap = argparse.ArgumentParser(prog="motor")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("guion"); a.add_argument("tema"); a.add_argument("--investigar", action="store_true"); a.add_argument("-o")
    b = sub.add_parser("render"); b.add_argument("guion"); b.add_argument("-o")
    for p in (b,):
        p.add_argument("--preview", action="store_true"); p.add_argument("--sin-voz", action="store_true")
        p.add_argument("--musica"); p.add_argument("--max-seg", type=float)
    c = sub.add_parser("todo"); c.add_argument("tema"); c.add_argument("--investigar", action="store_true")
    c.add_argument("--preview", action="store_true"); c.add_argument("--musica")
    d = sub.add_parser("validar"); d.add_argument("guion")
    e = sub.add_parser("ideas"); e.add_argument("-n", type=int, default=15); e.add_argument("--nicho", default="oficios de campo, mar, historia y naturaleza")
    args = ap.parse_args(argv)

    if args.cmd in ("guion", "todo"):
        from . import guion
        g = guion.generar(args.tema, investigar=args.investigar)
        ruta = getattr(args, "o", None) or f"guiones/{_slug(g.get('titulo', args.tema))}.json"
        _guardar(g, ruta)
        _reporte(g)
        if args.cmd == "todo":
            render.renderizar(g, f"salida/{_slug(g.get('titulo', args.tema))}.mp4", preview=args.preview, musica=args.musica)
    elif args.cmd == "render":
        g = render.cargar(args.guion)
        validar.normalizar(g)
        out = args.o or f"salida/{_slug(os.path.splitext(os.path.basename(args.guion))[0])}{'_preview' if args.preview else ''}.mp4"
        render.renderizar(g, out, preview=args.preview, sin_voz=args.sin_voz, musica=args.musica, max_seg=args.max_seg)
    elif args.cmd == "validar":
        _reporte(render.cargar(args.guion))
    elif args.cmd == "ideas":
        from . import guion
        print(json.dumps(guion.ideas(args.n, args.nicho), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
