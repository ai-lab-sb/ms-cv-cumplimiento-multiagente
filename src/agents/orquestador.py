"""
Orquestador principal del SLIP.
Coordina la extracción de información de todos los documentos
y consolida los datos para generar el SLIP final.

MVP: Todas las secciones se alimentan de documentos subidos por el Director.
V2: Las secciones 3, 6, 7 y 9 se alimentarán de servicios (Emmis, SISCONC, Simon, Tronador P&G).
"""
from typing import Dict, Any, List
from datetime import datetime
from src.services.llm_service import LLMService
from src.services.spreadsheet_reader import es_spreadsheet, leer_spreadsheet
from src.prompts.prompt_extractor_contrato import (
    SYSTEM_PROMPT_CONTRATO,
    get_prompt_contrato,
)
from src.prompts.prompt_extractor_legal import (
    SYSTEM_PROMPT_LEGAL,
    get_prompt_legal,
)
from src.prompts.prompt_extractor_experiencia import (
    SYSTEM_PROMPT_EXPERIENCIA,
    get_prompt_experiencia,
)
from src.prompts.prompt_extractor_financiero import (
    SYSTEM_PROMPT_FINANCIERO,
    get_prompt_financiero,
)
from src.prompts.prompt_extractor_sisconc import (
    SYSTEM_PROMPT_SISCONC,
    get_prompt_sisconc,
)
from src.prompts.prompt_extractor_cupo import (
    SYSTEM_PROMPT_CUPO,
    get_prompt_cupo,
)
from src.prompts.prompt_extractor_vinculaciones import (
    SYSTEM_PROMPT_VINCULACIONES,
    get_prompt_vinculaciones,
)


