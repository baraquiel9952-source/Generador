from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    2 hojas tamaño Carta (612 x 792 pt = 215.9 x 279.4 mm).
    Coordenadas extraídas del JSON del PDF original del SAT.
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def _pt_a_mm(self, pt):
        """Convierte puntos PDF a milímetros (1 pt = 0.3528 mm)."""
        return pt * 0.3528

    def _escribir(self, x_pt, y_pt, texto, estilo='', tamanio_pt=9, alineacion='L'):
        """Escribe texto en coordenadas exactas (en puntos PDF)."""
        x_mm = self._pt_a_mm(x_pt)
        y_mm = self._pt_a_mm(y_pt)
        tamanio_mm = tamanio_pt * 0.3528

        if 'B' in estilo:
            self.set_font('Helvetica', 'B', tamanio_mm)
        else:
            self.set_font('Helvetica', '', tamanio_mm)

        self.set_xy(x_mm, y_mm)
        self.cell(0, tamanio_mm + 1, texto, align=alineacion)

    def _pagina_1(self):
        """Página 1: Datos de identificación y domicilio."""
        self.add_page()
        d = self.datos

        # === ENCABEZADO PRINCIPAL ===

        # CÉDULA DE IDENTIFICACIÓN FISCAL (x0=68.7, y0=126.3)
        self.set_font('Helvetica', 'B', 6)
        self.set_xy(self._pt_a_mm(42.7), self._pt_a_mm(126.3))
        self.cell(self._pt_a_mm(183.3), 5, 'CÉDULA DE IDENTIFICACIÓN FISCAL', align='L')

        # CONSTANCIA DE SITUACIÓN FISCAL (x0=334.4, y0=179.3) - centrada
        self.set_font('Helvetica', 'B', 6.5)
        self.set_xy(self._pt_a_mm(42.7), self._pt_a_mm(179.3))
        self.cell(self._pt_a_mm(510.5), 5, 'CONSTANCIA DE SITUACIÓN FISCAL', align='C')

        # RFC en esquina superior derecha (x0=189.4, y0=185.1)
        self._escribir(189.4, 185.1, d['rfc'], estilo='B', tamanio_pt=7)

        # Registro Federal de Contribuyentes (x0=186.1, y0=196.4)
        self._escribir(186.1, 196.4, 'Registro Federal de', tamanio_pt=7)
        self._escribir(194.5, 205.5, 'Contribuyentes', tamanio_pt=7)

        # === NOMBRE O RAZÓN SOCIAL ===

        # Etiqueta (x0=165.0, y0=239.1)
        self._escribir(165.0, 239.1, 'Nombre, denominación o razón', tamanio_pt=7)
        self._escribir(211.2, 247.2, 'social', tamanio_pt=7)

        # Valor: nombre en 2 líneas (x0=161.6, y0=222.8 y x0=195.4, y0=231.3)
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''

        self._escribir(161.6, 222.8, linea1, estilo='B', tamanio_pt=8)
        if linea2:
            self._escribir(195.4, 231.3, linea2, estilo='B', tamanio_pt=8)

        # === IDCIF (x0=186.8, y0=265.9) ===
        self._escribir(186.8, 265.9, f'idCIF: {d["idcif"]}', tamanio_pt=7)

        # === VALIDA TU INFORMACIÓN FISCAL (x0=170.9, y0=274.4) ===
        self._escribir(170.9, 274.4, 'VALIDA TU INFORMACIÓN', tamanio_pt=7)
        self._escribir(207.5, 283.8, 'FISCAL', tamanio_pt=7)

        # === RFC repetido (x0=409.9, y0=287.2) ===
        self._escribir(409.9, 287.2, d['rfc'], tamanio_pt=7)

        # === LUGAR Y FECHA DE EMISIÓN (x0=308.3, y0=231.0) ===
        lugar_fecha = f"{d['domicilio']['estado'].upper()}, A {datetime.now().strftime('%d DE %B DE %Y').upper()}"
        # Traducir meses
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            lugar_fecha = lugar_fecha.replace(en, es)
        self._escribir(308.3, 231.0, lugar_fecha, tamanio_pt=7)

        # === Línea separadora invisible (espacio) ===

        # === DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE (x0=202.1, y0=319.8) ===
        self._escribir(202.1, 319.8, 'Datos de Identificación del Contribuyente:', estilo='B', tamanio_pt=8)

        # Campos en formato etiqueta (izquierda) + valor (derecha)
        campos_id = [
            ('RFC:', d['rfc'], 342.9, 341.0),
            ('CURP:', d['curp'], 364.7, 363.7),
            ('Nombre (s):', d.get('nombres', ''), 386.6, 386.1),
            ('Primer Apellido:', d.get('primer_apellido', ''), 408.4, 406.5),
            ('Segundo Apellido:', d.get('segundo_apellido', ''), 430.2, 429.2),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '18 DE OCTUBRE DE 2016'), 452.1, 450.2),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO'), 473.9, 472.9),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '18 DE OCTUBRE DE 2016'), 495.5, 495.5),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre']), 517.4, 516.8),
        ]

        for etiqueta, valor, y_label, y_valor in campos_id:
            self._escribir(43.2, y_label, etiqueta, estilo='B', tamanio_pt=7)
            self._escribir(235.3, y_valor, str(valor), tamanio_pt=7)

        # === DATOS DEL DOMICILIO REGISTRADO (x0=230.7, y0=549.5) ===
        self._escribir(230.7, 549.5, 'Datos del domicilio registrado', estilo='B', tamanio_pt=8)

        dom = d['domicilio']

        # Columna IZQUIERDA
        dom_izq = [
            ('Código Postal:', dom['codigo_postal'], 572.6, 571.8, 99.2),
            ('Nombre de Vialidad:', dom['calle'].upper(), 594.4, 592.8, 121.3),
            ('Número Interior:', dom.get('numero_interior', ''), 616.3, 615.4, 105.2),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 638.1, 637.3, 137.8),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 659.7, 658.8, 169.5),
        ]

        for etiqueta, valor, y_label, y_valor, x_valor in dom_izq:
            self._escribir(43.2, y_label, etiqueta, estilo='B', tamanio_pt=7)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=7)

        # Columna DERECHA
        dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 572.6, 571.8, 377.6),
            ('Número Exterior:', dom['numero_exterior'], 594.4, 593.0, 378.4),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 616.3, 614.6, 396.9),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 633.3, 639.5, 311.0),
            ('Entre Calle:', dom.get('entre_calle', ''), 659.7, 658.8, 311.0),
        ]

        for etiqueta, valor, y_label, y_valor, x_valor in dom_der:
            self._escribir(311.9, y_label, etiqueta, estilo='B', tamanio_pt=7)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=7)

        # Y Calle (x0=42.7, y0=681.1)
        self._escribir(42.7, 681.1, 'Y Calle:', estilo='B', tamanio_pt=7)
        self._escribir(76.4, 681.1, dom.get('y_calle', ''), tamanio_pt=7)

        # === PIE DE PÁGINA ===
        self._escribir(509.0, 774.2, 'Página 1 de 2', tamanio_pt=6)

    def _pagina_2(self):
        """Página 2: Actividades económicas, regímenes, avisos, cadenas y QR."""
        self.add_page()
        d = self.datos

        # === ACTIVIDADES ECONÓMICAS (x0=241.8, y0=126.3) ===
        self._escribir(241.8, 126.3, 'Actividades Económicas:', estilo='B', tamanio_pt=8)

        # Cabeceras
        cabeceras_act = [
            (45.1, 145.2, 'Orden'),
            (176.5, 145.2, 'Actividad Económica'),
            (377.4, 145.2, 'Porcentaje'),
            (440.8, 145.2, 'Fecha Inicio'),
            (516.2, 145.2, 'Fecha Fin'),
        ]
        for x, y, texto in cabeceras_act:
            self._escribir(x, y, texto, estilo='B', tamanio_pt=7)

        # Datos de actividad
        self._escribir(37.7, 159.9, d.get('actividad_orden', '1'), tamanio_pt=7)
        self._escribir(84.8, 163.3, d.get('actividad_economica', 'Asalariado'), tamanio_pt=7)
        self._escribir(371.9, 159.9, d.get('actividad_porcentaje', '100'), tamanio_pt=7)
        self._escribir(448.7, 163.3, d.get('actividad_fecha_inicio', '18/10/2016'), tamanio_pt=7)
        self._escribir(516.2, 163.3, d.get('actividad_fecha_fin', ''), tamanio_pt=7)

        # === REGÍMENES (x0=272.5, y0=198.1) ===
        self._escribir(272.5, 198.1, 'Regímenes:', estilo='B', tamanio_pt=8)

        # Cabeceras
        self._escribir(215.1, 217.0, 'Régimen', estilo='B', tamanio_pt=7)
        self._escribir(440.8, 217.0, 'Fecha Inicio', estilo='B', tamanio_pt=7)
        self._escribir(516.2, 217.0, 'Fecha Fin', estilo='B', tamanio_pt=7)

        # Datos de régimen (1 fila con nombre oficial largo)
        self._escribir(41.1, 234.2, d['regimen_fiscal'], tamanio_pt=7)
        self._escribir(448.7, 237.0, d.get('regimen_fecha_inicio', '18/10/2016'), tamanio_pt=7)
        self._escribir(516.2, 237.0, d.get('regimen_fecha_fin', ''), tamanio_pt=7)

        # === AVISOS LEGALES ===
        avisos = [
            (42.3, 265.1, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de'),
            (42.3, 274.7, 'Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las'),
            (42.3, 284.1, 'facultades conferidas a la autoridad fiscal.'),
            (42.3, 305.9, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección'),
            (42.3, 315.5, 'http://sat.gob.mx'),
            (42.3, 337.1, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a'),
            (42.3, 346.7, 'través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o'),
            (42.3, 356.1, 'www.gob.mx/sfp".'),
        ]
        for x, y, texto in avisos:
            self._escribir(x, y, texto, tamanio_pt=6)

        # === CADENA ORIGINAL SELLO (x0=47.8, y0=377.7) ===
        self._escribir(47.8, 377.7, 'Cadena Original Sello:', estilo='B', tamanio_pt=7)
        cadena = d.get('cadena_digital', '')
        self._escribir(146.8, 375.9, cadena[:70], tamanio_pt=6)
        self._escribir(146.8, 387.2, cadena[70:140] if len(cadena) > 70 else '', tamanio_pt=6)
        self._escribir(146.8, 398.6, cadena[140:210] if len(cadena) > 140 else '', tamanio_pt=6)

        # === SELLO DIGITAL (x0=47.8, y0=405.3) ===
        self._escribir(47.8, 405.3, 'Sello Digital:', estilo='B', tamanio_pt=7)
        sello = d.get('sello_digital', '')
        self._escribir(146.8, 409.9, sello[:70], tamanio_pt=6)
        self._escribir(146.8, 421.3, sello[70:140] if len(sello) > 70 else '', tamanio_pt=6)

        # === PIE DE PÁGINA ===
        self._escribir(509.0, 774.2, 'Página 2 de 2', tamanio_pt=6)

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
