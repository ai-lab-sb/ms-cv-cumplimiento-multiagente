"""
Prompt para extraer información de Cupo y Cúmulo.
Alimenta: Cupo y Cúmulo.
Fuente MVP: Documento proporcionado por el Director (en V2: servicios Emmis + Simon).
"""

SYSTEM_PROMPT_CUPO = """Eres un analista de riesgos de Seguros Bolívar.
Tu tarea es extraer información sobre cupo de crédito y cúmulo asegurado de un cliente
a partir de los documentos proporcionados.

Debes devolver SIEMPRE un JSON válido con la estructura indicada.
Si un campo no se encuentra en el documento, usa null.
No inventes datos. Solo extrae lo que está explícitamente en el documento."""


def get_prompt_cupo() -> str:
    return """Analiza el documento de cupo y cúmulo adjunto y extrae la siguiente información en formato JSON:

{
    "calificador": {
        "z_score": null,
        "seriedad_oferta_pct": null,
        "cumplimiento_afines_pct": null
    },
    "cupo_propuesto": "$0",
    "cupo_seguros_bolivar": "$0",
    "cumulo": "$0",
    "detalle_cumulo": [
        {
            "poliza": "Número de póliza",
            "ramo": "Ramo",
            "valor_asegurado": "$0",
            "vigencia": "Vigencia"
        }
    ],
    "observaciones": "Observaciones relevantes sobre la relación entre cupo aprobado y exposición máxima."
}

IMPORTANTE:
- Identifica el cupo aprobado y el cúmulo actual
- Si hay desglose de pólizas que componen el cúmulo, inclúyelas
- Calcula o extrae la relación entre la exposición máxima y el cupo aprobado"""
