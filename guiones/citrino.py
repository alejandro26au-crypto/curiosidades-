#!/usr/bin/env python3
"""Fichas y AUDITOR de guiones de Citrino (fórmula: docs/FORMULA-GUIONES-CITRINO.md).
Adaptado al español del auditor de la fórmula de misterio de Benthara (repo Oceano-animado-, programa/formula.py).

  python3 guiones/citrino.py nuevo "Título" [--bucles 1|2|3]  -> guiones/<titulo>.json (ficha con las etapas vacías)
  python3 guiones/citrino.py auditar guiones/<titulo>.json      -> nota sobre 100 por apartados + debilidades + duración
  python3 guiones/citrino.py texto guiones/<titulo>.json [dibujos/videos/<nombre>/script.txt]  -> guion limpio

Puntos: gancho 15 · promesa 10 · recompensas 15 · bucles 15 · clímax 15 · ritmo 15 · CTA 5 · datos 10.
La nota es una AYUDA: la auditoría de verdad la hago YO leyendo en voz alta (puntos de abandono, redundancias, que
cada revelación pida la siguiente, que todo sea cierto). Con < 90 se reescribe lo débil y se vuelve a auditar.
Las etapas son columna vertebral, no jaula (principio de optimización narrativa): recompensa3/bucle3 opcionales,
bucle2 se puede quitar en temas cortos. La duración NO es fija: sale del guion (se informa a ~170 ppm).
"""
import json
import os
import re
import sys
import unicodedata

PPM = 170
UMBRAL = 90
PUNTOS = {"gancho": 15, "promesa": 10, "recompensas": 15, "bucles": 15, "clímax": 15, "ritmo": 15, "CTA": 5, "datos": 10}
OPCIONALES = {"recompensa3", "bucle3", "bucle2"}
ETAPAS = [
    ("hook", "HOOK (0-3 s): afirmación, pregunta o situación que despierta curiosidad YA. Primera frase ≤ 10 palabras, sin introducción."),
    ("promesa", "PROMESA: qué descubrirá el espectador si sigue viendo, sin desvelarlo."),
    ("recompensa1", "RECOMPENSA 1: el primer descubrimiento relevante, concreto y visual (cifra, lugar, fecha), y pronto."),
    ("bucle1", "BUCLE 1: una incógnita nueva relacionada con lo anterior (pregunta o «Pero…» que deja algo abierto)."),
    ("recompensa2", "RECOMPENSA 2: información nueva que profundiza o CAMBIA lo que creíamos, conectada con el bucle 1."),
    ("bucle2", "BUCLE 2: eleva la expectativa hacia una revelación más importante («Y eso no es lo más raro.»)."),
    ("recompensa3", "(OPCIONAL) RECOMPENSA 3: solo si el tema lo pide. Información nueva, no relleno."),
    ("bucle3", "(OPCIONAL) BUCLE 3: solo con recompensa 3. La última puerta antes del clímax."),
    ("climax", "CLÍMAX (65-90 % del guion): el descubrimiento principal; resuelve todas las incógnitas abiertas."),
    ("cta", "CTA: cierre breve y natural (≤ 14 palabras) con UNA sola acción; mejor si enlaza con el gancho (loop)."),
]
INTRO = r"^\s*(¿?sab[ií]as que|hoy te|hoy vamos|en este v[ií]deo|bienvenid|hola|alguna vez te has preguntado)"
_PROMESA = r"\b(vas a (ver|descubrir|saber|entender)|descubrir[aá]s|al final|te (cuento|explico)|esto es lo que|la respuesta|lo que (encontraron|descubrieron|pas[oó])|por qu[eé]|c[oó]mo|qu[eé] (pas[oó]|hay))\b"
_ABRE = r"(\?|\b(pero|aunque|sin embargo|todav[ií]a|nadie|nunca|hasta que|excepto|qu[eé]|por qu[eé]|c[oó]mo|algo|alguien|la pregunta|misterio|raro|extraño|el problema)\b)"
_SUBE = r"\b(ni siquiera|lo m[aá]s (raro|extraño|grave|sorprendente|loco)|lo peor|el verdadero|la verdadera|la verdad|no era|no fue|y (empeora|hay m[aá]s)|ah[ií] (fue|es) cuando|entonces)\b"
_REVELA = r"\b(result[oó]|resulta que|era|fue|la (respuesta|raz[oó]n|verdad|clave) (es|era|fue)|el (secreto|truco) (es|era)|porque|por eso|al final|por fin|los cient[ií]ficos (descubrieron|confirmaron|creen|piensan)|la explicaci[oó]n|el culpable)\b"
_RELLENO = r"\b(b[aá]sicamente|literalmente|realmente|o sea|bueno|pues nada|la verdad es que|digamos|tipo)\b"
_HIPOTESIS = r"\b(podr[ií]a|quiz[aá]s?|tal vez|probablemente|se cree|los cient[ií]ficos (creen|piensan|sospechan)|una teor[ií]a|la teor[ií]a|dicen que|leyenda|nadie lo sabe)\b"
_ACCIONES = r"\b(suscr[ií]bete|s[ií]gueme|comenta|d[eé]jame|dime|cu[eé]ntame|escr[ií]beme|dale (like|me gusta)|comparte|guarda|etiqueta|m[aá]ndaselo|env[ií]aselo|mira)\b"
_CIFRA = r"\d|\b(un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|quince|veinte|treinta|cuarenta|cincuenta|cien|ciento|mil|mill[oó]n|millones|mitad|doble|triple)\b"


