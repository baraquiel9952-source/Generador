from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    2 hojas tamaño Carta (216 x 279 mm).
    Corregida según comparativa con PDF original del SAT.
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)
        # Metadato producer como el SAT real
        self._producer = 'FPDF 1.86'

    @property
    def producer(self):
        return self._producer

    def _escribir(self, x, y, texto, negrita=False, tamanio=9, alineacion='L'):
        """Helper para escribir texto en coordenadas exactas."""
        estilo = 'B' if negrita else ''
        self.set_font('Helvetica', estilo, tamanio)
        self.set_xy(x, y)
        self.cell(0, 4, texto, align=alineacion)

    def _mes_espanol(self, fecha_str):
        """Traduce meses del inglés al español."""
        meses = {
            'JANUARY': 'ENERO', 'FEBRUARY': 'FEBRERO', 'MARCH': 'MARZO',
            'APRIL': 'ABRIL', 'MAY': 'MAYO', 'JUNE': 'JUNIO',
            'JULY': 'JULIO', 'AUGUST': 'AGOSTO', 'SEPTEMBER': 'SEPTIEMBRE',
            'OCTOBER': 'OCTUBRE', 'NOVEMBER': 'NOVIEMBRE', 'DECEMBER': 'DICIEMBRE'
        }
        for en, es in meses.items():
            fecha_str = fecha_str.replace(en, es)
        return fecha_str

    def _pagina_1(self):
        """Construye la página 1: datos principales del contribuyente."""
        self.add_page()
        d = self.datos

        # === TÍTULOS Y ENCABEZADOS (centrados) ===

        self.set_font('Helvetica', 'B', 16)
        self.set_xy(31.2, 20)
        self.cell(150, 6, 'CÉDULA DE IDENTIFICACIÓN FISCAL', align='C')

        self.set_font('Helvetica', 'B', 14)
        self.set_xy(31.2, 28)
        self.cell(150, 6, 'CONSTANCIA DE SITUACIÓN FISCAL', align='C')

        # RFC en el encabezado
        self._escribir(31.2, 36, d['rfc'], tamanio=8, alineacion='C')

        # Registro Federal de Contribuyentes
        self._escribir(31.2, 44, 'Registro Federal de', tamanio=9, alineacion='C')
        self._escribir(31.2, 50, 'Contribuyentes', tamanio=9, alineacion='C')

        # Nombre o razón social
        self._escribir(31.2, 60, 'Nombre, denominación o razón social', tamanio=8)
        self._escribir(31.2, 68, d['nombre'], tamanio=10, negrita=True)

        # ID CIF
        self._escribir(31.2, 78, f"idCIF: {d['idcif']}", tamanio=9)

        # VALIDA TU INFORMACIÓN FISCAL
        self._escribir(31.2, 86, 'VALIDA TU INFORMACIÓN FISCAL', tamanio=9)

        # Lugar y Fecha de Emisión (¡corregido: mes en español!)
        lugar_fecha = f"{d['domicilio']['estado'].upper()}, A {self._mes_espanol(datetime.now().strftime('%d DE %B DE %Y').upper())}"
        self._escribir(258.0, 192.2, lugar_fecha, tamanio=8)

        # === DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE ===

        self._escribir(31.2, 290, 'Datos de Identificación del Contribuyente:', negrita=True, tamanio=10)

        campos_id = [
            ('RFC:', d['rfc'], 311.3),
            ('CURP:', d['curp'], 334.0),
            ('Nombre (s):', d.get('nombres', ''), 356.6),
            ('Primer Apellido:', d.get('primer_apellido', ''), 379.3),
            ('Segundo Apellido:', d.get('segundo_apellido', ''), 402.0),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '18 DE OCTUBRE DE 2016'), 424.7),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO'), 447.3),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '18 DE OCTUBRE DE 2016'), 470.0),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre']), 492.7),
        ]

        for etiqueta, valor, y_valor in campos_id:
            self._escribir(31.2, y_valor - 1, etiqueta, tamanio=8)
            self._escribir(144.6, y_valor, str(valor), tamanio=8)

        # === DATOS DEL DOMICILIO REGISTRADO (sin ":" extra) ===

        self._escribir(31.2, 540, 'Datos del domicilio registrado', negrita=True, tamanio=10)

        dom = d['domicilio']
        # Columna izquierda
        campos_dom_izq = [
            ('Código Postal:', dom['codigo_postal'], 566.4),
            ('Nombre de Vialidad:', dom['calle'].upper(), 589.1),
            ('Número Interior:', dom.get('numero_interior', ''), 611.8),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 634.4),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 657.1),
            ('Y Calle:', dom.get('y_calle', ''), 679.0),
        ]

        # Columna derecha
        campos_dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 566.4),
            ('Número Exterior:', dom['numero_exterior'], 589.1),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 611.8),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 634.4),
            ('Entre Calle:', dom.get('entre_calle', ''), 657.1),
        ]

        for etiqueta, valor, y in campos_dom_izq:
            self._escribir(31.2, y, etiqueta, tamanio=8)
            self._escribir(85.0, y, str(valor), tamanio=8)

        for etiqueta, valor, y in campos_dom_der:
            self._escribir(229.6, y, etiqueta, tamanio=8)
            self._escribir(283.0, y, str(valor), tamanio=8)

        # === QR EN PÁGINA 1 (agregado) ===
        qr_img = io.BytesIO()
        img = qrcode.make(d['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        self.image(qr_img, x=430, y=30, w=35)
        self.set_font('Helvetica', '', 5)
        self.set_xy(430, 67)
        self.cell(35, 3, 'Verifica tu constancia', align='C')

        # === PIE DE PÁGINA 1 ===
        self._escribir(31.2, 250, 'Página 1 de 2', tamanio=7, alineacion='C')

    def _pagina_2(self):
        """Construye la página 2: actividades, regímenes, avisos, cadenas y QR."""
        self.add_page()
        d = self.datos

        # === ACTIVIDADES ECONÓMICAS ===

        self._escribir(31.2, 20, 'Actividades Económicas:', negrita=True, tamanio=10)

        # Cabeceras con bordes (como el original)
        col_act = [15, 80, 25, 30, 30]
        cabeceras_act = ['Orden', 'Actividad Económica', 'Porcentaje', 'Fecha Inicio', 'Fecha Fin']
        x_act = [31.2, 46.2, 126.2, 151.2, 181.2]

        self.set_font('Helvetica', 'B', 8)
        for cab, x, w in zip(cabeceras_act, x_act, col_act):
            self.set_xy(x, 30)
            self.cell(w, 5, cab, border=1)

        # Datos de actividad (con valor por defecto)
        self.set_font('Helvetica', '', 8)
        self.set_xy(x_act[0], 36)
        self.cell(col_act[0], 5, d.get('actividad_orden', '1'), border=1)
        self.set_xy(x_act[1], 36)
        self.cell(col_act[1], 5, d.get('actividad_economica', 'Asalariado'), border=1)  # ¡corregido!
        self.set_xy(x_act[2], 36)
        self.cell(col_act[2], 5, d.get('actividad_porcentaje', '100'), border=1)
        self.set_xy(x_act[3], 36)
        self.cell(col_act[3], 5, d.get('actividad_fecha_inicio', '18/10/2016'), border=1)
        self.set_xy(x_act[4], 36)
        self.cell(col_act[4], 5, d.get('actividad_fecha_fin', ''), border=1)

        # === REGÍMENES (nombre oficial largo, 1 sola fila) ===

        self._escribir(31.2, 55, 'Regímenes:', negrita=True, tamanio=10)

        col_reg = [130, 35, 35]
        cabeceras_reg = ['Régimen', 'Fecha Inicio', 'Fecha Fin']
        x_reg = [31.2, 161.2, 196.2]

        self.set_font('Helvetica', 'B', 8)
        for cab, x, w in zip(cabeceras_reg, x_reg, col_reg):
            self.set_xy(x, 65)
            self.cell(w, 5, cab, border=1)

        # 1 sola fila con nombre oficial largo
        self.set_font('Helvetica', '', 8)
        self.set_xy(x_reg[0], 71)
        self.cell(col_reg[0], 5, d['regimen_fiscal'], border=1)
        self.set_xy(x_reg[1], 71)
        self.cell(col_reg[1], 5, d.get('regimen_fecha_inicio', '18/10/2016'), border=1)
        self.set_xy(x_reg[2], 71)
        self.cell(col_reg[2], 5, d.get('regimen_fecha_fin', ''), border=1)

        # === AVISOS LEGALES ===

        self.set_font('Helvetica', '', 6.5)
        avisos = [
            (31.2, 100, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las facultades conferidas a la autoridad fiscal.'),
            (31.2, 112, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección http://sat.gob.mx'),
            (31.2, 124, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o www.gob.mx/sfp".'),
        ]

        for x, y, texto in avisos:
            self.set_xy(x, y)
            self.multi_cell(150, 4, texto, align='J')

        # === CADENA ORIGINAL Y SELLO DIGITAL ===

        self._escribir(31.2, 145, 'Cadena Original Sello:', tamanio=7, negrita=True)
        cadena = d.get('cadena_digital', '')
        lineas_cadena = [cadena[i:i+90] for i in range(0, min(len(cadena), 270), 90)]
        for i, linea in enumerate(lineas_cadena):
            self._escribir(31.2, 152 + (i * 5), linea, tamanio=6)

        self._escribir(31.2, 172, 'Sello Digital:', tamanio=7, negrita=True)
        sello = d.get('sello_digital', '')
        lineas_sello = [sello[i:i+90] for i in range(0, min(len(sello), 180), 90)]
        for i, linea in enumerate(lineas_sello):
            self._escribir(31.2, 179 + (i * 5), linea, tamanio=6)

        # === QR EN PÁGINA 2 ===
        qr_img = io.BytesIO()
        img = qrcode.make(d['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        self.image(qr_img, x=150, y=210, w=35)
        self.set_font('Helvetica', '', 5)
        self.set_xy(150, 247)
        self.cell(35, 3, 'Verifica tu constancia', align='C')

        # === PIE DE PÁGINA 2 ===
        self._escribir(31.2, 260, 'Página 2 de 2', tamanio=7, alineacion='C')

    def construir(self):
        """Construye el PDF completo (2 páginas)."""
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    """
    Recibe el diccionario de datos generados y devuelve los bytes del PDF.
    """
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
