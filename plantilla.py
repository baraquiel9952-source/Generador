from fpdf import FPDF
from datetime import datetime
import json
import io


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla de Constancia de Situación Fiscal del SAT.
    Basada en PDF original NXCA810924MASVRL01.
    Tamaños corregidos: títulos 40pt, datos 32pt.
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def _escribir(self, x_mm, y_mm, texto, estilo='', tamanio_mm=8, alineacion='L'):
        """Escribe texto con fuente Helvetica (Arial equivalente)."""
        if 'B' in estilo:
            self.set_font('Helvetica', 'B', tamanio_mm)
        else:
            self.set_font('Helvetica', '', tamanio_mm)
        self.set_xy(x_mm, y_mm)
        self.cell(0, tamanio_mm + 1, texto, align=alineacion)

    def _pagina_1(self):
        self.add_page()
        d = self.datos
        dom = d['domicilio']

        # Escala: el original NXCA tiene 2448px de ancho para carta (215.9mm)
        # Factor: 215.9 / 2448 = 0.0882 mm/px
        # Pero vamos a usar posiciones aproximadas basadas en el JSON

        # === PIE DE PÁGINA ===
        self._escribir(180, 273, 'Página 1 de 2', tamanio_mm=6)

        # === CÉDULA DE IDENTIFICACIÓN FISCAL (40pt = 14mm) ===
        self._escribir(10, 45, 'CÉDULA DE IDENTIFICACIÓN FISCAL', estilo='B', tamanio_mm=11)

        # === CONSTANCIA DE SITUACIÓN FISCAL (48pt = 17mm) ===
        self._escribir(10, 63, 'CONSTANCIA DE SITUACIÓN FISCAL', estilo='B', tamanio_mm=13)

        # === RFC en encabezado (32pt = 11mm) ===
        self._escribir(10, 78, d['rfc'], tamanio_mm=9)

        # === Registro Federal de Contribuyentes ===
        self._escribir(10, 90, 'Registro Federal de', tamanio_mm=9)
        self._escribir(10, 98, 'Contribuyentes', tamanio_mm=9)

        # === Lugar y Fecha de Emisión (40pt título, 32pt valor) ===
        self._escribir(100, 77, 'Lugar y Fecha de Emisión', tamanio_mm=9)
        
        # Formato: "ESTADO , ESTADO A DD DE MES DE AAAA"
        estado = dom['estado'].upper()
        fecha = datetime.now().strftime('%d DE %B DE %Y').upper()
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            fecha = fecha.replace(en, es)
        
        lugar_fecha = f"{estado} , {estado} A {fecha}"
        self._escribir(100, 85, lugar_fecha, estilo='B', tamanio_mm=9)

        # === Nombre del contribuyente ===
        self._escribir(10, 108, d['nombre'], tamanio_mm=9)

        # === Nombre, denominación o razón social ===
        self._escribir(10, 117, 'Nombre, denominación o razón', tamanio_mm=8)
        self._escribir(10, 124, 'social', tamanio_mm=8)

        # === IDCIF ===
        self._escribir(10, 134, f"idCIF: {d['idcif']}", tamanio_mm=9)

        # === VALIDA TU INFORMACIÓN FISCAL ===
        self._escribir(10, 143, 'VALIDA TU INFORMACIÓN', tamanio_mm=9)
        self._escribir(10, 151, 'FISCAL', tamanio_mm=9)

        # === RFC repetido (esquina derecha) ===
        self._escribir(140, 143, d['rfc'], tamanio_mm=9)

        # === DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE (40pt) ===
        self._escribir(10, 165, 'Datos de Identificación del Contribuyente:', estilo='B', tamanio_mm=11)

        # Campos de identificación (etiqueta 32pt, valor 32pt)
        campos_id = [
            ('RFC:', d['rfc']),
            ('CURP:', d['curp']),
            ('Nombre (s):', d.get('nombres', '')),
            ('Primer Apellido:', d.get('primer_apellido', '')),
            ('Segundo Apellido:', d.get('segundo_apellido', '')),
            ('Fecha inicio de operaciones:', d.get('fecha_inicio_operaciones', '31 DE DICIEMBRE DE 2010')),
            ('Estatus en el padrón:', d.get('estatus', 'ACTIVO')),
            ('Fecha de último cambio de estado:', d.get('fecha_cambio_estado', '31 DE DICIEMBRE DE 2010')),
            ('Nombre Comercial:', d.get('nombre_comercial', d['nombre'])),
        ]

        y_campo = 178
        for etiqueta, valor in campos_id:
            self._escribir(10, y_campo, etiqueta, estilo='B', tamanio_mm=8)
            self._escribir(60, y_campo, str(valor), tamanio_mm=8)
            y_campo += 10

        # === DATOS DEL DOMICILIO REGISTRADO (40pt) ===
        y_campo += 5
        self._escribir(10, y_campo, 'Datos del domicilio registrado', estilo='B', tamanio_mm=11)
        y_campo += 12

        # Columna izquierda
        dom_izq = [
            ('Código Postal:', dom['codigo_postal']),
            ('Nombre de Vialidad:', dom.get('calle', 'SIN NOMBRE').upper()),
            ('Número Interior:', dom.get('numero_interior', '')),
            ('Nombre de la Localidad:', dom.get('localidad', '')),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper()),
            ('Y Calle:', dom.get('y_calle', '')),
        ]

        for etiqueta, valor in dom_izq:
            self._escribir(10, y_campo, etiqueta, estilo='B', tamanio_mm=8)
            self._escribir(55, y_campo, str(valor), tamanio_mm=8)
            y_campo += 10

        # Reset Y para columna derecha
        y_campo_der = y_campo - (len(dom_izq) * 10)

        dom_der = [
            ('Tipo de Vialidad:', dom.get('tipo_vialidad', 'CALLE')),
            ('Número Exterior:', dom.get('numero_exterior', '')),
            ('Nombre de la Colonia:', dom.get('colonia', '').upper()),
            ('Nombre del Municipio o Demarcación Territorial:', dom.get('municipio', '')),
            ('Entre Calle:', dom.get('entre_calle', '')),
        ]

        for etiqueta, valor in dom_der:
            self._escribir(110, y_campo_der, etiqueta, estilo='B', tamanio_mm=8)
            self._escribir(175, y_campo_der, str(valor), tamanio_mm=8)
            y_campo_der += 10

    def _pagina_2(self):
        self.add_page()
        d = self.datos

        # === PIE DE PÁGINA ===
        self._escribir(180, 273, 'Página 2 de 2', tamanio_mm=6)

        # === ACTIVIDADES ECONÓMICAS (40pt) ===
        self._escribir(10, 45, 'Actividades Económicas:', estilo='B', tamanio_mm=11)

        # Cabeceras (40pt)
        self._escribir(10, 55, 'Orden', estilo='B', tamanio_mm=9)
        self._escribir(30, 55, 'Actividad Económica', estilo='B', tamanio_mm=9)
        self._escribir(100, 55, 'Porcentaje', estilo='B', tamanio_mm=9)
        self._escribir(125, 55, 'Fecha Inicio', estilo='B', tamanio_mm=9)
        self._escribir(155, 55, 'Fecha Fin', estilo='B', tamanio_mm=9)

        # Datos
        self._escribir(10, 65, d.get('actividad_orden', '1'), tamanio_mm=8)
        self._escribir(30, 65, d.get('actividad_economica', 'Asalariado'), tamanio_mm=8)
        self._escribir(100, 65, d.get('actividad_porcentaje', '100'), tamanio_mm=8)
        self._escribir(125, 65, d.get('actividad_fecha_inicio', '31/12/2010'), tamanio_mm=8)

        # === REGÍMENES (40pt) ===
        self._escribir(10, 85, 'Regímenes:', estilo='B', tamanio_mm=11)

        # Cabeceras
        self._escribir(10, 95, 'Régimen', estilo='B', tamanio_mm=9)
        self._escribir(125, 95, 'Fecha Inicio', estilo='B', tamanio_mm=9)
        self._escribir(155, 95, 'Fecha Fin', estilo='B', tamanio_mm=9)

        # Datos (nombre oficial largo del SAT)
        self._escribir(10, 105, d['regimen_fiscal'], tamanio_mm=8)
        self._escribir(125, 105, d.get('regimen_fecha_inicio', '31/12/2010'), tamanio_mm=8)

        # === AVISOS LEGALES ===
        y_aviso = 130
        avisos = [
            'Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de',
            'Datos Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las',
            'facultades conferidas a la autoridad fiscal.',
            'Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección',
            'http://sat.gob.mx',
            '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a',
            'través de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o',
            'www.gob.mx/sfp".',
        ]

        for aviso in avisos:
            self._escribir(10, y_aviso, aviso, tamanio_mm=6)
            y_aviso += 7

        # === CADENA ORIGINAL Y SELLO DIGITAL ===
        y_aviso += 5
        self._escribir(10, y_aviso, 'Cadena Original Sello:', estilo='B', tamanio_mm=7)
        y_aviso += 6
        cadena = d.get('cadena_digital', '')
        self._escribir(10, y_aviso, cadena[:90], tamanio_mm=6)
        y_aviso += 5
        self._escribir(10, y_aviso, cadena[90:180] if len(cadena) > 90 else '', tamanio_mm=6)
        y_aviso += 5
        self._escribir(10, y_aviso, cadena[180:270] if len(cadena) > 180 else '', tamanio_mm=6)

        y_aviso += 8
        self._escribir(10, y_aviso, 'Sello Digital:', estilo='B', tamanio_mm=7)
        y_aviso += 6
        sello = d.get('sello_digital', '')
        self._escribir(10, y_aviso, sello[:90], tamanio_mm=6)
        y_aviso += 5
        self._escribir(10, y_aviso, sello[90:180] if len(sello) > 90 else '', tamanio_mm=6)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
