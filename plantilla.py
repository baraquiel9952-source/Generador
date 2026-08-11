from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    2 hojas tamaño Carta (216 x 279 mm).
    Coordenadas basadas en mapeo exacto del PDF original.
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
        self.cell(0, 4, texto, align=alineacion)

    def _pagina_1(self):
        """Construye la página 1: datos principales del contribuyente."""
        self.add_page()
        d = self.datos

        # === TÍTULOS Y ENCABEZADOS ===

        # CÉDULA DE IDENTIFICACIÓN FISCAL (centrado)
        self.set_font('Helvetica', 'B', 16)
        self.set_xy(42.7, 20)
        self.cell(130, 6, 'CÉDULA DE IDENTIFICACIÓN FISCAL', align='C')

        # CONSTANCIA DE SITUACIÓN FISCAL
        self.set_font('Helvetica', 'B', 14)
        self.set_xy(42.7, 28)
        self.cell(130, 6, 'CONSTANCIA DE SITUACIÓN FISCAL', align='C')

        # RFC en el encabezado
        self._escribir(42.7, 36, d['rfc'], tamanio=8, alineacion='C')

        # Registro Federal de Contribuyentes
        self._escribir(42.7, 44, 'Registro Federal de', tamanio=9, alineacion='C')
        self._escribir(42.7, 50, 'Contribuyentes', tamanio=9, alineacion='C')

        # Nombre o razón social (etiqueta + valor)
        self._escribir(42.7, 60, 'Nombre, denominación o razón social', tamanio=8)
        self._escribir(42.7, 68, d['nombre'], tamanio=10, negrita=True)

        # ID CIF
        self._escribir(42.7, 78, f"idCIF: {d['idcif']}", tamanio=9)

        # VALIDA TU INFORMACIÓN FISCAL
        self._escribir(42.7, 86, 'VALIDA TU INFORMACIÓN FISCAL', tamanio=9)

        # Lugar y Fecha de Emisión
        lugar_fecha = f"{d['domicilio']['estado'].upper()}, A {datetime.now().strftime('%d DE %B DE %Y').upper()}"
        self._escribir(130, 60, 'Lugar y Fecha de Emisión', tamanio=8)
        self._escribir(130, 68, lugar_fecha, tamanio=8)

        # RFC repetido esquina superior derecha
        self._escribir(130, 36, d['rfc'], tamanio=8, alineacion='R')

        # === DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE ===

        self._escribir(42.7, 100, 'Datos de Identificación del Contribuyente:', negrita=True, tamanio=10)

        campos_id = [
            ('RFC:', d['rfc']),
            ('CURP:', d['curp']),
            ('Nombre (s):', d.get('nombres', '')),
            ('Primer Apellido:', d.get('primer_apellido', '')),
            ('Segundo Apellido:', d.get('segundo_apellido', '')),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '18 DE OCTUBRE DE 2016')),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO')),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '18 DE OCTUBRE DE 2016')),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre'])),
        ]

        y_inicio = 110
        for i, (etiqueta, valor) in enumerate(campos_id):
            y = y_inicio + (i * 8)
            self._escribir(42.7, y, etiqueta, tamanio=8)
            self._escribir(90, y, str(valor), tamanio=8)

        # === DATOS DEL DOMICILIO REGISTRADO ===

        y_dom = y_inicio + len(campos_id) * 8 + 10
        self._escribir(42.7, y_dom, 'Datos del domicilio registrado:', negrita=True, tamanio=10)

        dom = d['domicilio']
        # Columna izquierda
        campos_dom_izq = [
            ('Código Postal:', dom['codigo_postal']),
            ('Nombre de Vialidad:', dom['calle'].upper()),
            ('Número Interior:', dom.get('numero_interior', '')),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', ''))),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper()),
            ('Y Calle:', dom.get('y_calle', '')),
        ]

        # Columna derecha
        campos_dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE')),
            ('Número Exterior:', dom['numero_exterior']),
            ('Nombre de la Colonia:', dom['colonia'].upper()),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', '')),
            ('Entre Calle:', dom.get('entre_calle', '')),
        ]

        y_dom_inicio = y_dom + 8
        for i, (etiqueta, valor) in enumerate(campos_dom_izq):
            y = y_dom_inicio + (i * 8)
            self._escribir(42.7, y, etiqueta, tamanio=8)
            self._escribir(85, y, str(valor), tamanio=8)

        for i, (etiqueta, valor) in enumerate(campos_dom_der):
            y = y_dom_inicio + (i * 8)
            self._escribir(120, y, etiqueta, tamanio=8)
            self._escribir(175, y, str(valor), tamanio=8)

        # === PIE DE PÁGINA 1 ===
        self._escribir(42.7, 250, 'Página 1 de 2', tamanio=7, alineacion='C')

    def _pagina_2(self):
        """Construye la página 2: actividades, regímenes, avisos, cadenas y QR."""
        self.add_page()
        d = self.datos

        # === ACTIVIDADES ECONÓMICAS ===

        self._escribir(42.7, 20, 'Actividades Económicas:', negrita=True, tamanio=10)

        # Cabeceras de tabla
        col_act = [15, 80, 25, 30, 30]
        cabeceras_act = ['Orden', 'Actividad Económica', 'Porcentaje', 'Fecha Inicio', 'Fecha Fin']
        x_act = [42.7, 57.7, 137.7, 162.7, 192.7]

        self.set_font('Helvetica', 'B', 8)
        for cab, x, w in zip(cabeceras_act, x_act, col_act):
            self.set_xy(x, 30)
            self.cell(w, 5, cab, border=1)

        # Datos de actividad
        self.set_font('Helvetica', '', 8)
        self.set_xy(x_act[0], 36)
        self.cell(col_act[0], 5, d.get('actividad_orden', '1'), border=1)
        self.set_xy(x_act[1], 36)
        self.cell(col_act[1], 5, d.get('actividad_economica', ''), border=1)
        self.set_xy(x_act[2], 36)
        self.cell(col_act[2], 5, d.get('actividad_porcentaje', '100'), border=1)
        self.set_xy(x_act[3], 36)
        self.cell(col_act[3], 5, d.get('actividad_fecha_inicio', '18/10/2016'), border=1)
        self.set_xy(x_act[4], 36)
        self.cell(col_act[4], 5, d.get('actividad_fecha_fin', ''), border=1)

        # === REGÍMENES ===

        self._escribir(42.7, 55, 'Regímenes:', negrita=True, tamanio=10)

        # Cabeceras
        col_reg = [100, 35, 35]
        cabeceras_reg = ['Régimen', 'Fecha Inicio', 'Fecha Fin']
        x_reg = [42.7, 142.7, 177.7]

        self.set_font('Helvetica', 'B', 8)
        for cab, x, w in zip(cabeceras_reg, x_reg, col_reg):
            self.set_xy(x, 65)
            self.cell(w, 5, cab, border=1)

        # Datos de régimen (2 filas)
        self.set_font('Helvetica', '', 8)
        # Fila 1: nombre corto
        self.set_xy(x_reg[0], 71)
        self.cell(col_reg[0], 5, 'Asalariado', border=1)
        self.set_xy(x_reg[1], 71)
        self.cell(col_reg[1], 5, d.get('regimen_fecha_inicio', '18/10/2016'), border=1)
        self.set_xy(x_reg[2], 71)
        self.cell(col_reg[2], 5, d.get('regimen_fecha_fin', ''), border=1)
        # Fila 2: nombre largo
        self.set_xy(x_reg[0], 77)
        self.cell(col_reg[0], 5, d['regimen_fiscal'], border=1)
        self.set_xy(x_reg[1], 77)
        self.cell(col_reg[1], 5, '', border=1)
        self.set_xy(x_reg[2], 77)
        self.cell(col_reg[2], 5, '', border=1)

        # === AVISOS LEGALES ===

        self.set_font('Helvetica', '', 6.5)
        avisos = [
            (42.7, 100, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las facultades conferidas a la autoridad fiscal.'),
            (42.7, 112, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección http://sat.gob.mx'),
            (42.7, 124, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o www.gob.mx/sfp".'),
        ]

        for x, y, texto in avisos:
            self.set_xy(x, y)
            self.multi_cell(130, 4, texto, align='J')

        # === CADENA ORIGINAL Y SELLO DIGITAL ===

        self._escribir(42.7, 145, 'Cadena Original Sello:', tamanio=7, negrita=True)
        cadena = d.get('cadena_digital', '')
        lineas_cadena = [cadena[i:i+90] for i in range(0, min(len(cadena), 270), 90)]
        for i, linea in enumerate(lineas_cadena):
            self._escribir(42.7, 152 + (i * 5), linea, tamanio=6)

        self._escribir(42.7, 172, 'Sello Digital:', tamanio=7, negrita=True)
        sello = d.get('sello_digital', '')
        lineas_sello = [sello[i:i+90] for i in range(0, min(len(sello), 180), 90)]
        for i, linea in enumerate(lineas_sello):
            self._escribir(42.7, 179 + (i * 5), linea, tamanio=6)

        # === CÓDIGO QR ===

        qr_img = io.BytesIO()
        img = qrcode.make(d['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        # QR en esquina inferior derecha
        self.image(qr_img, x=150, y=210, w=35)
        self.set_font('Helvetica', '', 5)
        self.set_xy(150, 247)
        self.cell(35, 3, 'Verifica tu constancia', align='C')

        # === PIE DE PÁGINA 2 ===
        self._escribir(42.7, 260, 'Página 2 de 2', tamanio=7, alineacion='C')

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
