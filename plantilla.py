from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    Coordenadas basadas en mapeo exacto del PDF original.
    Tamaño: Carta (215.9 x 279.4 mm aprox)
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def _escribir(self, x, y, texto, negrita=False, tamanio=9, alineacion='L'):
        """Helper para escribir texto en coordenadas exactas."""
        estilo = 'B' if negrita else ''
        self.set_font('Helvetica', estilo, tamanio)
        self.set_xy(x, y)
        # Usamos cell con ancho 0 para posicionamiento absoluto
        self.cell(0, 4, texto, align=alineacion)

    def construir(self):
        self.add_page()

        d = self.datos  # atajo a los datos

        # ============================================================
        # TÍTULOS Y ENCABEZADOS (PÁGINA 1)
        # ============================================================

        # Título principal
        self._escribir(42.7, 126.3, 'CÉDULA DE IDENTIFICACIÓN FISCAL', negrita=True, tamanio=16, alineacion='C')

        # CONSTANCIA DE SITUACIÓN FISCAL (centrado aproximado)
        self.set_font('Helvetica', 'B', 14)
        self.set_xy(200, 179.3)
        self.cell(100, 6, 'CONSTANCIA DE SITUACIÓN FISCAL', align='C')

        # Página (variable)
        self._escribir(509.0, 774.2, d.get('pagina', '1 de 2'), tamanio=8, alineacion='R')

        # Registro Federal de Contribuyentes
        self._escribir(186.1, 196.4, 'Registro Federal de', tamanio=9)
        self._escribir(194.5, 205.5, 'Contribuyentes', tamanio=9)

        # RFC repetido 1 (parte del título)
        self._escribir(189.4, 185.1, d['rfc'], tamanio=7)

        # Lugar y Fecha de Emisión
        self._escribir(382.0, 218.0, 'Lugar y Fecha de Emisión', tamanio=8)
        lugar_fecha = d.get('lugar_fecha_emision', f"{d['domicilio']['estado'].upper()}, A {datetime.now().strftime('%d DE %B DE %Y').upper()}")
        self._escribir(358.1, 227.9, lugar_fecha[:40], tamanio=7)
        self._escribir(399.8, 238.7, lugar_fecha[40:80] if len(lugar_fecha) > 40 else '', tamanio=7)

        # Nombre o razón social
        self._escribir(165.0, 239.1, 'Nombre, denominación o razón', tamanio=8)
        self._escribir(211.2, 247.2, 'social', tamanio=8)
        self._escribir(171.2, 222.8, d['nombre'][:30], tamanio=8)
        self._escribir(199.0, 231.3, d['nombre'][30:60] if len(d['nombre']) > 30 else '', tamanio=8)

        # ID CIF
        self._escribir(186.8, 265.9, f"idCIF: {d['idcif']}", tamanio=8)

        # VALIDA TU INFORMACIÓN FISCAL
        self._escribir(170.9, 274.4, 'VALIDA TU INFORMACIÓN', tamanio=8)
        self._escribir(207.5, 283.8, 'FISCAL', tamanio=8)

        # RFC repetido 2
        self._escribir(409.9, 287.2, d['rfc'], tamanio=7)

        # ============================================================
        # DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE
        # ============================================================

        self._escribir(202.1, 319.8, 'Datos de Identificación del Contribuyente:', negrita=True, tamanio=9)

        # Tabla de datos (etiqueta izquierda, valor derecha)
        campos_id = [
            ('RFC:', d['rfc'], 342.9, 235.3, 341.0),
            ('CURP:', d['curp'], 364.7, 235.6, 363.7),
            ('Nombre (s):', d.get('nombres', ''), 386.6, 235.6, 386.1),
            ('Primer Apellido:', d.get('primer_apellido', ''), 408.4, 234.7, 406.5),
            ('Segundo Apellido:', d.get('segundo_apellido', ''), 430.2, 234.7, 429.2),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '18 DE OCTUBRE DE 2016'), 452.1, 238.4, 450.2),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO'), 473.9, 233.9, 472.9),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '18 DE OCTUBRE DE 2016'), 495.5, 238.4, 495.5),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre']), 517.4, 235.6, 516.8),
        ]

        for etiqueta, valor, y_label, x_valor, y_valor in campos_id:
            self._escribir(43.2, y_label, etiqueta, tamanio=8)
            self._escribir(x_valor, y_valor, str(valor), tamanio=8)

        # ============================================================
        # DATOS DEL DOMICILIO REGISTRADO
        # ============================================================

        self._escribir(230.7, 549.5, 'Datos del domicilio registrado', negrita=True, tamanio=9)

        dom = d['domicilio']
        campos_dom = [
            ('Código Postal:', dom['codigo_postal'], 572.6, 99.2, 571.8),
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 572.6, 377.6, 571.8),  # etiqueta en 311.9
            ('Nombre de Vialidad:', dom['calle'].upper(), 594.4, 121.3, 592.8),
            ('Número Exterior:', dom['numero_exterior'], 594.4, 378.4, 593.0),  # etiqueta en 311.9
            ('Número Interior:', dom.get('numero_interior', ''), 616.3, 130.0, 615.0),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 616.3, 137.8, 637.3),  # etiqueta en 311.9
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 638.1, 130.0, 637.0),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 633.3, 311.0, 639.5),  # etiqueta en 311.9
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 659.7, 169.5, 658.8),
            ('Entre Calle:', dom.get('entre_calle', ''), 659.7, 380.0, 658.0),  # etiqueta en 311.9
            ('Y Calle:', dom.get('y_calle', ''), 681.1, 80.0, 680.0),
        ]

        # Etiquetas de domicilio
        etiquetas_dom = [
            (43.2, 572.6, 'Código Postal:'),
            (311.9, 572.6, 'Tipo de Vialidad:'),
            (43.2, 594.4, 'Nombre de Vialidad:'),
            (311.9, 594.4, 'Número Exterior:'),
            (43.2, 616.3, 'Número Interior:'),
            (311.9, 616.3, 'Nombre de la Colonia:'),
            (43.2, 638.1, 'Nombre de la Localidad:'),
            (311.9, 633.3, 'Nombre del Municipio o Demarcación Territorial:'),
            (43.2, 659.7, 'Nombre de la Entidad Federativa:'),
            (311.9, 659.7, 'Entre Calle:'),
            (42.7, 681.1, 'Y Calle:'),
        ]

        for x, y, texto in etiquetas_dom:
            self._escribir(x, y, texto, tamanio=8)

        # Valores de domicilio
        valores_dom = [
            (99.2, 571.8, dom['codigo_postal']),
            (377.6, 571.8, dom.get('tipo_vialidad', 'CALLE')),
            (121.3, 592.8, dom['calle'].upper()),
            (378.4, 593.0, dom['numero_exterior']),
            (130.0, 615.0, dom.get('numero_interior', '')),
            (137.8, 637.3, dom['colonia'].upper()),
            (130.0, 637.0, dom.get('localidad', dom.get('municipio', ''))),
            (311.0, 639.5, dom.get('municipio', '')),
            (169.5, 658.8, dom['estado'].upper()),
            (380.0, 658.0, dom.get('entre_calle', '')),
            (80.0, 680.0, dom.get('y_calle', '')),
        ]

        for x, y, valor in valores_dom:
            self._escribir(x, y, str(valor), tamanio=8)

        # ============================================================
        # ACTIVIDADES ECONÓMICAS (PÁGINA 2)
        # ============================================================
        # Nota: Las coordenadas sugieren que esto está en otra página
        # Si necesitas página 2, agrega: self.add_page()
        # Por ahora lo incluimos en la misma página si cabe

        self._escribir(241.8, 126.3, 'Actividades Económicas:', negrita=True, tamanio=9)

        # Cabeceras
        cabeceras_act = [
            (45.1, 145.2, 'Orden'),
            (176.5, 145.2, 'Actividad Económica'),
            (377.4, 145.2, 'Porcentaje'),
            (440.8, 145.2, 'Fecha Inicio'),
            (516.2, 145.2, 'Fecha Fin'),
        ]
        for x, y, texto in cabeceras_act:
            self._escribir(x, y, texto, tamanio=8)

        # Valores
        self._escribir(37.7, 159.9, d.get('actividad_orden', '1'), tamanio=8)
        self._escribir(84.8, 163.3, d.get('actividad_economica', ''), tamanio=8)
        self._escribir(371.9, 159.9, d.get('actividad_porcentaje', '100'), tamanio=8)
        self._escribir(448.7, 163.3, d.get('actividad_fecha_inicio', '18/10/2016'), tamanio=8)

        # ============================================================
        # REGÍMENES
        # ============================================================

        self._escribir(272.5, 198.1, 'Regímenes:', negrita=True, tamanio=9)

        # Cabeceras
        self._escribir(215.1, 217.0, 'Régimen', tamanio=8)
        self._escribir(440.8, 217.0, 'Fecha Inicio', tamanio=8)
        # Fecha Fin no tiene label visible en el mapeo, usamos coordenada aproximada
        self._escribir(500.0, 217.0, 'Fecha Fin', tamanio=8)

        # Valores (asumimos 2 filas como en el PDF real)
        self._escribir(215.1, 228.0, 'Asalariado', tamanio=8)
        self._escribir(215.1, 236.0, d['regimen_fiscal'], tamanio=8)
        self._escribir(440.8, 228.0, d.get('regimen_fecha_inicio', '18/10/2016'), tamanio=8)
        self._escribir(500.0, 228.0, d.get('regimen_fecha_fin', ''), tamanio=8)

        # ============================================================
        # PIE DE PÁGINA - AVISOS Y CADENAS
        # ============================================================

        # Aviso de datos personales
        self._escribir(42.3, 265.1, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de', tamanio=6)
        self._escribir(42.3, 274.7, 'Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las', tamanio=6)
        self._escribir(42.3, 284.1, 'facultades conferidas a la autoridad fiscal.', tamanio=6)

        # Aviso de modificación
        self._escribir(42.3, 305.9, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección', tamanio=6)
        self._escribir(42.3, 315.5, 'http://sat.gob.mx', tamanio=6)

        # Aviso anticorrupción
        self._escribir(42.3, 337.1, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a', tamanio=6)
        self._escribir(42.3, 346.7, 'través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o', tamanio=6)
        self._escribir(42.3, 356.1, 'www.gob.mx/sfp".', tamanio=6)

        # Cadena Original
        self._escribir(47.8, 377.7, 'Cadena Original Sello:', tamanio=7)
        cadena = d.get('cadena_digital', '')
        self._escribir(146.8, 375.9, cadena[:80], tamanio=6)
        self._escribir(146.8, 387.2, cadena[80:160] if len(cadena) > 80 else '', tamanio=6)
        self._escribir(146.8, 398.6, cadena[160:240] if len(cadena) > 160 else '', tamanio=6)

        # Sello Digital
        self._escribir(47.8, 405.3, 'Sello Digital:', tamanio=7)
        sello = d.get('sello_digital', '')
        self._escribir(146.8, 409.9, sello[:80], tamanio=6)
        self._escribir(146.8, 421.3, sello[80:160] if len(sello) > 80 else '', tamanio=6)

        # ============================================================
        # CÓDIGO QR (ESQUINA INFERIOR DERECHA)
        # ============================================================
        qr_img = io.BytesIO()
        img = qrcode.make(d['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        # Posición del QR: esquina inferior derecha (típicamente X=155, Y=430 en esta escala)
        self.image(qr_img, x=420, y=430, w=30)
        self.set_font('Helvetica', '', 5)
        self.set_xy(420, 462)
        self.cell(30, 3, 'Verifica tu constancia', align='C')

        return self.output()


def generar_pdf_constancia(datos):
    """
    Recibe el diccionario de datos generados y devuelve los bytes del PDF.
    """
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
