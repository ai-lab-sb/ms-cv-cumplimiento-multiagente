"""
Generador del HTML y PDF del SLIP a partir de datos estructurados.
Usa Jinja2 para renderizar la plantilla y WeasyPrint para generar el PDF.
"""
import os
import io
from jinja2 import Environment, FileSystemLoader, Undefined


class SilentUndefined(Undefined):
    """Permite acceso encadenado a atributos sin errores cuando faltan claves."""

    def __getattr__(self, name):
        return self

    def __getitem__(self, name):
        return self

    def __str__(self):
        return ""

    def __bool__(self):
        return False

    def __iter__(self):
        return iter([])


class SlipGenerator:
    """Genera el HTML y PDF del SLIP con los datos proporcionados."""

    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self._env = Environment(
            loader=FileSystemLoader(template_dir),
            undefined=SilentUndefined,
        )

    def generar_html(self, datos: dict) -> str:
        datos = self._enriquecer_con_graficos(datos)
        template = self._env.get_template("slip_template.html")
        return template.render(**datos)

    def _enriquecer_con_graficos(self, datos: dict) -> dict:
        """Genera gráficos financieros y los inyecta como base64 en los datos."""
        analisis = datos.get("analisis_financiero")
        if analisis and isinstance(analisis, dict) and analisis.get("indicadores_cliente"):
            try:
                from src.services.chart_generator import generar_graficos_financieros
                graficos = generar_graficos_financieros(analisis)
                datos["grafico_anual_b64"] = graficos.get("grafico_anual")
                datos["grafico_sector_b64"] = graficos.get("grafico_sector")
            except Exception as e:
                print(f"[WARN] No se pudieron generar gráficos: {e}")
                datos["grafico_anual_b64"] = None
                datos["grafico_sector_b64"] = None
        return datos

    def generar_pdf(self, datos: dict) -> bytes:
        """
        Genera el PDF del SLIP renderizando primero el HTML y luego
        convirtiéndolo a PDF con WeasyPrint.

        Returns:
            bytes del archivo PDF generado.
        """
        from weasyprint import HTML

        html_string = self.generar_html(datos)
        pdf_buffer = io.BytesIO()
        HTML(string=html_string).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer.read()
