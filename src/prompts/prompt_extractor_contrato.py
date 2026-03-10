"""
Prompt para extraer información del Contrato / Pliego de Condiciones.
Alimenta: Motivo de la Solicitud, Resumen del Negocio, Detalles de Póliza.
"""

SYSTEM_PROMPT_CONTRATO = """Eres un analista experto en seguros de cumplimiento de Seguros Bolívar.
Tu tarea es extraer información estructurada de un contrato o pliego de condiciones
para generar un SLIP de presentación ante el comité de cupos.

Debes devolver SIEMPRE un JSON válido con la siguiente estructura exacta.
Si un campo no se encuentra en el documento, usa null.
No inventes datos. Solo extrae lo que está explícitamente en el documento."""


def get_prompt_contrato() -> str:
    return """Analiza el documento adjunto (contrato o pliego de condiciones) y extrae la siguiente información en formato JSON:

{
    "motivo_solicitud": {
        "valor_superior_8000m": true/false,
        "solicitud_facultativa": true/false,
        "aprobacion_cliente_enfoque": true/false
    },
    "resumen_negocio": {
        "nombre_proyecto": "Nombre corto o título del proyecto/licitación",
        "tomador_nombre": "Nombre completo del tomador/contratista",
        "tomador_nit": "NIT del tomador",
        "asegurado_nombre": "Nombre completo del asegurado/beneficiario/entidad contratante",
        "asegurado_nit": "NIT del asegurado",
        "valor_contrato": "Valor total del contrato en pesos colombianos",
        "plazo_ejecucion": "Plazo de ejecución del contrato",
        "objeto_contrato": "Descripción detallada del objeto del contrato"
    },
    "detalles_poliza": {
        "amparos": [
            {
                "nombre": "Nombre del amparo (ej: Seriedad de la Oferta)",
                "vigencia": "Vigencia del amparo",
                "porcentaje": "Porcentaje del valor del contrato",
                "valor_asegurado": "Valor asegurado en pesos"
            }
        ],
        "maxima_exposicion": "Suma total de todos los valores asegurados"
    }
}

IMPORTANTE:
- Los valores monetarios deben incluir el símbolo $ y separadores de miles
- Los porcentajes deben incluir el símbolo %
- Si el valor del contrato es superior a $8.000.000.000, marca valor_superior_8000m como true
- Extrae TODOS los amparos que aparezcan en el documento"""
