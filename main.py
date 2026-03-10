"""
MS-CV-CUMPLIMIENTO-MULTIAGENTE
Generador automático de SLIP para Comité de Cupos - Seguros Bolívar
"""
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

try:
    from load_secrets import load_secrets_from_json
    load_secrets_from_json()
except Exception as e:
    print(f"[WARN] No se pudieron cargar secrets: {e}")

app = Flask(__name__)

from src.agents.orquestador import OrquestadorSLIP

_orquestador = None
try:
    _orquestador = OrquestadorSLIP()
    print("[OK] OrquestadorSLIP inicializado correctamente")
except Exception as e:
    print(f"[WARN] Error inicializando OrquestadorSLIP: {e}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "ms-cv-cumplimiento-multiagente",
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/run", methods=["POST"])
def run():
    """
    Endpoint principal: recibe documentos del Director Comercial,
    extrae información con IA y genera el SLIP pre-llenado.
    
    Espera un multipart/form-data con:
    - contrato: PDF/imagen del contrato o pliego de condiciones
    - camara_comercio: PDF/imagen de la cámara de comercio
    - rut: PDF/imagen del RUT
    - sarlaft: PDF/imagen del certificado SARLAFT
    - composicion_accionaria: PDF/imagen de la composición accionaria
    - renta: PDF/imagen de la declaración de renta
    - experiencia: PDF/imagen del documento de experiencia del cliente
    - estados_financieros: PDF/imagen/Excel de estados financieros (fuente Emmis en V2)
    - sisconc: PDF/imagen de consulta SISCONC (fuente SISCONC en V2)
    - cupo_cumulo: PDF/imagen de cupo y cúmulo (fuente Emmis+Simon en V2)
    - vinculaciones: PDF/imagen de vinculaciones (fuente Tronador P&G en V2)
    - concepto_negocio (text, opcional): Concepto del Director Comercial
    - analisis_cliente (text, opcional): Análisis del Director sobre el cliente
    - conclusion (text, opcional): Conclusión y recomendación del Director
    - oficina (text, opcional): Oficina del Director
    - localidad (text, opcional): Localidad
    - intermediario (text, opcional): Intermediario
    - director_comercial (text, opcional): Nombre del Director Comercial
    """
    global _orquestador

    if _orquestador is None:
        try:
            _orquestador = OrquestadorSLIP()
        except Exception as e:
            return jsonify({"error": f"Error inicializando orquestador: {str(e)}"}), 500

    try:
        documentos = {}
        campos_documento = [
            "contrato", "camara_comercio", "rut", "sarlaft",
            "composicion_accionaria", "renta", "experiencia",
            "estados_financieros", "sisconc", "cupo_cumulo", "vinculaciones",
        ]

        for campo in campos_documento:
            if campo in request.files:
                archivo = request.files[campo]
                if archivo.filename:
                    documentos[campo] = {
                        "contenido": archivo.read(),
                        "nombre": archivo.filename,
                        "tipo": archivo.content_type,
                    }

        if not documentos:
            return jsonify({"error": "No se recibieron documentos. Se requiere al menos el contrato."}), 400

        if "contrato" not in documentos:
            return jsonify({"error": "El documento del contrato/pliego de condiciones es obligatorio."}), 400

        datos_director = {
            "concepto_negocio": request.form.get("concepto_negocio", ""),
            "analisis_cliente": request.form.get("analisis_cliente", ""),
            "conclusion": request.form.get("conclusion", ""),
            "oficina": request.form.get("oficina", ""),
            "localidad": request.form.get("localidad", ""),
            "intermediario": request.form.get("intermediario", ""),
            "director_comercial": request.form.get("director_comercial", ""),
        }

        print(f"[INFO] Procesando SLIP - Documentos recibidos: {list(documentos.keys())}")
        resultado = _orquestador.ejecutar(documentos, datos_director)

        return jsonify({
            "status": "success",
            "resultado": resultado,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/generar-slip", methods=["POST"])
def generar_slip():
    """
    Genera el HTML final del SLIP a partir de datos ya procesados.
    Recibe un JSON con todos los datos del SLIP.
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se recibieron datos"}), 400

        from src.services.slip_generator import SlipGenerator
        generator = SlipGenerator()
        html = generator.generar_html(datos)

        return jsonify({
            "status": "success",
            "html": html,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/generar-pdf", methods=["POST"])
def generar_pdf():
    """
    Genera el PDF final del SLIP a partir de datos ya procesados.
    Recibe un JSON con todos los datos del SLIP.
    Retorna el archivo PDF para descarga.
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se recibieron datos"}), 400

        from src.services.slip_generator import SlipGenerator
        generator = SlipGenerator()
        pdf_bytes = generator.generar_pdf(datos)

        from flask import Response
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=SLIP_Comite_Cupos.pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
