"""
Servicio LLM usando Google GenAI (Gemini).
Soporta procesamiento de documentos (PDFs e imágenes) con capacidades multimodales.
"""
import os
import json
import base64
from typing import Optional, Dict, Any, List

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


class LLMService:
    """Servicio para interactuar con modelos Gemini via Google GenAI."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.3,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ):
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai no está instalado. Ejecuta: pip install google-genai")

        self._model_name = model_name
        self._temperature = temperature

        resolved_project = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        resolved_location = location or os.environ.get("GOOGLE_CLOUD_LOCATION")
        resolved_api_key = os.environ.get("GOOGLE_API_KEY")

        if resolved_project:
            if not resolved_location:
                raise EnvironmentError("GOOGLE_CLOUD_LOCATION no está configurado")
            try:
                self._client = genai.Client(
                    vertexai=True,
                    project=resolved_project,
                    location=resolved_location,
                )
                print(f"[OK] GenAI configurado con Vertex AI (proyecto: {resolved_project})")
            except Exception as e:
                if resolved_api_key:
                    self._client = genai.Client(api_key=resolved_api_key)
                    print("[OK] GenAI configurado con API key (fallback)")
                else:
                    raise EnvironmentError(f"Error configurando GenAI: {e}")
        elif resolved_api_key:
            self._client = genai.Client(api_key=resolved_api_key)
            print("[OK] GenAI configurado con API key")
        else:
            raise EnvironmentError(
                "No se encontró autenticación para google.genai. "
                "Configura GOOGLE_CLOUD_PROJECT o GOOGLE_API_KEY."
            )

        print(f"   Modelo: {self._model_name}")

    def generar_respuesta(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: int = 8192,
    ) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            config = types.GenerateContentConfig(
                temperature=temperature or self._temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
            )
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            print(f"[ERROR] Error generando respuesta LLM: {e}")
            raise

    def procesar_documento(
        self,
        system_prompt: str,
        user_prompt: str,
        documento_bytes: bytes,
        mime_type: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Procesa un documento (PDF/imagen) con el modelo multimodal
        y devuelve un JSON estructurado.
        """
        try:
            doc_part = types.Part.from_bytes(data=documento_bytes, mime_type=mime_type)
            text_part = types.Part.from_text(text=f"{system_prompt}\n\n{user_prompt}")

            config = types.GenerateContentConfig(
                temperature=temperature or 0.1,
                max_output_tokens=65536,
                top_p=0.95,
            )

            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[doc_part, text_part],
                config=config,
            )

            return self._limpiar_y_parsear_json(response.text)

        except Exception as e:
            print(f"[ERROR] Error procesando documento: {e}")
            raise

    def procesar_multiples_documentos(
        self,
        system_prompt: str,
        user_prompt: str,
        documentos: List[Dict[str, Any]],
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Procesa múltiples documentos en una sola llamada al modelo.
        Cada documento en la lista debe tener 'contenido' (bytes) y 'tipo' (mime_type).
        """
        try:
            parts = []
            for doc in documentos:
                parts.append(
                    types.Part.from_bytes(data=doc["contenido"], mime_type=doc["tipo"])
                )
            parts.append(types.Part.from_text(text=f"{system_prompt}\n\n{user_prompt}"))

            config = types.GenerateContentConfig(
                temperature=temperature or 0.1,
                max_output_tokens=65536,
                top_p=0.95,
            )

            response = self._client.models.generate_content(
                model=self._model_name,
                contents=parts,
                config=config,
            )

            return self._limpiar_y_parsear_json(response.text)

        except Exception as e:
            print(f"[ERROR] Error procesando múltiples documentos: {e}")
            raise

    def generar_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        try:
            respuesta_raw = self.generar_respuesta(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature or 0.2,
                max_tokens=65536,
            )
            return self._limpiar_y_parsear_json(respuesta_raw)
        except Exception as e:
            print(f"[ERROR] Error en generar_json: {e}")
            raise

    def _limpiar_y_parsear_json(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}

        cleaned = text.strip()

        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        first_brace = cleaned.find("{")
        if first_brace == -1:
            print(f"[WARN] No se encontró JSON: {text[:200]}...")
            return {}

        depth = 0
        end_pos = -1
        for j in range(first_brace, len(cleaned)):
            c = cleaned[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end_pos = j
                    break

        if end_pos > first_brace:
            candidate = cleaned[first_brace : end_pos + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        print(f"[WARN] No se pudo parsear JSON: {text[:200]}...")
        return {}
