"""Puesta en escena del Short de fresas (planos, props, cámara, personajes).

Reescribe guiones/fresas.json conservando título, voces y "voz_externa"; los textos
deben coincidir con el guion actual (las voces de ElevenLabs están cortadas por plano).
Uso:  python guiones/fresas_planos.py
"""
import os
RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fresas.json")
import json
N = "noche"
def F(*props, lugar="huerto", hora=N, **kw): return dict(lugar=lugar, hora=hora, props=list(props), **kw)
def fresal(x, plano="medio", **k): return dict(tipo="fresal", x=x, plano=plano, **k)
def fog(x, plano="medio", **k): return dict(tipo="fogata", x=x, plano=plano, **k)
def pr(t, x, plano="medio", **k): return dict(tipo=t, x=x, plano=plano, **k)
def A(id, x, expresion, pose="idle", **k): return dict(id=id, x=x, expresion=expresion, pose=pose, **k)
GR = lambda **k: pr("fresa_grande", 0.5, "frente", y=0.86, **k)
valle = lambda apag=False: [fog(x, "fondo", **({"apagandose": True, "retraso": i * 0.12} if apag else {})) for i, x in enumerate((-0.3, 0.1, 0.45, 0.8, 1.15))] + [pr("iglesia", 1.25, "fondo", escala=0.7)]

