// EJEMPLO. Lo reescribe tiempos_es.py con la voz real (python3 ../../herramientas/tiempos_es.py voice.mp3 script.txt es).
// FRASES = [fotograma inicio, fotograma fin, texto] · PAL = [palabra, fotograma inicio, fotograma fin] (30 fps)
export const FRASES = [[0, 40, "¡Un pozo en la plaza!"], [45, 75, "¡Diez metros!"], [85, 150, "El vecino apostó... ¡cien monedas!"], [160, 200, "Y el chico se rió."], [205, 238, "Al atardecer... silencio."]];
export const PAL = [["¡Un", 0, 6], ["pozo", 6, 16], ["en", 16, 20], ["la", 20, 24], ["plaza!", 24, 40], ["¡Diez", 45, 58], ["metros!", 58, 75], ["El", 85, 89], ["vecino", 89, 102], ["apostó...", 102, 118], ["¡cien", 124, 136], ["monedas!", 136, 150], ["Y", 160, 163], ["el", 163, 167], ["chico", 167, 178], ["se", 178, 182], ["rió.", 182, 200], ["Al", 205, 209], ["atardecer...", 209, 222], ["silencio.", 226, 238]];
export const DURACION = 240; // fotogramas (voz + ~0,5 s)
