"""Cámara virtual 2.5D: push-in, pull-out, paneos, tilts, crash zoom, sacudida,
seguimiento y órbita, con parallax por profundidad de capa y temblor de mano."""
import math

from .dibujo import ease_in_out, ease_out, ease_out_back, clamp, ruido1d

W, H = 1080, 1920
MOVIMIENTOS = ["estatico", "push_in", "pull_out", "pan_izq", "pan_der", "tilt_arriba",
               "tilt_abajo", "zoom_golpe", "sacudida", "seguimiento", "orbita"]
ENCUADRES = {"general": 0.9, "medio": 1.3, "americano": 1.38, "primer_plano": 1.85, "detalle": 2.3}


def estado(cam_spec, p, t, foco_xy, dur, semilla=0):
    """Devuelve dict(x, y, zoom, rot) = punto del mundo al centro de pantalla."""
    mov = cam_spec.get("mov", "estatico")
    base = ENCUADRES.get(cam_spec.get("encuadre", "medio"), 1.0)
    inten = float(cam_spec.get("intensidad", 1.0))
    fx, fy = foco_xy
    cx, cy = W / 2, H / 2
    # encuadrar el foco cuando hay zoom de base
    if base > 1.0:
        k = clamp((base - 1) / 0.5)
        cx += (fx - cx) * k
        cy += (fy - cy) * k
    elif base < 1.0:
        cy -= 80
    zoom, rot = base, 0.0
    e = ease_in_out(p)
    if mov == "estatico":
        zoom *= 1 + 0.03 * p
    elif mov == "push_in":
        zoom *= 1 + 0.28 * inten * e
        cx += (fx - cx) * 0.6 * e
        cy += (fy - cy) * 0.6 * e
    elif mov == "pull_out":
        zoom *= 1.3 - 0.3 * inten * ease_out(p)
        k = 1 - ease_out(p)
        cx += (fx - cx) * 0.6 * k
        cy += (fy - cy) * 0.6 * k
    elif mov in ("pan_izq", "pan_der"):
        s = -1 if mov == "pan_izq" else 1
        cx += s * 260 * inten * (e - 0.5)
        zoom *= 1.05
    elif mov in ("tilt_arriba", "tilt_abajo"):
        s = -1 if mov == "tilt_arriba" else 1
        cy += s * 340 * inten * (e - 0.5)
        zoom *= 1.05
    elif mov == "zoom_golpe":
        k = ease_out_back(clamp(t / 0.18), 2.0)
        zoom *= 1 + 0.38 * inten * k
        cx += (fx - cx) * 0.7 * clamp(k)
        cy += (fy - cy) * 0.7 * clamp(k)
    elif mov == "sacudida":
        zoom *= 1.08
    elif mov == "seguimiento":
        cx = fx
        zoom *= 1.08
    elif mov == "orbita":
        rot = (e - 0.5) * 0.05 * inten
        cx += 120 * (e - 0.5)
        zoom *= 1.06 + 0.06 * e
    # temblor de mano (siempre) + sacudida
    amp = 3.0 + (22 * inten * (1 - 0.6 * p) if mov == "sacudida" or cam_spec.get("sacudida") else 0)
    cx += amp * ruido1d(t * 6, semilla)
    cy += amp * ruido1d(t * 6 + 50, semilla)
    rot += 0.002 * ruido1d(t * 2 + 9, semilla) + (0.01 * ruido1d(t * 18, semilla) if mov == "sacudida" else 0)
    # entrada "whip": barrido rápido desde un costado en los primeros frames
    if cam_spec.get("entrada") == "whip":
        k = 1 - ease_out(clamp(t / 0.16))
        cx += 700 * k * (1 if semilla % 2 else -1)
    return {"x": cx, "y": cy, "zoom": zoom, "rot": rot}


def aplicar(ctx, cam, profundidad):
    d = profundidad
    z = cam["zoom"] ** (0.25 + 0.75 * d) if d < 1 else cam["zoom"] * (1 + (d - 1) * 0.3)
    ctx.translate(W / 2, H / 2)
    ctx.rotate(cam["rot"] * min(d, 1.2))
    ctx.scale(z, z)
    ctx.translate(-(W / 2 + (cam["x"] - W / 2) * d), -(H / 2 + (cam["y"] - H / 2) * d))