planos = [
 dict(beat="gancho", texto="Este agricultor cubrió sus fresas de hielo mientras el pueblo prendía fogatas.",
      fondo=F(fresal(0.55, "frente", y=0.88, hielo=True, goteo=True, largo=700), fog(0.05, "fondo"), fog(0.95, "fondo"), pr("iglesia", 0.75, "fondo")),
      actores=[A("heroe", 0.28, "determinado", "trabajar", objeto="balde", mira="der")],
      camara=dict(mov="push_in", foco="heroe"), efectos=["escarcha"], sfx=["agua"], destacar=["hielo", "fogatas"]),
 dict(beat="burla", voz="vecino", texto="¿Qué vendes, Paletero? ¿Raspados de fresa?",
      fondo=F(fog(0.5, "frente", y=0.84), pr("cerca", 0.5, "medio", largo=1600), pr("tocon", 0.2, "frente", y=0.85)),
      actores=[A("vecino", 0.3, "burla", "sentado", mira="der"), A("amigo1", 0.72, "burla", "reir", mira="izq")],
      camara=dict(mov="zoom_golpe", foco="vecino"), sfx=["risa", "fuego"]),
 dict(beat="apuesta", texto="Esta noche va a bajar a cuatro bajo cero.",
      fondo=F(*valle(), fresal(0.5, "medio", largo=1200, hielo=True)),
      actores=[], camara=dict(mov="tilt_abajo", encuadre="general", foco=[0.5, 0.55]),
      inserto=dict(tipo="termometro", de=3, a=-4, unidad="°C", etiqueta="Esta noche", min=-6, max=6), efectos=["escarcha"], sfx=["viento", {"nombre": "campana", "t": 0.4}]),
 dict(beat="apuesta", texto="A dos bajo cero, la fresa se congela y se vuelve puré.",
      fondo=F(pr("fresa_partida", 0.5, "frente", y=0.86, estado="congelando")), actores=[], camara=dict(mov="push_in", encuadre="medio", foco=[0.5, 0.8], intensidad=1.4),
      efectos=["escarcha"], sfx=["hielo", {"nombre": "hielo", "t": 1.2}]),
 dict(beat="rival", texto="Los vecinos prenden fogatas entre los surcos.",
      fondo=F(pr("carreta", 0.62, "frente", y=0.84, carga="leña"), fog(0.2, "medio"), fog(0.85, "medio"), fresal(0.5, "medio", largo=1000)),
      actores=[A("vecino", 0.38, "presumido", "manos_cadera", mira="der", accion="entrar_izq")],
      camara=dict(mov="seguimiento", foco="vecino", entrada="whip"), sfx=["fuego"]),
 dict(beat="rival", voz="vecino", texto="Fuego, Paletero. Así se le gana al frío.",
      fondo=F(fog(0.55, "frente", y=0.84), pr("carreta", 0.9, "medio", carga="leña")),
      actores=[A("vecino", 0.33, "confiado", "brazos_cruzados", mira="der")],
      camara=dict(mov="push_in", encuadre="americano", foco="vecino"), sfx=["fuego"]),
 dict(beat="proceso", texto="Él solo tiene un pozo, una cubeta y unas latas viejas.",
      fondo=F(pr("estanque", 0.68, "frente", y=0.9, helado=True), pr("pozo", 0.9, "medio"), pr("cubeta", 0.25, "frente", y=0.88)),
      actores=[A("heroe", 0.42, "preocupado", "rascarse", objeto="balde", mira="der")],
      camara=dict(mov="pan_izq", encuadre="medio", foco="heroe"), efectos=["escarcha"]),
 dict(beat="proceso", texto="Les hace agujeros y las cuelga sobre los surcos.",
      fondo=F(pr("tocon", 0.55, "frente", y=0.86), fresal(0.5, "medio", goteo=True, largo=700)),
      actores=[A("heroe", 0.38, "determinado", "trabajar", objeto="martillo", mira="der")],
      camara=dict(mov="push_in", encuadre="americano", foco="heroe"), sfx=["golpe", {"nombre": "golpe", "t": 0.6}, {"nombre": "golpe", "t": 1.2}]),
 dict(beat="proceso", texto="Gota a gota, toda la noche, sin parar.",
      fondo=F(fresal(0.5, "frente", y=0.88, goteo=True, hielo_crece=True, largo=900)),
      actores=[A("heroe", 0.2, "determinado", "caminar", objeto="balde", mira="der", accion="mover", x2=0.75)],
      camara=dict(mov="seguimiento", encuadre="medio", foco="heroe"), sfx=["agua"], destacar=["Gota"]),
 dict(beat="escalada", texto="A las once, cada fresa ya trae su capa de hielo.",
      fondo=F(GR(estado="buena", hielo=True)), actores=[], camara=dict(mov="orbita", encuadre="detalle", foco=[0.5, 0.8]),
      inserto=dict(tipo="reloj", de=21, a=23, texto="11 de la noche"), efectos=["escarcha"], sfx=["campana", "hielo"]),
 dict(beat="escalada", texto="A la una, junto al fuego, hace un grado.",
      fondo=F(fog(0.5, "frente", y=0.84), pr("cerca", 0.5, "medio", largo=1600)),
      actores=[A("vecino", 0.25, "feliz", "sentado", objeto="malvavisco", mira="der"), A("amigo1", 0.75, "feliz", "sentado", objeto="malvavisco", mira="izq")],
      camara=dict(mov="pan_der", encuadre="general", foco=[0.5, 0.7]),
      inserto=dict(tipo="termometro", de=3, a=1, unidad="°C", etiqueta="Fogatas", min=-6, max=6, posicion="der"), sfx=["fuego"]),
 dict(beat="escalada", texto="Junto al Paletero, cero. Y de ahí no baja.",
      fondo=F(fresal(0.55, "frente", y=0.87, hielo=True, goteo=True, largo=600)),
      actores=[A("heroe", 0.3, "determinado", "cargar", objeto="balde", mira="der", sudor=True)],
      camara=dict(mov="push_in", encuadre="medio", foco="heroe"),
      inserto=dict(tipo="termometro", de=1, a=0, unidad="°C", etiqueta="Bajo el hielo", min=-6, max=6, posicion="der"), efectos=["escarcha"]),
 dict(beat="escalada", voz="vecino", texto="Ya duérmete, Paletero. Eso ya se murió.",
      fondo=F(pr("cerca", 0.5, "frente", y=0.84, largo=1600), fog(0.85, "medio")),
      actores=[A("vecino", 0.35, "burla", "señalar", mira="der"), A("amigo2", 0.62, "burla", "reir", mira="der")],
      camara=dict(mov="zoom_golpe", encuadre="americano", foco="vecino"), sfx=["risa"]),
 dict(beat="escalada", texto="Y lo peor todavía no llega.",
      fondo=F(pr("estanque", 0.55, "frente", y=0.9, helado=True), pr("pozo", 0.9, "medio")),
      actores=[A("heroe", 0.45, "determinado", "trabajar", objeto="balde", mira="der")],
      camara=dict(mov="pull_out", encuadre="medio", foco="heroe", sacudida=True), efectos=["nieve"], sfx=["hielo", {"nombre": "golpe", "t": 0.5}]),
 dict(beat="giro", texto="A las tres se acaba la leña. Queman cajas, después la cerca.",
      fondo=F(fog(0.6, "frente", y=0.85), pr("carreta", 0.85, "medio"), pr("cerca", 0.3, "medio", largo=500)),
      actores=[A("vecino", 0.3, "preocupado", "trabajar", objeto="martillo", mira="der"), A("amigo1", 0.75, "panico", "cargar", objeto="rama", mira="izq")],
      camara=dict(mov="seguimiento", foco="vecino", entrada="whip"),
      inserto=dict(tipo="reloj", de=1, a=3, texto="3 de la mañana", posicion="der"), sfx=["golpe", {"nombre": "golpe", "t": 0.8}, "tictac"]),
 dict(beat="giro", texto="Una por una, las fogatas se apagan.",
      fondo=F(*[fog(x, "medio", apagandose=True, retraso=i * 0.13) for i, x in enumerate((0.1, 0.35, 0.6, 0.85))], fresal(0.5, "frente", y=0.9, largo=1200)),
      actores=[], camara=dict(mov="pan_der", encuadre="general", foco=[0.5, 0.7]), efectos=[], sfx=["aire"]),
 dict(beat="giro", texto="Tres bajo cero. Cuatro bajo cero.",
      fondo=F(fog(0.5, "frente", y=0.85, apagada=True), fresal(0.5, "medio", largo=900)),
      actores=[A("vecino", 0.38, "panico", "temblar", objeto="malvavisco_helado", mira="der")],
      camara=dict(mov="estatico", encuadre="americano", foco="vecino", sacudida=True),
      inserto=dict(tipo="termometro", de=-1, a=-4, unidad="°C", etiqueta="Fresas del vecino", min=-6, max=6, posicion="der"), efectos=["nieve"], sfx=["hielo", "viento"]),
 dict(beat="truco", texto="El truco es que el agua, al congelarse, suelta calor.",
      fondo=F(GR(estado="buena", hielo=True)), actores=[], camara=dict(mov="zoom_golpe", encuadre="detalle", foco=[0.5, 0.82]),
      inserto=dict(tipo="capas", capas=[{"color": "#DFF4FF", "etiqueta": "Hielo (suelta calor)"}, {"color": "#8FD0FF", "etiqueta": "Agua que se congela"}, {"color": "#E3243B", "etiqueta": "Fresa a 0 °C"}]),
      sfx=["ding"], destacar=["suelta", "calor"]),
 dict(beat="truco", texto="Cada gota que se congela le regala calor.",
      fondo=F(fresal(0.5, "frente", y=0.86, hielo=True, goteo=True, largo=300)),
      actores=[], camara=dict(mov="push_in", encuadre="detalle", foco=[0.5, 0.83]), efectos=["destello"], sfx=["agua"]),
 dict(beat="truco", texto="Mientras siga goteando, la fresa se queda en cero. Nunca llega a dos.",
      fondo=F(fresal(0.5, "medio", hielo=True, goteo=True, largo=900)),
      actores=[], camara=dict(mov="orbita", encuadre="medio", foco=[0.5, 0.75]),
      inserto=dict(tipo="texto", texto="0 °C", etiqueta="La fresa bajo el hielo", color="#4AA3DF")),
 dict(beat="desenlace", texto="Al amanecer, los vecinos muerden sus fresas. Puro puré aguado.",
      fondo=F(fresal(0.5, "frente", y=0.9, mala=True, largo=900), fog(0.85, "medio", apagada=True), hora="amanecer"),
      actores=[A("vecino", 0.35, "triste", "idle", objeto="fresa_mordida", mira="der"), A("amigo1", 0.7, "preocupado", "agachado", objeto="fresa_mala", mira="izq")],
      camara=dict(mov="push_in", encuadre="general", foco=[0.5, 0.7], entrada="whip"),
      sfx=["error"]),
 dict(beat="desenlace", texto="Y él sigue regando hasta que el sol derrite el hielo.",
      fondo=F(fresal(0.55, "frente", y=0.87, derrite=True, goteo=True, largo=800), hora="amanecer"),
      actores=[A("heroe", 0.3, "confiado", "trabajar", objeto="balde", mira="der")],
      camara=dict(mov="pan_der", encuadre="medio", foco="heroe"), efectos=["vapor"], sfx=["agua"]),
 dict(beat="desenlace", texto="Debajo, fresas rojas, firmes y dulces.",
      fondo=F(GR(estado="buena", derrite=True), hora="dia"),
      actores=[], camara=dict(mov="push_in", encuadre="detalle", foco=[0.5, 0.82]),
      efectos=["destello"], sfx=["ding"], destacar=["rojas", "firmes", "dulces"]),
 dict(beat="remate", texto="Esa semana, el pueblo hizo fila con el Paletero.",
      fondo=F(pr("puesto", 0.62, "medio", fresas=True), pr("canasta", 0.85, "frente", y=0.86), hora="dia", lugar="pueblo"),
      actores=[A("heroe", 0.86, "feliz", "saludar", objeto="canasta", mira="izq"), A("vecina", 0.55, "feliz", "idle", objeto="monedas", mira="der"),
               A("nino", 0.35, "feliz", "idle", mira="der"), A("amigo2", 0.15, "neutral", "idle", mira="der")],
      camara=dict(mov="pan_der", encuadre="general", foco=[0.55, 0.75]), sfx=["campana"]),
 dict(beat="remate", voz="vecino", texto="Paletero... ¿me vende unas de fresa?",
      fondo=F(pr("puesto", 0.65, "medio", fresas=True), hora="dia", lugar="pueblo"),
      actores=[A("vecino", 0.35, "preocupado", "rascarse", objeto="monedas", mira="der"), A("heroe", 0.75, "confiado", "brazos_cruzados", mira="izq")],
      camara=dict(mov="zoom_golpe", encuadre="americano", foco="vecino"), sfx=["pop"]),
]
viejo = json.load(open(RUTA, encoding="utf-8"))
assert [p["texto"] for p in viejo["planos"]] == [p["texto"] for p in planos], "los textos cambiaron"
viejo["planos"] = planos
pj = viejo["personajes"]
pj["amigo1"] = dict(rol="extra", sombrero="gorra", color_sombrero="#2E5E3E", ropa="chaleco", color_ropa="#C9A86A", color_ropa2="#5A4632", bigote=True)
pj["amigo2"] = dict(rol="extra", sombrero="boina", color_sombrero="#3A3A40", ropa="abrigo", color_ropa="#4B5D7A", barba=True)
json.dump(viejo, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
