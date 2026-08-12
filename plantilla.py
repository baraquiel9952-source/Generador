from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    Tamaños corregidos: multiplicados por 2.5 para legibilidad.
    2 hojas tamaño Carta (612 x 792 pt).
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def _pt_mm(self, pt):
        return pt * 0.3528

    def _escribir(self, x_pt, y_pt, texto, estilo='', tamanio_pt=7.0, alineacion='L'):
        """
        Escribe texto con tamaño corregido (×2.5 del original generado).
        """
        x_mm = self._pt_mm(x_pt)
        y_mm = self._pt_mm(y_pt)

        if 'Bold' in estilo:
            self.set_font('Helvetica', 'B', tamanio_pt * 0.3528)
        else:
            self.set_font('Helvetica', '', tamanio_pt * 0.3528)

        self.set_xy(x_mm, y_mm)
        self.cell(0, self._pt_mm(tamanio_pt) + 1.5, texto, align=alineacion)

    def _pagina_1(self):
        self.add_page()
        d = self.datos

        # PIE DE PÁGINA
        self._escribir(511.9, 777.5, 'Página 1 de 2', tamanio_pt=7.0)

        # CÉDULA DE IDENTIFICACIÓN FISCAL
        self._escribir(71.5, 130.0, 'CÉDULA DE IDENTIFICACIÓN FISCAL', estilo='Bold', tamanio_pt=9.0)

        # CONSTANCIA DE SITUACIÓN FISCAL
        self._escribir(420.9, 183.5, 'CONSTANCIA DE SITUACIÓN FISCAL', estilo='Bold', tamanio_pt=10.5, alineacion='C')

        # RFC encabezado
        self._escribir(192.2, 188.3, d['rfc'], tamanio_pt=7.0)

        # Registro Federal de Contribuyentes
        self._escribir(188.9, 199.6, 'Registro Federal de', tamanio_pt=7.0)
        self._escribir(197.4, 208.7, 'Contribuyentes', tamanio_pt=7.0)

        # Lugar y Fecha de Emisión etiqueta
        self._escribir(384.9, 221.7, 'Lugar y Fecha de Emisión', tamanio_pt=9.0)

        # Nombre en 2 líneas
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''
        self._escribir(164.4, 226.0, linea1, tamanio_pt=7.0)
        if linea2:
            self._escribir(198.2, 234.5, linea2, tamanio_pt=7.0)

        # Lugar y fecha valor
        lugar_fecha = f"{d['domicilio']['estado'].upper()}, A {datetime.now().strftime('%d DE %B DE %Y').upper()}"
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            lugar_fecha = lugar_fecha.replace(en, es)
        self._escribir(311.1, 234.8, lugar_fecha, estilo='Bold', tamanio_pt=9.0)

        # Nombre, denominación o razón social
        self._escribir(167.9, 242.3, 'Nombre, denominación o razón', tamanio_pt=7.0)
        self._escribir(214.1, 250.4, 'social', tamanio_pt=7.0)

        # IDCIF
        self._escribir(189.6, 269.1, f'idCIF: {d["idcif"]}', tamanio_pt=7.0)

        # VALIDA TU INFORMACIÓN FISCAL
        self._escribir(173.8, 277.6, 'VALIDA TU INFORMACIÓN', tamanio_pt=7.0)
        self._escribir(210.4, 287.0, 'FISCAL', tamanio_pt=7.0)

        # RFC repetido
        self._escribir(412.8, 290.4, d['rfc'], tamanio_pt=7.0)

        # DATOS DE IDENTIFICACIÓN título
        self._escribir(204.9, 323.6, 'Datos de Identificación del Contribuyente:', estilo='Bold', tamanio_pt=9.0)

        # Campos
        campos_id = [
            ('RFC:', d['rfc'], 346.1, 238.1, 344.3),
            ('CURP:', d['curp'], 367.9, 238.4, 367.0),
            ('Nombre (s):', d.get('nombres', ''), 389.8, 238.4, 389.4),
            ('Primer Apellido:', d.get('primer_apellido', ''), 411.6, 237.6, 409.8),
            ('Segundo Apellido:', d.get('segundo_apellido', ''), 433.4, 237.6, 432.5),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '18 DE OCTUBRE DE 2016'), 455.3, 241.2, 453.5),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO'), 477.1, 236.8, 476.2),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '18 DE OCTUBRE DE 2016'), 498.7, 241.2, 498.8),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre']), 520.7, 238.4, 520.1),
        ]

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in campos_id:
            self._escribir(46.0, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.0)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=7.0)

        # DATOS DEL DOMICILIO REGISTRADO título
        self._escribir(233.6, 553.3, 'Datos del domicilio registrado', estilo='Bold', tamanio_pt=9.0)

        dom = d['domicilio']

        # Columna IZQUIERDA
        dom_izq = [
            ('Código Postal:', dom['codigo_postal'], 575.9, 102.0, 575.1),
            ('Nombre de Vialidad:', dom['calle'].upper(), 597.7, 124.1, 596.1),
            ('Número Interior:', dom.get('numero_interior', ''), 619.6, 108.0, 618.0),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 641.4, 108.0, 640.0),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 663.0, 172.4, 662.1),
        ]

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in dom_izq:
            self._escribir(46.0, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.0)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=7.0)

        # Columna DERECHA
        dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE'), 575.9, 380.5, 575.1),
            ('Número Exterior:', dom['numero_exterior'], 597.7, 381.3, 596.3),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 619.6, 399.8, 617.9),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', ''), 636.6, 314.8, 637.0),
            ('Entre Calle:', dom.get('entre_calle', ''), 663.0, 360.0, 662.0),
        ]

        for etiqueta, valor, y_etiqueta, x_valor, y_valor in dom_der:
            self._escribir(314.8, y_etiqueta, etiqueta, estilo='Bold', tamanio_pt=7.0)
            self._escribir(x_valor, y_valor, str(valor), tamanio_pt=7.0)

        # Y Calle
        self._escribir(45.5, 684.4, 'Y Calle:', estilo='Bold', tamanio_pt=7.0)
        self._escribir(76.0, 684.4, dom.get('y_calle', ''), tamanio_pt=7.0)

    def _pagina_2(self):
        self.add_page()
        d = self.datos

        # PIE DE PÁGINA
        self._escribir(511.9, 777.5, 'Página 2 de 2', tamanio_pt=7.0)

        # ACTIVIDADES ECONÓMICAS título
        self._escribir(244.6, 130.0, 'Actividades Económicas:', estilo='Bold', tamanio_pt=9.0)

        # Cabeceras
        cabeceras_act = [
            (47.9, 148.9, 'Orden'),
            (179.4, 148.9, 'Actividad Económica'),
            (380.3, 148.9, 'Porcentaje'),
            (443.7, 148.9, 'Fecha Inicio'),
            (519.1, 148.9, 'Fecha Fin'),
        ]
        for x, y, texto in cabeceras_act:
            self._escribir(x, y, texto, estilo='Bold', tamanio_pt=9.0)

        # Datos
        self._escribir(40.5, 163.1, d.get('actividad_orden', '1'), tamanio_pt=7.0)
        self._escribir(87.6, 166.5, d.get('actividad_economica', 'Asalariado'), tamanio_pt=7.0)
        self._escribir(374.8, 163.1, d.get('actividad_porcentaje', '100'), tamanio_pt=7.0)
        self._escribir(451.6, 166.5, d.get('actividad_fecha_inicio', '18/10/2016'), tamanio_pt=7.0)

        # REGÍMENES título
        self._escribir(275.4, 201.8, 'Regímenes:', estilo='Bold', tamanio_pt=9.0)

        # Cabeceras
        self._escribir(217.9, 220.7, 'Régimen', estilo='Bold', tamanio_pt=9.0)
        self._escribir(443.7, 220.7, 'Fecha Inicio', estilo='Bold', tamanio_pt=9.0)
        self._escribir(519.1, 220.7, 'Fecha Fin', estilo='Bold', tamanio_pt=9.0)

        # Datos
        self._escribir(43.9, 237.4, d['regimen_fiscal'], tamanio_pt=7.0)
        self._escribir(451.6, 240.2, d.get('regimen_fecha_inicio', '18/10/2016'), tamanio_pt=7.0)

        # AVISOS LEGALES
        avisos = [
            (45.1, 268.3, 'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de'),
            (45.1, 277.9, 'Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las'),
            (45.1, 287.3, 'facultades conferidas a la autoridad fiscal.'),
            (45.1, 309.1, 'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección'),
            (45.1, 318.7, 'http://sat.gob.mx'),
            (45.1, 340.3, '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a'),
            (45.1, 349.9, 'través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o'),
            (45.1, 359.3, 'www.gob.mx/sfp".'),
        ]
        for x, y, texto in avisos:
            self._escribir(x, y, texto, estilo='Bold', tamanio_pt=7.0)

        # CADENA ORIGINAL SELLO
        self._escribir(50.6, 380.9, 'Cadena Original Sello:', estilo='Bold', tamanio_pt=7.0)
        cadena = d.get('cadena_digital', '')
        self._escribir(149.6, 379.2, cadena[:70], tamanio_pt=7.0)
        self._escribir(149.6, 390.5, cadena[70:140] if len(cadena) > 70 else '', tamanio_pt=7.0)
        self._escribir(149.6, 401.9, cadena[140:210] if len(cadena) > 140 else '', tamanio_pt=7.0)

        # SELLO DIGITAL
        self._escribir(50.6, 408.5, 'Sello Digital:', estilo='Bold', tamanio_pt=7.0)
        sello = d.get('sello_digital', '')
        self._escribir(149.6, 413.2, sello[:70], tamanio_pt=7.0)
        self._escribir(149.6, 424.6, sello[70:140] if len(sello) > 70 else '', tamanio_pt=7.0)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
