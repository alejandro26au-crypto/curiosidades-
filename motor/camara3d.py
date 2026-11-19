"""Cámara 3D (metros) con los mismos movimientos del formato y proyección
idéntica a three.js para pegar los personajes 2D sobre el escenario 3D."""
import math

from .dibujo import ease_in_out, ease_out, ease_out_back, clamp, ruido1d

W, H = 1080, 1920
FOV = 40.0
ALTO_PERSONAJE = 1.75          # metros
ALTO_LOCAL = 660.0             # unidades de dibujo de personajes.py (pies -> coronilla)
DIST = {"general": 10.5, "medio": 4.8, "americano": 3.5, "primer_plano": 2.3, "detalle": 2.4}
ALTURA_FOCO = {"general": 1.2, "medio": 1.05, "americano": 1.2, "primer_plano": 1.5, "detalle": 0.55}
DESENFOQUE = {"general": 0.0, "medio": 1.4, "americano": 2.2, "primer_plano": 3.6, "detalle": 4.5}


# --- mapeo del storyboard (0-1) a metros -------------------------------------------------
# x=0..1 equivale aprox. al ancho de pantalla en un plano medio (el cuadro vertical es angosto)
ANCHO_ESCENA = 2.6


def _z(y):
    return min(0.25, (y - 0.86) * 30.0)


def actor_mundo(x, y):
    return ((x - 0.5) * ANCHO_ESCENA, 0.0, _z(y))


def prop_mundo(pr):
    plano = pr.get("plano", "medio")
    x = float(pr.get("x", 0.5))
    esc = float(pr.get("escala", 1.0))
    if plano == "fondo":
        return [(x - 0.5) * 10, 0, -13.0], esc * 1.2
    if plano == "medio":
        return [(x - 0.5) * 5, 0, -4.0], esc
    if plano == "primer_plano":
        return [(x - 0.5) * 1.4, 0, 1.6], esc
    y = float(pr.get("y", 0.86))
    return [(x - 0.5) * ANCHO_ESCENA, 0, _z(y)], esc


def foco_lista(f):
    x, y = f
    return ((x - 0.5) * ANCHO_ESCENA, max(0.25, (0.93 - y) * 5.0), 0.0)


# --- vectores ---------------------------------------------------------------------------------
def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _norm(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def estado(cam_spec, p, t, foco, semilla=0):
    mov = cam_spec.get("mov", "estatico")
    enc = cam_spec.get("encuadre", "medio")
    inten = float(cam_spec.get("intensidad", 1.0))
    d = DIST.get(enc, DIST["medio"])
    tx, ty, tz = foco
    az, fov, roll = 0.0, FOV, 0.0
    e = ease_in_out(p)
    if mov == "estatico":
        d *= 1 - 0.04 * p
    elif mov == "push_in":
        d *= 1 - 0.32 * inten * e
    elif mov == "pull_out":
        d *= 1 + 0.45 * inten * ease_out(p) - 0.15
    elif mov in ("pan_izq", "pan_der"):
        s = -1 if mov == "pan_izq" else 1
        tx += s * 1.4 * inten * (e - 0.5)
        az = s * 0.12 * (e - 0.5)
    elif mov in ("tilt_arriba", "tilt_abajo"):
        k = e if mov == "tilt_arriba" else 1 - e
        ty += 2.8 * inten * k
    elif mov == "zoom_golpe":
        k = ease_out_back(clamp(t / 0.18), 2.0)
        fov = FOV / (1 + 0.5 * inten * k)
    elif mov == "orbita":
        az = (e - 0.5) * 0.55 * inten
        d *= 1 - 0.08 * e
    elif mov == "sacudida":
        d *= 0.95
    if cam_spec.get("entrada") == "whip":
        az += 0.9 * (1 - ease_out(clamp(t / 0.18))) * (1 if semilla % 2 else -1)
    elev = 0.12 * d + 0.12
    px, py, pz = tx + math.sin(az) * d, ty + elev, tz + math.cos(az) * d
    amp = 0.008 + (0.07 * inten * (1 - 0.6 * p) if mov == "sacudida" or cam_spec.get("sacudida") else 0)
    px += amp * ruido1d(t * 6, semilla)
    py += amp * ruido1d(t * 6 + 50, semilla)
    roll = 0.003 * ruido1d(t * 2 + 9, semilla) + (0.02 * ruido1d(t * 16, semilla) if mov == "sacudida" else 0)
    return {"pos": [px, max(0.15, py), pz], "target": [tx, ty, tz], "fov": fov, "roll": roll}


def proyectar(cam, punto, ancho=W, alto=H):
    """Punto del mundo -> (x_px, y_px, profundidad). Igual que THREE.PerspectiveCamera.lookAt."""
    pos, tgt = cam["pos"], cam["target"]
    up = (math.sin(cam["roll"]), math.cos(cam["roll"]), 0.0)
    f = _norm(_sub(tgt, pos))
    r = _norm(_cross(f, up))
    u = _cross(r, f)
    v = _sub(punto, pos)
    z = _dot(v, f)
    if z <= 0.05:
        return None
    fpx = (alto / 2) / math.tan(math.radians(cam["fov"]) / 2)
    return (ancho / 2 + _dot(v, r) / z * fpx, alto / 2 - _dot(v, u) / z * fpx, z)


def escala_personaje(cam, profundidad, alto=H):
    fpx = (alto / 2) / math.tan(math.radians(cam["fov"]) / 2)
    return ALTO_PERSONAJE * fpx / (profundidad * ALTO_LOCAL)
