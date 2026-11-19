"""La fórmula, extraída de los 10 Shorts del canal analizado (nov 2026).

Todo el motor (guionista, validador y render) lee de aquí, así que si quieres
ajustar el estilo basta con cambiar estos valores.
"""

# --- Métricas duras del formato ------------------------------------------------
DURACION_OBJETIVO = (64, 70)        # segundos; todos los videos duran 1:06-1:10
PALABRAS_OBJETIVO = (175, 225)      # el original ~180 palabras; la voz del motor va a ~200 ppm
PLANOS_OBJETIVO = (22, 32)          # 1 plano cada 2-3 s
SEG_POR_PLANO = (1.6, 3.4)

# --- Arco narrativo (en % de la duración) -----------------------------------------
# Cada guion debe recorrer estos beats en este orden.
BEATS = [
    ("gancho",      0.00, 0.06, "Acción absurda/contraintuitiva + contraste con lo que hacen todos. "
                                "Arranca con 'Este [oficio] [hizo X]...' o directamente con el verbo."),
    ("burla",       0.04, 0.10, "Alguien (vecino/experto) se burla con un APODO que nace de la acción "
                                "('heladero', 'doctor', 'albañil', 'Fosforito'). Frase corta, citada."),
    ("apuesta",     0.08, 0.22, "Qué se pierde y en cuánto tiempo, con números concretos "
                                "('cuatro horas a dos bajo cero', 'en media hora el agua llega aquí', "
                                "'son todos sus ahorros')."),
    ("rival",       0.15, 0.35, "El rival hace lo obvio, caro o de fuerza bruta, y presume."),
    ("proceso",     0.25, 0.50, "Montaje del método casero del héroe con objetos concretos y humildes "
                                "(latas, una ramita, un cartón, una barra de hierro)."),
    ("escalada",    0.35, 0.68, "Cuenta regresiva de números que el narrador 'canta': temperaturas, "
                                "libras, horas, metros ('35 libras, 25, 15'). 'Y lo peor aún no llega'."),
    ("giro",        0.50, 0.72, "El plan del rival colapsa / el del héroe aguanta contra todo pronóstico."),
    ("truco",       0.66, 0.82, "'El truco es que...' o '¿Por qué?': la ciencia en 2-3 frases con una "
                                "analogía doméstica (tacón vs chancla, camisa negra vs sombrero)."),
    ("desenlace",   0.80, 0.94, "Consecuencia visible para el rival; el héroe gana sin presumir."),
    ("remate",      0.92, 1.00, "Callback irónico que reutiliza el apodo o la frase de burla inicial, "
                                "invertida ('La almendra partió el cascanueces', 'Sanito', "
                                "'le pide fuego a Fosforito'). Opcional: cortar la última frase para "
                                "que enlace con la primera (loop)."),
]

# --- Reglas de escritura ----------------------------------------------------
REGLAS_GUION = [
    "Español latino neutro (México), frases de 4 a 12 palabras, presente histórico.",
    "Cero introducciones, cero 'hoy te cuento', cero llamados a suscribirse.",
    "El protagonista casi nunca tiene nombre; se le conoce por el apodo burlón. "
    "Si es un personaje histórico, el nombre real se revela tarde, como premio.",
    "Siempre hay UN rival concreto (vecino, experto, comerciante, comodoro) que representa la intuición equivocada.",
    "Diálogos cortísimos, citados, y el narrador los dice sin 'dijo'.",
    "Mínimo 3 números concretos y una cuenta regresiva cantada.",
    "Exactamente una explicación científica, en lenguaje de cocina, con analogía física.",
    "El apodo aparece al menos 3 veces: burla, escalada y remate.",
    "Historia real o fenómeno real comprobable (física, biología, historia). Nada inventado como 'dato'.",
    "Humor seco de pueblo: el rival termina pagando, pidiendo o copiando al héroe.",
]

PLANTILLAS_TITULO = [
    "¿Por qué este {oficio} {accion_absurda}?",
    "¿Para qué {accion_absurda_plural}?",
    "{objeto} con {detalle_absurdo}",
    "El {objeto_humilde} que venció a {amenaza}",
]

# --- Estilo visual --------------------------------------------------------------
ESTILO = {
    "resolucion": (1080, 1920),
    "fps": 30,
    "contorno": 7,                 # px de línea negra en personajes (a 1080 de ancho)
    "subtitulo_fuente": "Inter Black",
    "subtitulo_tamano": 92,
    "subtitulo_y": 0.70,           # tercio inferior
    "subtitulo_max_palabras": 2,
    "color_destacado": "#FFD84A",  # números y apodo en amarillo
    "voz_narrador": "es-MX-JorgeNeural",
    "velocidad_voz": "+14%",
    "musica_db": -23,
}

# Horario de publicación observado: 1 Short diario entre 14:55 y 21:41 UTC.
PUBLICACION = "1 Short al día, 16:00-19:00 UTC (10:00-13:00 CDMX)"