class OrquestadorSLIP:
    """
    Orquesta el flujo completo de generación del SLIP.
    En el MVP todas las secciones se extraen de documentos subidos por el Director.
    """

    def __init__(self):
        self._llm = LLMService()
        print("[OK] OrquestadorSLIP listo")

    def ejecutar(
        self, documentos: Dict[str, Dict], datos_director: Dict[str, str]
    ) -> Dict[str, Any]:
        hoy = datetime.now()
        meses = [
            "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ]
        fecha_str = f"{hoy.day} de {meses[hoy.month]} de {hoy.year}"

        resultado = {
            "fecha_elaboracion": fecha_str,
            "archivos_adjuntos": [doc["nombre"] for doc in documentos.values() if "nombre" in doc],
            "motivo_solicitud": {},
            "resumen_negocio": {},
            "analisis_financiero": {},
            "informacion_legal": {},
            "detalles_poliza": {},
            "sisconc": {},
            "cupo_cumulo": {},
            "experiencia": {},
            "vinculaciones": {},
            "concepto_conclusion": {},
        }

        # PASO 1: Extraer datos del contrato (Secciones 1, 2, 5)
        if "contrato" in documentos:
            print("[PASO 1/8] Extrayendo datos del contrato/pliego...")
            datos_contrato = self._extraer_documento(
                documentos["contrato"],
                SYSTEM_PROMPT_CONTRATO,
                get_prompt_contrato(),
            )
            resultado["motivo_solicitud"] = datos_contrato.get("motivo_solicitud", {})
            resultado["resumen_negocio"] = datos_contrato.get("resumen_negocio", {})
            resultado["detalles_poliza"] = datos_contrato.get("detalles_poliza", {})
            print("[OK] Datos del contrato extraídos")

        # PASO 2: Extraer información legal (Sección 4)
        docs_legales = self._recopilar_docs(
            documentos, ["camara_comercio", "rut", "sarlaft", "composicion_accionaria", "renta"]
        )
        if docs_legales:
            print("[PASO 2/8] Extrayendo información legal...")
            resultado["informacion_legal"] = self._extraer_multiples(
                docs_legales, SYSTEM_PROMPT_LEGAL, get_prompt_legal()
            )
            print("[OK] Información legal extraída")

        # PASO 3: Extraer análisis financiero (Sección 3) — MVP: documento del Director
        if "estados_financieros" in documentos:
            print("[PASO 3/8] Extrayendo análisis financiero...")
            resultado["analisis_financiero"] = self._extraer_documento(
                documentos["estados_financieros"],
                SYSTEM_PROMPT_FINANCIERO,
                get_prompt_financiero(),
            )
            print("[OK] Análisis financiero extraído")

        # PASO 4: Extraer SISCONC (Sección 6) — MVP: documento del Director
        if "sisconc" in documentos:
            print("[PASO 4/8] Extrayendo información SISCONC...")
            resultado["sisconc"] = self._extraer_documento(
                documentos["sisconc"],
                SYSTEM_PROMPT_SISCONC,
                get_prompt_sisconc(),
            )
            print("[OK] SISCONC extraído")

        # PASO 5: Extraer cupo y cúmulo (Sección 7) — MVP: documento del Director
        if "cupo_cumulo" in documentos:
            print("[PASO 5/8] Extrayendo cupo y cúmulo...")
            resultado["cupo_cumulo"] = self._extraer_documento(
                documentos["cupo_cumulo"],
                SYSTEM_PROMPT_CUPO,
                get_prompt_cupo(),
            )
            print("[OK] Cupo y cúmulo extraído")

        # PASO 6: Extraer experiencia (Sección 8)
        if "experiencia" in documentos:
            print("[PASO 6/8] Extrayendo experiencia del cliente...")
            resultado["experiencia"] = self._extraer_documento(
                documentos["experiencia"],
                SYSTEM_PROMPT_EXPERIENCIA,
                get_prompt_experiencia(),
            )
            print("[OK] Experiencia extraída")

        # PASO 7: Extraer vinculaciones (Sección 9) — MVP: documento del Director
        if "vinculaciones" in documentos:
            print("[PASO 7/8] Extrayendo vinculaciones...")
            resultado["vinculaciones"] = self._extraer_documento(
                documentos["vinculaciones"],
                SYSTEM_PROMPT_VINCULACIONES,
                get_prompt_vinculaciones(),
            )
            print("[OK] Vinculaciones extraídas")

        # PASO 8: Incorporar datos del Director Comercial (Sección 10)
        print("[PASO 8/8] Incorporando concepto del Director Comercial...")
        resultado["concepto_conclusion"] = {
            "concepto_negocio": datos_director.get("concepto_negocio", ""),
            "analisis_cliente": datos_director.get("analisis_cliente", ""),
            "conclusion": datos_director.get("conclusion", ""),
            "informacion_sucursal": {
                "oficina": datos_director.get("oficina", ""),
                "localidad": datos_director.get("localidad", ""),
                "intermediario": datos_director.get("intermediario", ""),
                "director_comercial": datos_director.get("director_comercial", ""),
            },
        }

        print("[OK] SLIP generado exitosamente")
        return resultado

    def _extraer_documento(
        self, doc: Dict, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        if es_spreadsheet(doc.get("tipo", "")):
            texto = leer_spreadsheet(
                doc["contenido"], doc["tipo"], doc.get("nombre", "")
            )
            prompt_con_datos = (
                f"{user_prompt}\n\n"
                f"--- CONTENIDO DEL DOCUMENTO ---\n{texto}\n--- FIN DEL DOCUMENTO ---"
            )
            return self._llm.generar_json(
                system_prompt=system_prompt,
                user_prompt=prompt_con_datos,
            )

        return self._llm.procesar_documento(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            documento_bytes=doc["contenido"],
            mime_type=doc["tipo"],
        )

    def _recopilar_docs(
        self, documentos: Dict, campos: List[str]
    ) -> List[Dict]:
        docs = []
        for campo in campos:
            if campo in documentos:
                docs.append({
                    "contenido": documentos[campo]["contenido"],
                    "tipo": documentos[campo]["tipo"],
                })
        return docs

    def _extraer_multiples(
        self, docs: List[Dict], system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        docs_multimodal = []
        textos_extra = []

        for doc in docs:
            if es_spreadsheet(doc.get("tipo", "")):
                textos_extra.append(
                    leer_spreadsheet(doc["contenido"], doc["tipo"], doc.get("nombre", ""))
                )
            else:
                docs_multimodal.append(doc)

        prompt_final = user_prompt
        if textos_extra:
            bloque = "\n\n".join(textos_extra)
            prompt_final = (
                f"{user_prompt}\n\n"
                f"--- CONTENIDO ADICIONAL (hojas de cálculo) ---\n{bloque}\n--- FIN ---"
            )

        if not docs_multimodal:
            return self._llm.generar_json(
                system_prompt=system_prompt,
                user_prompt=prompt_final,
            )

        if len(docs_multimodal) == 1:
            return self._llm.procesar_documento(
                system_prompt=system_prompt,
                user_prompt=prompt_final,
                documento_bytes=docs_multimodal[0]["contenido"],
                mime_type=docs_multimodal[0]["tipo"],
            )

        return self._llm.procesar_multiples_documentos(
            system_prompt=system_prompt,
            user_prompt=prompt_final,
            documentos=docs_multimodal,
        )
