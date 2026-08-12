from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    Fuentes y tamaños exactos extraídos del PDF original.
    2 hojas tamaño Carta (612 x 792 pt).
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def _pt_mm(self, pt):
        return pt * 0.3528

    def _escribir(self, x_pt, y_pt, texto, fuente='Helvetica', estilo='', tamanio_pt=8.0, alineacion='L'):
        """
        Escribe texto con fuente, estilo y tamaño exactos.
        """
        x_mm = self._pt_mm(x_pt)
        y_mm = self._pt_mm(y_pt)

        # Mapear fuentes del SAT a Helvetica (fpdf2 no tiene Arial ni Lucida Sans nativas)
        if 'Bold' in estilo:
            self.set_font(fuente, 'B', tamanio_pt * 0.3528)
        else:
            self.set_font(fuente, '', tamanio_pt * 0.3528)

        self.set_xy(x_mm, y_mm)
        self.cell(0, self._pt_mm(tamanio_pt) + 1, texto, align=alineacion)

    def _pagina_1(self):
        self.add_page()
        d = self.datos

        # === PIE DE PÁGINA (Lucida Sans 7.9pt) ===
        self._escribir(509.0, 774.2, 'Página 1 de 2', fuente='Helvetica', tamanio_pt=7.9)

        # === CÉDULA DE IDENTIFICACIÓN FISCAL (Arial Bold 10.1pt) ===
        self._escribir(68.7, 126.3, 'CÉDULA DE IDENTIFICACIÓN FISCAL', estilo='Bold', tamanio_pt=10.1)

        # === CONSTANCIA DE SITUACIÓN FISCAL (Arial Bold 12pt) ===
        self._escribir(334.4, 179.3, 'CONSTANCIA DE SITUACIÓN FISCAL', estilo='Bold', tamanio_pt=12.0, alineacion='C')

        # === RFC encabezado (Helvetica 8pt) ===
        self._escribir(189.4, 185.1, d['rfc'], tamanio_pt=8.0)

        # === Registro Federal de Contribuyentes (Arial 7.9pt) ===
        self._escribir(186.1, 196.4, 'Registro Federal de', tamanio_pt=7.9)
        self._escribir(194.5, 205.5, 'Contribuyentes', tamanio_pt=7.9)

        # === Lugar y Fecha de Emisión (Arial 10.1pt etiqueta) ===
        self._escribir(382.0, 218.0, 'Lugar y Fecha de Emisión', tamanio_pt=10.1)

        # === Nombre en 2 líneas (Helvetica 8pt) ===
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''
        self._escribir(161.6, 222.8, linea1, tamanio_pt=8.0)
        if linea2:
            self._escribir(195.4, 231.3, linea2, tamanio_pt=8.0)

        # === Lugar y fecha valor (Helvetica Bold 10.3pt) ===
        lugar_fecha = f"{d['domicilio']['estado'].upper()}, A {datetime.now().strftime('%d DE %B DE %Y').upper()}"
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            lugar_fecha = lugar_fecha.replace(en, es)
        self._escribir(308.3, 231.0, lugar_fecha, estilo='Bold', tamanio_pt=10.3)

        # === Nombre, denominación o razón social (Helvetica 7.9pt) ===
        self._escribir(165.0, 239.1, 'Nombre, denominación o razón', tamanio_pt=7.9)
        self._escribir(211.2, 247.2, 'social', tamanio_pt=8.0)

        # === IDCIF (Helvetica 8pt) ===
        self._escribir(186.8, 265.9, f'idCIF: {d["idcif"]}', tamanio_pt=8.0)

        # === VALIDA TU INFORMACIÓN FISCAL (Helvetica 8pt) ===
        self._escribir(170.9, 274.4, 'VALIDA TU INFORMACIÓN', tamanio_pt=8.0)
        self._escribir(207.5, 283.8, 'FISCAL', tamanio_pt=8.0)

        # === RFC repetido (Helvetica 8pt) ===
        self._escribir(409.9, 287.2, d['rfc'], tamanio_pt=8.0)

        # === DATOS DE IDENTIFICACIÓN (Arial Bold 10.1pt título) ===
        self._escribir(202.1, 319.8, 'Datos de Identificación del Contribuyente:', estilo='Bold', tamanio_pt=10.1)

        # Campos (etiqueta: Arial Bold 7.9pt, valor: Helvetica 8pt)
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

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in campos_id:
            self._escribir(43.2, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.9)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=8.0)

        # === DATOS DEL DOMICILIO REGISTRADO (Arial Bold 10.1pt) ===
        self._escribir(230.7, 549.5, 'Datos del domicilio registrado', estilo='Bold', tamanio_pt=10.1)

        dom = d['domicilio']

        # Columna IZQUIERDA (etiqueta: Arial Bold 7.9pt, valor: Helvetica 8pt)
        dom_izq = [
            ('Código Postal:', dom['codigo_postal'], 572.6, 99.2, 571.8),
            ('Nombre de Vialidad:', dom['calle'].upper(), 594.4, 121.3, 592.8),
            ('Número Interior:', dom.get('numero_interior', ''), 616.3, 105.2, 615.4),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 638.1, 137.8, 637.3),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 659.7, 169.5, 658.8),
        ]

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in dom_izq:
            self._escribir(43.2, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.9)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=8.0)

        # Columna DERECHA
        dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 572.6, 377.6, 571.8),
            ('Número Exterior:', dom['numero_exterior'], 594.4, 378.4, 593.0),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 616.3, 396.9, 614.6),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 633.3, 311.0, 639.5),
            ('Entre Calle:', dom.get('entre_calle', ''), 659.7, 311.0, 658.8),
        ]

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in dom_der:
            self._escribir(311.9, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.9)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=8.0)

        # Y Calle (Arial Bold 7.9pt etiqueta)
        self._escribir(42.7, 681.1, 'Y Calle:', estilo='Bold', tamanio_pt=7.9)
        self._escribir(76.4, 681.1, dom.get('y_calle', ''), tamanio_pt=8.0)

    def _pagina_2(self):
        self.add_page()
        d = self.datos

        # === PIE DE PÁGINA (Lucida Sans 7.9pt) ===
        self._escribir(509.0, 774.2, 'Página 2 de 2', fuente='Helvetica', tamanio_pt=7.9)

        # === ACTIVIDADES ECONÓMICAS (Arial Bold 10.1pt) ===
        self._escribir(241.8, 126.3, 'Actividades Económicas:', estilo='Bold', tamanio_pt=10.1)

        # Cabeceras (Arial Bold 10.1pt)
        cabeceras_act = [
            (45.1, 145.2, 'Orden'),
            (176.5, 145.2, 'Actividad Económica'),
            (377.4, 145.2, 'Porcentaje'),
            (440.8, 145.2, 'Fecha Inicio'),
            (516.2, 145.2, 'Fecha Fin'),
        ]
        for x, y, texto in cabeceras_act:
            self._escribir(x, y, texto, estilo='Bold', tamanio_pt=10.1)

        # Datos (Arial 7.9pt / Helvetica 8pt)
        self._escribir(37.7, 159.9, d.get('actividad_orden', '1'), tamanio_pt=7.9)
        self._escribir(84.8, 163.3, d.get('actividad_economica', 'Asalariado'), tamanio_pt=8.0)
        self._escribir(371.9, 159.9, d.get('actividad_porcentaje', '100'), tamanio_pt=7.9)
        self._escribir(448.7, 163.3, d.get('actividad_fecha_inicio', '18/10/2016'), tamanio_pt=8.0)
        self._escribir(516.2, 163.3, d.get('actividad_fecha_fin', ''), tamanio_pt=8.0)

        # === REGÍMENES (Arial Bold 10.1pt) ===
        self._escribir(272.5, 198.1, 'Regímenes:', estilo='Bold', tamanio_pt=10.1)

        # Cabeceras (Arial Bold 10.1pt)
        self._escribir(215.1, 217.0, 'Régimen', estilo='Bold', tamanio_pt=10.1)
        self._escribir(440.8, 217.0, 'Fecha Inicio', estilo='Bold', tamanio_pt=10.1)
        self._escribir(516.2, 217.0, 'Fecha Fin', estilo='Bold', tamanio_pt=10.1)

        # Datos (Helvetica 8pt)
        self._escribir(41.1, 234.2, d['regimen_fiscal'], tamanio_pt=8.0)
        self._escribir(448.7, 237.0, d.get('regimen_fecha_inicio', '18/10/2016'), tamanio_pt=8.0)
        self._escribir(516.2, 237.0, d.get('regimen_fecha_fin', ''), tamanio_pt=8.0)

        # === AVISOS LEGALES (Arial Bold 7.9pt) ===
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
            self._escribir(x, y, texto, estilo='Bold', tamanio_pt=7.9)

        # === CADENA ORIGINAL SELLO (Arial Bold 7.9pt etiqueta, Helvetica 8pt valor) ===
        self._escribir(47.8, 377.7, 'Cadena Original Sello:', estilo='Bold', tamanio_pt=7.9)
        cadena = d.get('cadena_digital', '')
        self._escribir(146.8, 375.9, cadena[:70], tamanio_pt=8.0)
        self._escribir(146.8, 387.2, cadena[70:140] if len(cadena) > 70 else '', tamanio_pt=8.0)
        self._escribir(146.8, 398.6, cadena[140:210] if len(cadena) > 140 else '', tamanio_pt=8.0)

        # === SELLO DIGITAL (Arial Bold 7.9pt etiqueta, Helvetica 8pt valor) ===
        self._escribir(47.8, 405.3, 'Sello Digital:', estilo='Bold', tamanio_pt=7.9)
        sello = d.get('sello_digital', '')
        self._escribir(146.8, 409.9, sello[:70], tamanio_pt=8.0)
        self._escribir(146.8, 421.3, sello[70:140] if len(sello) > 70 else '', tamanio_pt=8.0)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
