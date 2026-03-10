"""
Prompt para extraer información financiera.
Alimenta: Análisis Financiero.
Fuente MVP: Documento proporcionado por el Director (en V2: servicio Emmis).
"""

SYSTEM_PROMPT_FINANCIERO = """Eres un analista financiero experto de Seguros Bolívar.
Tu tarea es extraer información financiera estructurada de los documentos proporcionados
(estados financieros, balances, estados de resultados, indicadores).

Debes devolver SIEMPRE un JSON válido con la estructura indicada.
Si un campo no se encuentra en el documento, usa null.
No inventes datos. Solo extrae lo que está explícitamente en el documento.
Los valores monetarios deben estar en pesos colombianos (COP)."""


def get_prompt_financiero() -> str:
    return """Analiza el documento financiero adjunto y extrae la siguiente información en formato JSON:

{
    "anio_actual": "Año del periodo más reciente",
    "anio_anterior": "Año del periodo anterior",
    "balance_general": {
        "total_activo_corriente": {"actual": "$0", "anterior": "$0"},
        "total_activo_no_corriente": {"actual": "$0", "anterior": "$0"},
        "total_activo": {"actual": "$0", "anterior": "$0"},
        "total_pasivo_corriente": {"actual": "$0", "anterior": "$0"},
        "total_pasivo_lp": {"actual": "$0", "anterior": "$0"},
        "total_pasivo": {"actual": "$0", "anterior": "$0"},
        "total_patrimonio": {"actual": "$0", "anterior": "$0"},
        "total_pasivo_patrimonio": {"actual": "$0", "anterior": "$0"}
    },
    "estado_resultados": {
        "ingresos_operacionales": {"actual": "$0", "anterior": "$0"},
        "costos_ventas": {"actual": "$0", "anterior": "$0"},
        "utilidad_bruta": {"actual": "$0", "anterior": "$0"},
        "gastos_operacionales": {"actual": "$0", "anterior": "$0"},
        "utilidad_operacional": {"actual": "$0", "anterior": "$0"},
        "utilidad_antes_impuestos": {"actual": "$0", "anterior": "$0"},
        "provision_impuestos": {"actual": "$0", "anterior": "$0"},
        "utilidad_neta": {"actual": "$0", "anterior": "$0"}
    },
    "indicadores_cliente": {
        "razon_corriente": {"actual": 0.00, "anterior": 0.00},
        "nivel_endeudamiento": {"actual": "0.00%", "anterior": "0.00%"},
        "margen_ebitda": {"actual": "0.00%", "anterior": "0.00%"}
    },
    "indicadores_sector": {
        "razon_corriente": null,
        "nivel_endeudamiento": null,
        "margen_ebitda": null
    },
    "calificador": {
        "z_score": null,
        "seriedad_oferta_pct": null,
        "cumplimiento_afines_pct": null,
        "cupo_propuesto": null
    },
    "interpretacion_evolucion": "Análisis de la evolución de los indicadores comparando año actual con anterior.",
    "interpretacion_sector": "Análisis de la posición financiera del cliente frente al sector.",
    "competencia": [
        {
            "nombre": "Nombre de la compañía",
            "ingreso_operativo": "$0",
            "margen_neto": "0.00%",
            "ganancia_neta": "$0",
            "anio": "20XX"
        }
    ],
    "interpretacion_competencia": "Análisis de la posición competitiva del cliente."
}

IMPORTANTE:
- Si el documento contiene ambos periodos (actual y anterior), extrae ambos
- Los indicadores se calculan: Razón Corriente = Activo Corriente / Pasivo Corriente
- Nivel de Endeudamiento = Total Pasivo / Total Activo * 100
- Si hay datos de competidores o sector, inclúyelos
- Si no hay datos de un campo, usa null"""
