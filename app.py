import io
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from main import generar_datos_completos
from plantilla import generar_pdf_constancia

app = Flask(__name__)
CORS(app)

# ============================================================
# RUTA PRINCIPAL - INFORMACIÓN
# ============================================================

@app.route('/')
def index():
    return jsonify({
        'servicio': 'API Generador de Constancia Fiscal Sintética',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generar': 'Genera datos sintéticos (JSON)',
            'POST /api/generar/pdf': 'Genera PDF de constancia (descarga)',
            'POST /api/generar/completo': 'Genera datos + PDF (JSON con base64)',
            'GET /api/estados': 'Lista de estados disponibles'
        },
        'documentacion': {
            'ejemplo': {
                'method': 'POST',
                'url': '/api/generar',
                'body': {
                    'nombre': 'Hernandez Garcia Maria Luisa',
                    'fecha_nacimiento': '1990-03-22',
                    'estado': 'JALISCO',
                    'sexo': 'M'
                }
            }
        }
    })

# ============================================================
# ENDPOINT 1: GENERAR SOLO DATOS (JSON)
# ============================================================

@app.route('/api/generar', methods=['POST'])
def api_generar():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Cuerpo JSON requerido'}), 400

        nombre = data.get('nombre', '').strip()
        fecha = data.get('fecha_nacimiento', '').strip()
        estado = data.get('estado', '').strip().upper()
        sexo = data.get('sexo', 'H').strip().upper()

        errores = []
        if not nombre or len(nombre.split()) < 3:
            errores.append('Nombre completo requerido (Apellido1 Apellido2 Nombre)')
        if not fecha:
            errores.append('Fecha de nacimiento requerida (YYYY-MM-DD)')
        if not estado:
            errores.append('Estado requerido')
        if sexo not in ['H', 'M']:
            errores.append('Sexo debe ser H o M')

        if errores:
            return jsonify({'error': 'Datos inválidos', 'detalles': errores}), 400

        datos = generar_datos_completos(nombre, fecha, estado, sexo)

        return jsonify({
            'exito': True,
            'datos': datos
        })

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

# ============================================================
# ENDPOINT 2: GENERAR PDF (DESCARGA DIRECTA)
# ============================================================

@app.route('/api/generar/pdf', methods=['POST'])
def api_generar_pdf():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Cuerpo JSON requerido'}), 400

        nombre = data.get('nombre', '').strip()
        fecha = data.get('fecha_nacimiento', '').strip()
        estado = data.get('estado', '').strip().upper()
        sexo = data.get('sexo', 'H').strip().upper()

        errores = []
        if not nombre or len(nombre.split()) < 3:
            errores.append('Nombre completo requerido')
        if not fecha:
            errores.append('Fecha requerida')
        if not estado:
            errores.append('Estado requerido')
        if sexo not in ['H', 'M']:
            errores.append('Sexo debe ser H o M')

        if errores:
            return jsonify({'error': 'Datos inválidos', 'detalles': errores}), 400

        datos = generar_datos_completos(nombre, fecha, estado, sexo)
        pdf_bytes = generar_pdf_constancia(datos)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'constancia_{datos["rfc"]}.pdf'
        )

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

# ============================================================
# ENDPOINT 3: GENERAR DATOS + PDF (JSON CON BASE64)
# ============================================================

@app.route('/api/generar/completo', methods=['POST'])
def api_generar_completo():
    try:
        import base64
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Cuerpo JSON requerido'}), 400

        nombre = data.get('nombre', '').strip()
        fecha = data.get('fecha_nacimiento', '').strip()
        estado = data.get('estado', '').strip().upper()
        sexo = data.get('sexo', 'H').strip().upper()

        errores = []
        if not nombre or len(nombre.split()) < 3:
            errores.append('Nombre completo requerido')
        if not fecha:
            errores.append('Fecha requerida')
        if not estado:
            errores.append('Estado requerido')
        if sexo not in ['H', 'M']:
            errores.append('Sexo debe ser H o M')

        if errores:
            return jsonify({'error': 'Datos inválidos', 'detalles': errores}), 400

        datos = generar_datos_completos(nombre, fecha, estado, sexo)
        pdf_bytes = generar_pdf_constancia(datos)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return jsonify({
            'exito': True,
            'datos': datos,
            'pdf_base64': pdf_base64,
            'pdf_nombre': f'constancia_{datos["rfc"]}.pdf'
        })

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

# ============================================================
# ENDPOINT 4: LISTA DE ESTADOS
# ============================================================

@app.route('/api/estados', methods=['GET'])
def api_estados():
    from main import ENTIDADES
    estados = sorted(set(
        e for e in ENTIDADES.keys()
        if e not in ['CDMX', 'ESTADO DE MEXICO', 'MEXICO', 'NACIDO EN EL EXTRANJERO']
    ))
    return jsonify({
        'estados': estados,
        'total': len(estados)
    })

# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Método no permitido'}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Error interno del servidor'}), 500

# ============================================================
# INICIO
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
