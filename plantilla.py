from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    """
    Plantilla idéntica a la Constancia de Situación Fiscal del SAT.
    Coordenadas basadas en análisis de PDF real.
    Tamaño: Carta (210 x 297 mm)
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)

    def construir(self):
        self.add_page()

        MARGEN_IZQ = 20
        ANCHO_TEXTO = 170

        # ============================================================
        # 1. TÍTULO PRINCIPAL
        # ============================================================
        self.set_font('Helvetica', 'B', 20)
        self.set_xy(MARGEN_IZQ, 18)
        self.cell(ANCHO_TEXTO, 9, 'CONSTANCIA DE SITUACION FISCAL', align='C')

        # ============================================================
        # 2. SUBTÍTULO
        # ============================================================
        self.set_font('Helvetica', '', 11)
        self.set_xy(MARGEN_IZQ, 30)
        self.cell(ANCHO_TEXTO, 6, 'Registro Federal de Contribuyentes', align='C')

        # ============================================================
        # 3. RFC GRANDE (ESPACIADO)
        # ============================================================
        self.set_font('Helvetica', 'B', 26)
        rfc_espaciado = '  '.join(list(self.datos['rfc']))
        self.set_xy(MARGEN_IZQ, 39)
        self.cell(ANCHO_TEXTO, 12, rfc_espaciado, align='C')

        # ============================================================
        # 4. NOMBRE COMPLETO
        # ============================================================
        self.set_font('Helvetica', '', 11)
        self.set_xy(MARGEN_IZQ, 52)
        self.cell(ANCHO_TEXTO, 6, self.datos['nombre'], align='C')

        # ============================================================
        # 5. IDCIF
        # ============================================================
        self.set_font('Helvetica', '', 9)
        self.set_xy(MARGEN_IZQ, 60)
        self.cell(ANCHO_TEXTO, 5, f"idCIF: {self.datos['idcif']}", align='C')

        # ============================================================
        # 6. LEYENDA DE VALIDACIÓN
        # ============================================================
        self.set_font('Helvetica', '', 10)
        self.set_xy(MARGEN_IZQ, 67)
        self.cell(ANCHO_TEXTO, 5, 'VALIDA TU INFORMACION FISCAL', align='C')

        # ============================================================
        # 7. LUGAR Y FECHA DE EMISIÓN
        # ============================================================
        lugar = self.datos['domicilio'].get('estado', 'CIUDAD DE MEXICO').upper()
        fecha_emision = datetime.now().strftime('%d DE %B DE %Y').upper()
        meses = {
            'JANUARY': 'ENERO', 'FEBRUARY': 'FEBRERO', 'MARCH': 'MARZO',
            'APRIL': 'ABRIL', 'MAY': 'MAYO', 'JUNE': 'JUNIO',
            'JULY': 'JULIO', 'AUGUST': 'AGOSTO', 'SEPTEMBER': 'SEPTIEMBRE',
            'OCTOBER': 'OCTUBRE', 'NOVEMBER': 'NOVIEMBRE', 'DECEMBER': 'DICIEMBRE'
        }
        for en, es in meses.items():
            fecha_emision = fecha_emision.replace(en, es)

        self.set_font('Helvetica', '', 10)
        self.set_xy(MARGEN_IZQ, 75)
        self.cell(ANCHO_TEXTO, 5, f"{lugar}, A {fecha_emision}", align='C')

        # ============================================================
        # 8. SECCIÓN: DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE
        # ============================================================
        self.set_font('Helvetica', 'B', 11)
        self.set_xy(MARGEN_IZQ, 87)
        self.cell(ANCHO_TEXTO, 5, 'Datos de Identificacion del Contribuyente:')

        campos_id = [
            ('RFC:', self.datos['rfc'], 94),
            ('CURP:', self.datos['curp'], 99),
            ('Nombre (s):', self.datos.get('nombres', ''), 104),
            ('Primer Apellido:', self.datos.get('primer_apellido', ''), 109),
            ('Segundo Apellido:', self.datos.get('segundo_apellido', ''), 114),
            ('Fecha inicio de operaciones:', '18 DE OCTUBRE DE 2016', 119),
            ('Estatus en el padron:', 'ACTIVO', 124),
            ('Fecha de ultimo cambio de estado:', '18 DE OCTUBRE DE 2016', 129),
            ('Nombre Comercial:', self.datos['nombre'], 134),
        ]

        for etiqueta, valor, y in campos_id:
            self.set_font('Helvetica', 'B', 9)
            self.set_xy(MARGEN_IZQ, y)
            self.cell(45, 4, etiqueta)
            self.set_font('Helvetica', '', 9)
            self.set_xy(MARGEN_IZQ + 45, y)
            self.cell(125, 4, str(valor))

        # ============================================================
        # 9. SECCIÓN: DATOS DEL DOMICILIO REGISTRADO
        # ============================================================
        self.set_font('Helvetica', 'B', 11)
        self.set_xy(MARGEN_IZQ, 143)
        self.cell(ANCHO_TEXTO, 5, 'Datos del domicilio registrado:')

        dom = self.datos['domicilio']
        campos_dom = [
            ('Codigo Postal:', dom['codigo_postal'], 150),
            ('Tipo de Vialidad:', 'CALLE', 155),
            ('Nombre de Vialidad:', dom['calle'].upper(), 160),
            ('Numero Exterior:', dom['numero_exterior'], 165),
            ('Numero Interior:', dom.get('numero_interior', ''), 170),
            ('Nombre de la Colonia:', dom['colonia'].upper(), 175),
            ('Nombre de la Localidad:', dom.get('localidad', dom.get('municipio', '')), 180),
            ('Nombre del Municipio o Demarcacion Territorial:', dom.get('municipio', ''), 185),
            ('Nombre de la Entidad Federativa:', dom['estado'].upper(), 190),
            ('Entre Calle:', '', 195),
            ('Y Calle:', '', 200),
        ]

        for etiqueta, valor, y in campos_dom:
            self.set_font('Helvetica', 'B', 9)
            self.set_xy(MARGEN_IZQ, y)
            ancho_etiqueta = 60 if 'Municipio' in etiqueta or 'Demarcacion' in etiqueta else 40
            self.cell(ancho_etiqueta, 4, etiqueta)
            self.set_font('Helvetica', '', 9)
            self.set_xy(MARGEN_IZQ + ancho_etiqueta, y)
            self.cell(ANCHO_TEXTO - ancho_etiqueta, 4, str(valor))

        # ============================================================
        # 10. ACTIVIDADES ECONÓMICAS
        # ============================================================
        self.set_font('Helvetica', 'B', 11)
        self.set_xy(MARGEN_IZQ, 210)
        self.cell(ANCHO_TEXTO, 5, 'Actividades Economicas:')

        col_act = [15, 60, 20, 30, 30]
        cabeceras_act = ['Orden', 'Actividad Economica', 'Porcentaje', 'Fecha Inicio', 'Fecha Fin']
        x_act = [MARGEN_IZQ, MARGEN_IZQ + 15, MARGEN_IZQ + 75, MARGEN_IZQ + 95, MARGEN_IZQ + 125]

        self.set_font('Helvetica', 'B', 9)
        for cab, x, w in zip(cabeceras_act, x_act, col_act):
            self.set_xy(x, 217)
            self.cell(w, 4, cab)

        self.set_font('Helvetica', '', 9)
        self.set_xy(x_act[0], 222)
        self.cell(col_act[0], 4, '1')
        self.set_xy(x_act[1], 222)
        self.cell(col_act[1], 4, '')
        self.set_xy(x_act[2], 222)
        self.cell(col_act[2], 4, '100')
        self.set_xy(x_act[3], 222)
        self.cell(col_act[3], 4, '18/10/2016')
        self.set_xy(x_act[4], 222)
        self.cell(col_act[4], 4, '')

        # ============================================================
        # 11. REGÍMENES
        # ============================================================
        self.set_font('Helvetica', 'B', 11)
        self.set_xy(MARGEN_IZQ, 235)
        self.cell(ANCHO_TEXTO, 5, 'Regimenes:')

        col_reg = [60, 30, 30]
        cabeceras_reg = ['Regimen', 'Fecha Inicio', 'Fecha Fin']
        x_reg = [MARGEN_IZQ, MARGEN_IZQ + 60, MARGEN_IZQ + 90]

        self.set_font('Helvetica', 'B', 9)
        for cab, x, w in zip(cabeceras_reg, x_reg, col_reg):
            self.set_xy(x, 242)
            self.cell(w, 4, cab)

        self.set_font('Helvetica', '', 9)
        # Fila 1: nombre corto
        self.set_xy(x_reg[0], 247)
        self.cell(col_reg[0], 4, 'Asalariado')
        self.set_xy(x_reg[1], 247)
        self.cell(col_reg[1], 4, '18/10/2016')
        self.set_xy(x_reg[2], 247)
        self.cell(col_reg[2], 4, '18/10/2016')
        # Fila 2: nombre largo del régimen
        self.set_xy(x_reg[0], 252)
        self.cell(col_reg[0], 4, self.datos['regimen_fiscal'])
        self.set_xy(x_reg[1], 252)
        self.cell(col_reg[1], 4, '')
        self.set_xy(x_reg[2], 252)
        self.cell(col_reg[2], 4, '')

        # ============================================================
        # 12. TEXTOS LEGALES
        # ============================================================
        self.set_font('Helvetica', '', 7.5)
        texto_proteccion = (
            "Sus datos personales son incorporados y protegidos en los sistemas del SAT, "
            "con fundamento en los articulos 3, 16, 17, 18, 31 y demas relativos de la "
            "Ley General de Proteccion de Datos Personales en Posesion de Sujetos Obligados."
        )
        self.set_xy(MARGEN_IZQ, 265)
        self.multi_cell(ANCHO_TEXTO, 3.5, texto_proteccion, align='J')

        texto_corrupcion = (
            'La corrupcion tiene consecuencias. Denuncia al telefono 55-8852-2222, '
            'al correo denuncias@sat.gob.mx o en www.gob.mx/sfp'
        )
        self.set_xy(MARGEN_IZQ, 278)
        self.multi_cell(ANCHO_TEXTO, 3.5, texto_corrupcion, align='J')

        # ============================================================
        # 13. CADENA DIGITAL Y SELLO DIGITAL
        # ============================================================
        self.set_font('Helvetica', 'B', 9)
        self.set_xy(MARGEN_IZQ, 290)
        self.cell(ANCHO_TEXTO, 4, 'Cadena Original Sello:')

        self.set_font('Helvetica', '', 7.5)
        cadena = self.datos.get('cadena_digital', '')
        self.set_xy(MARGEN_IZQ, 294)
        self.cell(ANCHO_TEXTO, 4, cadena[:90])

        self.set_font('Helvetica', 'B', 9)
        self.set_xy(MARGEN_IZQ, 300)
        self.cell(ANCHO_TEXTO, 4, 'Sello Digital:')

        self.set_font('Helvetica', '', 7.5)
        sello = self.datos.get('sello_digital', '')
        self.set_xy(MARGEN_IZQ, 304)
        self.cell(ANCHO_TEXTO, 4, sello[:90])

        # ============================================================
        # 14. CÓDIGO QR (ESQUINA INFERIOR DERECHA)
        # ============================================================
        qr_img = io.BytesIO()
        img = qrcode.make(self.datos['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        self.image(qr_img, x=155, y=265, w=30)
        self.set_font('Helvetica', '', 6)
        self.set_xy(155, 296)
        self.cell(30, 3, 'Verifica tu constancia', align='C')

        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
