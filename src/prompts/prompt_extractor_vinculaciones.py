"""
Prompt para extraer información de Vinculaciones.
Alimenta: Vinculaciones y Referencias.
Fuente MVP: Documento proporcionado por el Director (en V2: servicio Tronador P&G).
"""

SYSTEM_PROMPT_VINCULACIONES = """Eres un analista de riesgos de Seguros Bolívar.
Tu tarea es extraer información sobre vinculaciones comerciales y referencias de un cliente
a partir de los documentos proporcionados.

Debes devolver SIEMPRE un JSON válido con la estructura indicada.
Si un campo no se encuentra en el documento, usa null.
No inventes datos. Solo extrae lo que está explícitamente en el documento."""


def get_prompt_vinculaciones() -> str:
    return """Analiza el documento de vinculaciones adjunto y extrae la siguiente información en formato JSON:

{
    "vinculaciones_comerciales": [
        {
            "empresa_vinculada": "Nombre de la empresa",
            "tipo_vinculacion": "Tipo de relación (accionista, filial, subordinada, etc.)",
            "porcentaje_participacion": "% de participación si aplica",
            "estado": "Activa/Inactiva"
        }
    ],
    "referencias_bancarias": [
        {
            "entidad": "Nombre del banco",
            "tipo_producto": "Tipo de producto financiero",
            "calificacion": "Calificación crediticia si existe"
        }
    ],
    "referencias_comerciales": [
        {
            "empresa": "Nombre de la empresa que da la referencia",
            "relacion": "Tipo de relación comercial",
            "antiguedad": "Tiempo de la relación"
        }
    ],
    "resumen": "Resumen de la situación de vinculaciones y referencias del cliente."
}

IMPORTANTE:
- Identifica TODAS las vinculaciones que aparezcan (societarias, comerciales, familiares)
- Clasifica el tipo de vinculación
- Incluye referencias bancarias y comerciales si están disponibles"""