def quita_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", quita_tildes(s.lower())).strip("-")


def frases(t):
    return [f for f in re.split(r"(?<=[.!?…])\s+", t.strip()) if f]


def pal(t):
    return [w for w in t.split() if re.sub(r"\W", "", w)]


def texto(fi, k):
    return (next((e.get("texto", "") for e in fi.get("etapas", []) if e.get("etapa") == k), "") or "").strip()


def nuevo(titulo, bucles=2):
    et = [{"etapa": k, "que_hace": d, "texto": ""} for k, d in ETAPAS
          if not (k in ("recompensa3", "bucle3") and bucles < 3) and not (k == "bucle2" and bucles < 2)]
    fi = {"titulo": titulo, "tema": "", "dato": "el hecho central comprobado, en una línea", "hipotesis": False,
          "etapas": et, "fuentes": [], "ritmo": "pausas (…), énfasis (MAYÚSCULAS) y ritmo para la locución", "notas": ""}
    os.makedirs("guiones", exist_ok=True)
    ruta = os.path.join("guiones", slug(titulo) + ".json")
    if os.path.exists(ruta):
        sys.exit(f"ya existe: {ruta}")
    json.dump(fi, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("✓", ruta)


def auditar(fi):
    """(nota, {apartado: (puntos, máximo, [debilidades])}, fallos, palabras)."""
    t = {k: texto(fi, k) for k, _ in ETAPAS}
    todo = " ".join(t[k] for k, _ in ETAPAS if t[k])
    n = len(pal(todo))
    fallos = [f"Falta «{k}»: {ayuda}" for k, ayuda in ETAPAS if not t[k] and k not in OPCIONALES]
    d = {k: [m, []] for k, m in PUNTOS.items()}

    def quita(ap, pts, msg):
        d[ap][0] = max(0, d[ap][0] - pts); d[ap][1].append(msg)

    # GANCHO
    primera = frases(t["hook"])[0] if t["hook"] else ""
    if len(pal(primera)) > 10: quita("gancho", 6, f"La primera frase del gancho tiene {len(pal(primera))} palabras (máx. 10: cabe en 0-3 s).")
    if re.search(INTRO, t["hook"], re.I): quita("gancho", 9, "El gancho presenta («¿Sabías que…?», «Hoy te…»): empieza por lo más raro.")
    if re.search(_REVELA, t["hook"], re.I) and re.search(r"\b(porque|resulta que|por eso)\b", t["hook"], re.I): quita("gancho", 6, "El gancho ya explica (porque / resulta que): guarda la respuesta.")
    if t["hook"] and not re.search(_CIFRA + r"|!|\?|\b(nunca|nadie|solo|imposible|raro|extraño|primer|[uú]ltim|desapareci|encontr|descubri)", t["hook"], re.I):
        quita("gancho", 4, "El gancho no choca (sin cifra, pregunta, «nunca», «nadie», «desapareció»…): hazlo más raro o concreto.")
    # PROMESA
    if t["promesa"] and not re.search(_PROMESA, t["promesa"], re.I): quita("promesa", 5, "La promesa no anticipa nada («vas a ver por qué…», «esto es lo que encontraron»).")
    if re.search(r"\b(porque|resulta que|la respuesta es)\b", t["promesa"], re.I): quita("promesa", 5, "La promesa desvela la respuesta: anticipa, no resuelvas.")
    if len(pal(t["promesa"])) > 22: quita("promesa", 3, "Promesa larga (> 22 palabras): una o dos frases.")
    # RECOMPENSAS
    for k in ("recompensa1", "recompensa2", "recompensa3"):
        if t[k] and not re.search(_CIFRA, t[k], re.I): quita("recompensas", 4, f"«{k}» sin cifra ni dato concreto: número, fecha, lugar o tamaño.")
        if t[k] and len(pal(t[k])) < 8: quita("recompensas", 3, f"«{k}» muy corta: la recompensa tiene que saciar algo.")
    if t["recompensa2"] and not re.search(r"\b(pero|en realidad|de hecho|resulta|en cambio|no|ni|incluso|eso|esto|ese|esa)\b", t["recompensa2"], re.I):
        quita("recompensas", 4, "La recompensa 2 no se conecta ni cambia lo anterior («Pero…», «En realidad…», «Eso no…»).")
    antes = sum(len(pal(t[k])) for k in ("hook", "promesa"))
    if n and t["recompensa1"] and antes / n > 0.25: quita("recompensas", 4, f"La primera recompensa llega tarde ({antes} de {n} palabras antes): adelántala.")
    # BUCLES
    if t["bucle1"] and not re.search(_ABRE, t["bucle1"], re.I): quita("bucles", 7, "El bucle 1 no abre ninguna incógnita (pregunta, «Pero…», «Nadie sabía…»).")
    if t["bucle2"] and not (re.search(_SUBE, t["bucle2"], re.I) or re.search(_ABRE, t["bucle2"], re.I)): quita("bucles", 7, "El bucle 2 no eleva la expectativa («Y eso no es lo más raro.»).")
    if re.search(r"\b(resulta que|la respuesta (es|era)|por eso)\b", t["bucle1"] + " " + t["bucle2"], re.I): quita("bucles", 4, "Un bucle desvela en vez de abrir: deja la respuesta para después.")
    if t["bucle1"] and t["bucle1"].lower() == t["bucle2"].lower(): quita("bucles", 6, "Los dos bucles son iguales: el segundo tiene que ir a más.")
    if re.search(r"qu[eé]date hasta el final|no te lo vas a creer|espera a ver|lo mejor viene ahora", todo, re.I): quita("bucles", 5, "Anticipación vacía («quédate hasta el final», «no te lo vas a creer»): bucle artificial, quítala.")
    # CLÍMAX
    if t["climax"] and not re.search(_REVELA + r"|\d", t["climax"], re.I): quita("clímax", 6, "El clímax no suena a revelación («Resulta que…», «La razón era…», un dato que lo resuelve).")
    if n and t["climax"]:
        pos = sum(len(pal(t[k])) for k in ("hook", "promesa", "recompensa1", "bucle1", "recompensa2", "bucle2", "recompensa3", "bucle3")) / n
        if not 0.6 <= pos <= 0.92: quita("clímax", 5, f"El clímax empieza al {pos:.0%} del guion (ideal 65-90 %).")
    if t["climax"] and len(pal(t["climax"])) < 10: quita("clímax", 3, "Clímax corto: la revelación merece 2-3 frases visuales.")
    clave = {w for w in re.sub(r"\W+", " ", quita_tildes((t["hook"] + " " + t["promesa"]).lower())).split() if len(w) > 4}
    if clave and t["climax"] and not clave & set(re.sub(r"\W+", " ", quita_tildes((t["climax"] + " " + t["cta"]).lower())).split()):
        quita("clímax", 4, "El clímax no retoma ninguna palabra clave del gancho ni de la promesa: ¿se cumple lo prometido?")
    # RITMO
    largas = [f for f in frases(todo) if len(pal(f)) > 16]
    if largas: quita("ritmo", min(6, 2 * len(largas)), f"{len(largas)} frase(s) de más de 16 palabras: pártelas («{largas[0][:40]}…»).")
    rel = [m.group(0) for m in re.finditer(_RELLENO, todo, re.I)]
    if len(rel) > 1: quita("ritmo", 3, f"Relleno: {', '.join(sorted(set(x.lower() for x in rel)))}. Quítalo.")
    inicios = [quita_tildes(pal(f)[0].lower().strip("¡¿")) for f in frases(todo) if pal(f)]
    rep = [w for w in set(inicios) if inicios.count(w) > 3 and w not in ("y", "el", "la", "pero")]
    if rep: quita("ritmo", 2, f"Demasiadas frases empiezan igual: {', '.join(rep)}.")
    for k, _ in ETAPAS:  # cada tramo justifica quedarse: dato, pregunta o avance
        if t[k] and k != "cta" and not re.search(_CIFRA + "|!|" + _ABRE + "|" + _REVELA + "|" + _SUBE, t[k], re.I):
            quita("ritmo", 2, f"Posible punto de abandono en «{k}»: no trae dato, pregunta ni avance.")
    fr = [re.sub(r"\W+", " ", quita_tildes(f.lower())).split() for f in frases(todo)]
    for i in range(len(fr)):
        for j in range(i + 1, len(fr)):
            a_, b_ = {w for w in fr[i] if len(w) > 3}, {w for w in fr[j] if len(w) > 3}
            if len(a_) >= 3 and len(a_ & b_) / max(1, min(len(a_), len(b_))) > 0.7 and fr[i] != fr[j]:
                quita("ritmo", 2, f"Redundancia: «{' '.join(fr[j])[:40]}…» repite una frase anterior."); break
    if re.search(r"[%&/=+]|\b\d{5,}\b", todo): quita("ritmo", 2, "Símbolos o cifras largas que se leen mal en voz alta: escríbelos como se dicen («por ciento», «mil»).")
    # CTA: breve, natural, UNA acción
    acc = {quita_tildes(m.group(0).lower()) for m in re.finditer(_ACCIONES, t["cta"], re.I)}
    if len(acc) > 1: quita("CTA", 3, f"El CTA pide varias acciones ({', '.join(sorted(acc))}): solo una.")
    if len(pal(t["cta"])) > 14: quita("CTA", 2, "CTA largo: ≤ 14 palabras.")
    if len(re.findall(_ACCIONES, todo.replace(t["cta"], ""), re.I)) > 0: quita("CTA", 2, "Hay llamadas a la acción fuera del CTA: solo al final.")
    # DATOS
    fuentes = fi.get("fuentes") or []
    if not fuentes: fallos.append("Faltan «fuentes»: verifica cada dato en fuentes fiables.")
    elif len(fuentes) < 2: quita("datos", 4, "Solo una fuente: contrasta los datos clave con al menos dos.")
    if not fi.get("dato") or fi.get("dato", "").startswith("el hecho central"): quita("datos", 3, "Falta «dato»: el hecho central comprobado, en una línea.")
    if fi.get("hipotesis") and not re.search(_HIPOTESIS, todo, re.I):
        quita("datos", 5, "La ficha marca una hipótesis, pero el guion la cuenta como hecho: di «se cree…», «los científicos piensan…».")
    titulo = (fi.get("titulo") or "").strip()
    if titulo and not 4 <= len(titulo.split()) <= 7: quita("gancho", 2, f"Título de {len(titulo.split())} palabras: 4-7, con curiosidad.")
    nota = sum(v[0] for v in d.values())
    return nota, {k: (v[0], PUNTOS[k], v[1]) for k, v in d.items()}, fallos, n


def informe(ruta):
    fi = json.load(open(ruta, encoding="utf-8"))
    nota, desg, fallos, n = auditar(fi)
    print(f"\n{fi.get('titulo')} — {n} palabras · duración estimada ≈ {n / PPM * 60:.0f} s (a {PPM} ppm; la marca el guion)")
    for k, (p, m, ms) in desg.items():
        print(f"  {k:<12}{p:>3}/{m}")
        for x in ms:
            print(f"      ⚠ {x}")
    print(f"  {'NOTA':<12}{nota:>3}/100  " + ("✓ pasa (y ahora léelo en voz alta)" if nota >= UMBRAL and not fallos else "✗ corregir y volver a auditar"))
    for x in fallos:
        print("  ✗", x)
    return nota


def limpio(fi):
    return " ".join(texto(fi, k) for k, _ in ETAPAS if texto(fi, k))


def main():
    a = sys.argv
    if len(a) < 3:
        sys.exit(__doc__)
    if a[1] == "nuevo":
        nuevo(a[2], int(a[a.index("--bucles") + 1]) if "--bucles" in a else 2)
    elif a[1] == "auditar":
        informe(a[2])
    elif a[1] == "texto":
        t = limpio(json.load(open(a[2], encoding="utf-8")))
        if len(a) > 3:
            open(a[3], "w", encoding="utf-8").write(t + "\n"); print("✓", a[3])
        else:
            print(t)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
