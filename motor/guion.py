"""Guionista: genera storyboards JSON con la fórmula usando la API de Claude."""
import json
import os
import re

from . import camara, efectos, escenarios, personajes, validar
from .audio import SFX
from .formula import BEATS, REGLAS_GUION, PLANTILLAS_TITULO, PALABRAS_OBJETIVO, PLANOS_OBJETIVO

MODELO = os.environ.get("MOTOR_MODELO", "claude-opus-5-5")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _catalogo():
    return f"""CATÁLOGO (usa SOLO estos valores; lo demás se descarta):
- lugares: {list(escenarios.LUGARES)}
- horas: {list(escenarios.HORAS)}
- props (fondo.props[].tipo): {escenarios.PROPS}
  parámetros útiles: arbol_fruta{{fruta:'#hex', hielo:bool}}, arbol{{pintado:bool}}, fogata{{apagada:bool}},
  lata_leche{{vendada:bool}}, camioneta{{color, hundida:0-1, llantas_bajas:bool}}, carreta{{carga:'leña', giro}},
  fardos{{filas, humo:bool}}, granero{{vapor:bool}}, bomba_agua{{sin_manija:bool}}, vaca{{ojos_traseros:bool, mira:±1}},
  cerca/muro{{largo}}. Cada prop: x (0-1, puede salir de 0-1 para paneos), plano: fondo|medio|frente|primer_plano,
  y (solo frente, 0.80-0.92), escala.
  fondo.mar_sube (0-1) en playa hace subir la marea durante el plano.
- personajes.*: sombrero {personajes.SOMBREROS}, peinado {personajes.PEINADOS}, ropa {personajes.ROPAS},
  accesorios {personajes.ACCESORIOS}, bigote/barba bool, color_sombrero/color_ropa/color_ropa2/color_pelo '#hex',
  rol heroe|rival|secundario|extra, voz (voz edge-tts, solo para quien habla: es-MX-JorgeNeural, es-CO-GonzaloNeural,
  es-AR-TomasNeural, es-US-AlonsoNeural, es-MX-DaliaNeural, es-CO-SalomeNeural), tono '-6Hz'.
- actores[]: id, x (0-1), y (0.70 lejos … 0.86 cerca), escala, mira der|izq, expresion {personajes.EXPRESIONES},
  pose {personajes.POSES}, objeto {personajes.OBJETOS}, accion entrar_izq|entrar_der|salir_izq|salir_der|mover(x2)|saltar,
  sudor bool.
- camara: mov {camara.MOVIMIENTOS}, encuadre {list(camara.ENCUADRES)}, foco (id de actor o [x,y] 0-1),
  intensidad 0.3-1.5, entrada 'whip' (barrido con whoosh en el corte), sacudida bool.
- inserto (tarjeta de datos animada): tipo {efectos.INSERTOS};
  termometro/manometro/contador/regla {{de, a, unidad, etiqueta, min, max}}, reloj {{de, a (horas decimales), texto}},
  comparativa {{items:[{{etiqueta, valor, color, unidad}}], etiqueta}}, flechas {{izq, der}} (fuerza concentrada vs repartida),
  capas {{capas:[{{color, etiqueta}}]}} (corte transversal), texto {{texto, etiqueta, color}}.
- efectos: {efectos.EFECTOS}
- sfx: {SFX} (string, o {{nombre, t (seg desde inicio del plano), vol}})
- destacar: palabras que el subtítulo pinta en amarillo (los números y el apodo ya se pintan solos).
"""


