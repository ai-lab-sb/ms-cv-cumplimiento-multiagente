"""
Prompt para extraer información de SISCONC.
Alimenta: SISCONC (exposiciones y siniestros).
Fuente MVP: Documento proporcionado por el Director (en V2: servicio SISCONC).
"""

SYSTEM_PROMPT_SISCONC = """Eres un analista de riesgos de Seguros Bolívar.
Tu tarea es extraer información sobre exposiciones y siniestros de un cliente
a partir de la consulta SISCONC proporcionada.

Debes devolver SIEMPRE un JSON válido con la estructura indicada.
Si un campo no se encuentra en el documento, usa null.
No inventes datos. Solo extrae lo que está explícitamente en el documento."""


def get_prompt_sisconc() -> str:
    return """Analiza el documento SISCONC adjunto y extrae la siguiente información en formato JSON:

{
    "tiene_siniestros": true/false,
    "cantidad_siniestros": 0,
    "detalle_siniestros": [
        {
            "aseguradora": "Nombre de la aseguradora",
            "ramo": "Ramo del seguro",
            "fecha": "Fecha del siniestro",
            "valor_reclamado": "$0",
            "estado": "Abierto/Cerrado/En proceso"
        }
    ],
    "exposiciones": [
        {
            "aseguradora": "Nombre de la aseguradora",
            "ramo": "Ramo del seguro",
            "valor_asegurado": "$0",
            "vigencia": "Fecha inicio - Fecha fin"
        }
    ],
    "resumen": "Resumen general de la situación del cliente en SISCONC: cantidad de exposiciones activas, historial de siniestros y cualquier señal de alerta."
}

IMPORTANTE:
- Identifica TODOS los siniestros o reclamaciones que aparezcan
- Clasifica el estado de cada siniestro
- Si no hay siniestros, indica tiene_siniestros como false
- El resumen debe ser un párrafo conciso con la valoración general"""
