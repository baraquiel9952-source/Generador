from fpdf import FPDF
from datetime import datetime
import io


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla EXACTA basada en JSON del PDF original NXCA del SAT.
    Incluye bordes de tabla, posiciones precisas.
    Factor: 2448px = 215.9mm → 1px = 0.0882mm
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)
        self.f = 215.9 / 2448  # factor px → mm

    def _mm(self, px):
        return px * self.f

    def _escribir(self, x_px, y_px, texto, estilo='', tamanio_pt=8, alineacion='L'):
        x_mm = self._mm(x_px)
        y_mm = self._mm(y_px)
        tamanio_mm = tamanio_pt * 0.3528

        if 'B' in estilo:
            self.set_font('Helvetica', 'B', tamanio_mm)
        else:
            self.set_font('Helvetica', '', tamanio_mm)

        self.set_xy(x_mm, y_mm)
        self.cell(0, tamanio_mm + 1, texto, align=alineacion)

    def _rect(self, x0, y0, x1, y1):
        """Dibuja un rectángulo (borde de celda)."""
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.1)
        self.rect(self._mm(x0), self._mm(y0), self._mm(x1 - x0), self._mm(y1 - y0))

    def _pagina_1(self):
        self.add_page()
        d = self.datos
        dom = d['domicilio']

        # === PIE DE PÁGINA ===
        self._escribir(2037, 3097, 'Página 1 de 2', tamanio_pt=6)

        # === CÉDULA DE IDENTIFICACIÓN FISCAL ===
        self._escribir(275, 501, 'CÉDULA DE IDENTIFICACIÓN FISCAL', estilo='B', tamanio_pt=11)

        # === CONSTANCIA DE SITUACIÓN FISCAL ===
        self._escribir(1338, 713, 'CONSTANCIA DE SITUACIÓN FISCAL', estilo='B', tamanio_pt=13)

        # === RFC ===
        self._escribir(763, 749, d['rfc'], tamanio_pt=9)

        # === Registro Federal de Contribuyentes ===
        self._escribir(745, 783, 'Registro Federal de', tamanio_pt=8)
        self._escribir(778, 819, 'Contribuyentes', tamanio_pt=8)

        # === Lugar y Fecha de Emisión ===
        self._escribir(1529, 868, 'Lugar y Fecha de Emisión', tamanio_pt=9)

        # === Nombre ===
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''
        self._escribir(693, 894, linea1, tamanio_pt=9)
        if linea2:
            self._escribir(817, 928, linea2, tamanio_pt=9)

        # === Fecha ===
        estado = dom['estado'].upper()
        fecha = datetime.now().strftime('%d DE %B DE %Y').upper()
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            fecha = fecha.replace(en, es)
        lugar_fecha = f"{estado} , {estado} A {fecha}"
        self._escribir(1331, 915, lugar_fecha, estilo='B', tamanio_pt=9)

        # === Nombre, denominación o razón social ===
        self._escribir(660, 959, 'Nombre, denominación o razón', tamanio_pt=7)
        self._escribir(845, 991, 'social', tamanio_pt=7)

        # === IDCIF ===
        self._escribir(747, 1066, f"idCIF: {d['idcif']}", tamanio_pt=9)

        # === VALIDA TU INFORMACIÓN FISCAL ===
        self._escribir(684, 1100, 'VALIDA TU INFORMACIÓN', tamanio_pt=9)
        self._escribir(830, 1138, 'FISCAL', tamanio_pt=9)

        # === RFC repetido ===
        self._escribir(1640, 1151, d['rfc'], tamanio_pt=9)

        # === DATOS DE IDENTIFICACIÓN (título) ===
        self._escribir(808, 1276, 'Datos de Identificación del Contribuyente:', estilo='B', tamanio_pt=11)

        # === BORDES DE TABLA - Datos de Identificación ===
        # Borde exterior
        self._rect(148, 1261, 2297, 2131)
        # Línea vertical central
        self._rect(921, 1261, 922, 2131)

        # === CAMPOS DE IDENTIFICACIÓN ===
        campos_id = [
            ('RFC:', d['rfc'], 1369),
            ('CURP:', d['curp'], 1456),
            ('Nombre (s):', d.get('nombres', ''), 1544),
            ('Primer Apellido:', d.get('primer_apellido', ''), 1631),
            ('Segundo Apellido:', d.get('segundo_apellido', ''), 1719),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '31 DE DICIEMBRE DE 2010'), 1806),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO'), 1894),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '31 DE DICIEMBRE DE 2010'), 1980),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre']), 2067),
        ]

        for etiqueta, valor, y_base in campos_id:
            # Etiqueta en columna izquierda
            self._escribir(172, y_base, etiqueta, estilo='B', tamanio_pt=8)
            # Valor en columna derecha
            self._escribir(942, y_base, str(valor), tamanio_pt=8)

        # === DATOS DEL DOMICILIO REGISTRADO (título) ===
        self._escribir(922, 2195, 'Datos del domicilio registrado', estilo='B', tamanio_pt=11)

        # === BORDES DE TABLA - Domicilio ===
        self._rect(148, 2181, 2297, 2784)
        self._rect(1222, 2181, 1223, 2784)

        # === CAMPOS DE DOMICILIO ===
        # Columna IZQUIERDA
        dom_izq = [
            ('Código Postal:', dom['codigo_postal'], 2288),
            ('Nombre de Vialidad:', dom.get('calle', 'SIN NOMBRE').upper(), 2376),
            ('Número Interior:', dom.get('numero_interior', ''), 2463),
            ('Nombre de la Localidad:', dom.get('localidad', ''), 2551),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 2637),
            ('Y Calle:', dom.get('y_calle', ''), 2723),
        ]

        for etiqueta, valor, y_base in dom_izq:
            self._escribir(172, y_base, etiqueta, estilo='B', tamanio_pt=8)
            self._escribir(397, y_base, str(valor), tamanio_pt=8)

        # Columna DERECHA
        dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 2288),
            ('Número Exterior:', dom.get('numero_exterior', ''), 2376),
            ('Nombre de la Colonia:', dom.get('colonia', '').upper(), 2463),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 2532),
            ('Entre Calle:', dom.get('entre_calle', ''), 2637),
        ]

        for etiqueta, valor, y_base in dom_der:
            self._escribir(1247, y_base, etiqueta, estilo='B', tamanio_pt=8)
            self._escribir(1511, y_base, str(valor), tamanio_pt=8)

    def _pagina_2(self):
        self.add_page()
        d = self.datos

        # === PIE DE PÁGINA ===
        self._escribir(2037, 3097, 'Página 2 de 2', tamanio_pt=6)

        # === ACTIVIDADES ECONÓMICAS (título) ===
        self._escribir(967, 501, 'Actividades Económicas:', estilo='B', tamanio_pt=11)

        # === BORDES TABLA ACTIVIDADES ===
        # Borde exterior
        self._rect(148, 485, 2297, 636)
        # Líneas verticales de columnas
        for x in [328, 1485, 1737, 2017]:
            self._rect(x, 485, x + 1, 636)

        # === CABECERAS ===
        cabeceras = [
            (149, 573, 'Orden'),
            (330, 573, 'Actividad Económica'),
            (1486, 573, 'Porcentaje'),
            (1738, 573, 'Fecha Inicio'),
            (2019, 573, 'Fecha Fin'),
        ]
        for x, y, texto in cabeceras:
            self._escribir(x + 10, y + 2, texto, estilo='B', tamanio_pt=9)

        # === DATOS ===
        self._escribir(150, 637, d.get('actividad_orden', '1'), tamanio_pt=8)
        self._escribir(331, 637, d.get('actividad_economica', 'Asalariado'), tamanio_pt=8)
        self._escribir(1487, 637, d.get('actividad_porcentaje', '100'), tamanio_pt=8)
        self._escribir(1784, 637, d.get('actividad_fecha_inicio', '31/12/2010'), tamanio_pt=8)

        # === REGÍMENES (título) ===
        self._escribir(1090, 789, 'Regímenes:', estilo='B', tamanio_pt=11)

        # === BORDES TABLA REGÍMENES ===
        self._rect(148, 772, 2297, 923)
        for x in [1737, 2017]:
            self._rect(x, 772, x + 1, 923)

        # === CABECERAS ===
        self._escribir(149, 860, 'Régimen', estilo='B', tamanio_pt=9)
        self._escribir(1738, 860, 'Fecha Inicio', estilo='B', tamanio_pt=9)
        self._escribir(2019, 860, 'Fecha Fin', estilo='B', tamanio_pt=9)

        # === DATOS ===
        self._escribir(150, 923, d['regimen_fiscal'], tamanio_pt=8)
        self._escribir(1784, 923, d.get('regimen_fecha_inicio', '31/12/2010'), tamanio_pt=8)

        # === AVISOS LEGALES ===
        avisos = [
            (169, 1058, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de'),
            (169, 1096, 'Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las'),
            (169, 1134, 'facultades conferidas a la autoridad fiscal.'),
            (169, 1221, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección'),
            (169, 1259, 'http://sat.gob.mx'),
            (169, 1346, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a'),
            (169, 1384, 'través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o'),
            (169, 1422, 'www.gob.mx/sfp".'),
        ]
        for x, y, texto in avisos:
            self._escribir(x, y, texto, tamanio_pt=6)

        # === CADENA ORIGINAL SELLO ===
        self._escribir(191, 1508, 'Cadena Original Sello:', estilo='B', tamanio_pt=7)
        cadena = d.get('cadena_digital', '')
        self._escribir(587, 1506, cadena[:80], tamanio_pt=6)
        self._escribir(587, 1551, cadena[80:160] if len(cadena) > 80 else '', tamanio_pt=6)

        # === SELLO DIGITAL ===
        self._escribir(191, 1619, 'Sello Digital:', estilo='B', tamanio_pt=7)
        sello = d.get('sello_digital', '')
        self._escribir(587, 1642, sello[:80], tamanio_pt=6)
        self._escribir(587, 1687, sello[80:160] if len(sello) > 80 else '', tamanio_pt=6)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