def _sistema():
    beats = "\n".join(f"  {i + 1}. {n} ({a:.0%}-{b:.0%}): {d}" for i, (n, a, b, d) in enumerate(BEATS))
    reglas = "\n".join(f"- {r}" for r in REGLAS_GUION)
    ejemplo = open(os.path.join(RAIZ, "ejemplos", "lechero.json"), encoding="utf-8").read()
    return f"""Eres el guionista y director de un canal de Shorts verticales de curiosidades narradas
con monitos de cabeza blanca redonda sobre escenarios 2.5D. Cada video dura 64-70 s y sigue
una fórmula fija que ya demostró ser viral. Tu salida es un storyboard JSON que un motor
renderiza tal cual: cada plano = un corte de cámara con su frase de narración.

ARCO OBLIGATORIO (en orden, % = posición en el guion):
{beats}

REGLAS DE ESCRITURA:
{reglas}

MÉTRICAS: {PALABRAS_OBJETIVO[0]}-{PALABRAS_OBJETIVO[1]} palabras en total, {PLANOS_OBJETIVO[0]}-{PLANOS_OBJETIVO[1]} planos,
3-16 palabras por plano. Títulos tipo: {PLANTILLAS_TITULO}.

DIRECCIÓN (cómo se ve):
- Cada plano cambia algo: encuadre, movimiento o lugar. Alterna planos medios, primeros planos y detalles.
- zoom_golpe en burlas, revelaciones y '¿Por qué?'. push_in lento en tensión. sacudida cuando algo colapsa.
  pan/tilt para revelar el entorno o la amenaza. entrada 'whip' en saltos de tiempo o de lugar.
- Cada número que el narrador canta debe verse en un inserto (termómetro, manómetro, contador, reloj).
- La explicación científica SIEMPRE lleva un inserto visual (capas, flechas o comparativa).
- El héroe: expresiones confiado/determinado. El rival: presumido/burla al inicio, preocupado/panico al final.
- Las líneas citadas llevan "voz": id del personaje que habla; el resto es "narrador" (omite el campo).
- Usa props del catálogo para que cada escenario se entienda sin texto.

FORMATO DE SALIDA: SOLO el JSON (sin markdown, sin comentarios), con las claves
titulo, apodo, tema, fuente (de dónde sale el dato real), animo_musica (curioso|tension|triunfo),
personajes, planos[] (beat, texto, voz?, fondo, actores, camara, inserto?, efectos?, sfx?, destacar?).

{_catalogo()}

EJEMPLO COMPLETO (mismo formato; NO copies su historia):
{ejemplo}
"""


def _cliente():
    import anthropic
    return anthropic.Anthropic()


def _llamar(mensajes, investigar=False, max_tokens=32000):
    cli = _cliente()
    kw = dict(model=MODELO, max_tokens=max_tokens, system=_sistema(), messages=mensajes,
              output_config={"effort": "high"})
    if investigar:
        kw["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]
    try:
        with cli.beta.messages.stream(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kw) as st:
            msg = st.get_final_message()
    except TypeError:  # SDK antiguo sin 'fallbacks'
        with cli.messages.stream(**kw) as st:
            msg = st.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("El modelo rechazó la solicitud; prueba con otro tema.")
    return msg


def _texto(msg):
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _extraer_json(s):
    s = s.strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    a, b = s.find("{"), s.rfind("}")
    return json.loads(s[a:b + 1])


def generar(tema, investigar=False, rondas=2, extra=""):
    """Genera un guion y lo corrige contra el validador hasta `rondas` veces."""
    pedido = (f"Tema / idea: {tema}\n"
              + ("Primero verifica con búsqueda web que el fenómeno o la historia sean reales y "
                 "anota la fuente en 'fuente'. " if investigar else "")
              + "Escribe el storyboard completo." + (f"\n{extra}" if extra else ""))
    mensajes = [{"role": "user", "content": pedido}]
    msg = _llamar(mensajes, investigar)
    g = _extraer_json(_texto(msg))
    validar.normalizar(g)
    for _ in range(rondas):
        puntaje, fallas = validar.revisar(g)
        if not fallas:
            break
        mensajes += [{"role": "assistant", "content": msg.content},
                     {"role": "user", "content": "El validador de la fórmula marcó esto:\n- " + "\n- ".join(fallas)
                      + "\nDevuelve el JSON completo corregido."}]
        msg = _llamar(mensajes)
        g = _extraer_json(_texto(msg))
        validar.normalizar(g)
    return g


def ideas(n=15, nicho="oficios de campo, mar, historia y naturaleza", evitar=()):
    """Banco de ideas con la fórmula: acción absurda + rival + física real + apodo."""
    pedido = (f"Propón {n} ideas NUEVAS para el canal ({nicho}). Cada una debe ser un fenómeno o una "
              "historia real verificable donde alguien hace algo que parece absurdo y gana. "
              "Evita estas ya usadas: " + "; ".join(evitar) + ". "
              "Responde SOLO un JSON: lista de objetos {titulo, oficio, accion_absurda, rival_y_su_metodo, "
              "apodo, numeros_para_cantar, ciencia_en_una_frase, analogia_domestica, remate, fuente}.")
    cli = _cliente()
    with cli.messages.stream(model=MODELO, max_tokens=16000, output_config={"effort": "high"},
                             system=_sistema().split("FORMATO DE SALIDA")[0],
                             messages=[{"role": "user", "content": pedido}]) as st:
        msg = st.get_final_message()
    s = _texto(msg)
    a, b = s.find("["), s.rfind("]")
    return json.loads(s[a:b + 1])
