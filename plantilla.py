from fpdf import FPDF
from datetime import datetime
import io
import qrcode


class ConstanciaFiscalPDF(FPDF):
    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        pass

    def footer(self):
        pass

    def construir(self):
        self.add_page()

        MARGEN_IZQ = 25
        ANCHO_TEXTO = 160
        self.set_left_margin(MARGEN_IZQ)

        # TÍTULO
        self.set_y(18)
        self.set_font('Helvetica', 'B', 18)
        self.cell(ANCHO_TEXTO, 8, 'CONSTANCIA DE SITUACION FISCAL', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # SUBTÍTULO
        self.set_font('Helvetica', '', 10)
        self.cell(ANCHO_TEXTO, 5, 'Registro Federal de Contribuyentes', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # RFC GRANDE
        self.set_font('Helvetica', 'B', 26)
        rfc_espaciado = '  '.join(list(self.datos['rfc']))
        self.cell(ANCHO_TEXTO, 10, rfc_espaciado, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # NOMBRE
        self.set_font('Helvetica', '', 10)
        self.cell(ANCHO_TEXTO, 5, self.datos['nombre'], align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        # IDCIF
        self.set_font('Helvetica', '', 8)
        self.cell(ANCHO_TEXTO, 4, f"idCIF: {self.datos['idcif']}", align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # LEYENDA
        self.set_font('Helvetica', '', 9)
        self.cell(ANCHO_TEXTO, 4, 'VALIDA TU INFORMACION FISCAL', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # LUGAR Y FECHA
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

        self.set_font('Helvetica', '', 9)
        self.cell(ANCHO_TEXTO, 4, f"{lugar}, A {fecha_emision}", align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # SEPARADOR
        self.line(MARGEN_IZQ, self.get_y(), MARGEN_IZQ + ANCHO_TEXTO, self.get_y())
        self.ln(4)

        # DATOS DE IDENTIFICACIÓN
        self.set_font('Helvetica', 'B', 10)
        self.cell(ANCHO_TEXTO, 5, 'Datos de Identificacion del Contribuyente:', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        self.set_font('Helvetica', '', 9)
        datos_id = [
            f"RFC: {self.datos['rfc']}",
            f"CURP: {self.datos['curp']}",
            f"Nombre o Razon Social: {self.datos['nombre']}",
            "",
            f"Fecha de Inicio de Operaciones: 18 de octubre de 2016",
            f"Estatus en el padron: ACTIVO",
            f"Fecha de ultimo cambio de estado: 18 de octubre de 2016",
            f"Nombre Comercial: ",
        ]
        for linea in datos_id:
            if linea:
                self.cell(ANCHO_TEXTO, 4, linea, new_x="LMARGIN", new_y="NEXT")
            else:
                self.ln(2)
        self.ln(4)

        # DOMICILIO
        self.set_font('Helvetica', 'B', 10)
        self.cell(ANCHO_TEXTO, 5, 'Datos del domicilio registrado:', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        self.set_font('Helvetica', '', 9)
        dom = self.datos['domicilio']
        datos_dom = [
            f"Codigo Postal: {dom['codigo_postal']}",
            f"Vialidad: {dom['calle'].upper()}",
            f"Numero Exterior: {dom['numero_exterior']}",
            f"Numero Interior: {dom['numero_interior'] if dom['numero_interior'] else ''}",
            f"Colonia: {dom['colonia'].upper()}",
            f"Localidad: {dom.get('localidad', '')}",
            f"Municipio o Alcaldia: {dom.get('municipio', '')}",
            f"Entidad Federativa: {dom['estado'].upper()}",
            f"Y Calle: ",
            f"O Calle: ",
        ]
        for linea in datos_dom:
            self.cell(ANCHO_TEXTO, 4, linea, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # ACTIVIDADES ECONÓMICAS
        self.set_font('Helvetica', 'B', 10)
        self.cell(ANCHO_TEXTO, 5, 'Actividades Economicas:', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        self.set_font('Helvetica', '', 8)
        col_anchos = [10, 100, 20, 20, 20]
        cabeceras = ['Ord.', 'Actividad Economica', 'Porcentaje', 'Fecha Inicio', 'Fecha Fin']
        for i, cab in enumerate(cabeceras):
            self.cell(col_anchos[i], 4, cab, border=0)
        self.ln(5)

        self.set_font('Helvetica', '', 8)
        self.cell(col_anchos[0], 4, '1')
        self.cell(col_anchos[1], 4, '')
        self.cell(col_anchos[2], 4, '100%')
        self.cell(col_anchos[3], 4, '18/10/2016')
        self.cell(col_anchos[4], 4, '')
        self.ln(6)

        # REGÍMENES
        self.set_font('Helvetica', 'B', 10)
        self.cell(ANCHO_TEXTO, 5, 'Regimenes:', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        self.set_font('Helvetica', '', 8)
        col_anchos_reg = [130, 25, 25]
        cabeceras_reg = ['Regimen', 'Fecha Inicio', 'Fecha Fin']
        for i, cab in enumerate(cabeceras_reg):
            self.cell(col_anchos_reg[i], 4, cab, border=0)
        self.ln(5)

        self.set_font('Helvetica', '', 8)
        self.cell(col_anchos_reg[0], 4, self.datos['regimen_fiscal'])
        self.cell(col_anchos_reg[1], 4, '18/10/2016')
        self.cell(col_anchos_reg[2], 4, '')
        self.ln(6)

        # PIE LEGAL
        self.set_y(210)
        self.set_font('Helvetica', '', 7)
        texto_legal = (
            "En atencion a lo dispuesto en los articulos 3, 16, 17, 18, 31 y demas relativos de la Ley General de "
            "Proteccion de Datos Personales en Posesion de Sujetos Obligados, se informa que los datos personales "
            "recabados seran protegidos, incorporados y tratados en el sistema de datos personales denominado "
            "Registro Federal de Contribuyentes..."
        )
        self.set_x(MARGEN_IZQ)
        self.multi_cell(ANCHO_TEXTO, 3, texto_legal, align='J')
        self.ln(2)

        self.set_font('Helvetica', '', 7)
        texto_anticorrupcion = (
            "El SAT te invita a denunciar actos de corrupcion al telefono 55-8852-2222 o al correo "
            "denuncias@sat.gob.mx. Tu denuncia es confidencial."
        )
        self.set_x(MARGEN_IZQ)
        self.multi_cell(ANCHO_TEXTO, 3, texto_anticorrupcion, align='J')
        self.ln(4)

        # CADENA DIGITAL
        self.set_font('Helvetica', 'B', 8)
        self.cell(ANCHO_TEXTO, 4, 'Cadena Original Sello:', new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        self.set_font('Courier', '', 7)
        cadena = self.datos['cadena_digital']
        lineas_cadena = [cadena[i:i+80] for i in range(0, min(len(cadena), 240), 80)]
        for linea in lineas_cadena:
            self.set_x(MARGEN_IZQ)
            self.cell(ANCHO_TEXTO, 3, linea, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # SELLO DIGITAL
        self.set_font('Helvetica', 'B', 8)
        self.cell(ANCHO_TEXTO, 4, 'Sello Digital:', new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        self.set_font('Courier', '', 7)
        sello = self.datos['sello_digital']
        lineas_sello = [sello[i:i+80] for i in range(0, len(sello), 80)]
        for linea in lineas_sello:
            self.set_x(MARGEN_IZQ)
            self.cell(ANCHO_TEXTO, 3, linea, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # FOLIO
        self.set_font('Courier', '', 7)
        self.set_x(MARGEN_IZQ)
        self.cell(ANCHO_TEXTO, 3, '200001088888800000031', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        # QR
        qr_img = io.BytesIO()
        img = qrcode.make(self.datos['url_qr'])
        img.save(qr_img, format='PNG')
        qr_img.seek(0)

        self.image(qr_img, x=145, y=255, w=35)
        self.set_xy(145, 291)
        self.set_font('Helvetica', '', 6)
        self.cell(35, 3, 'Verifica tu constancia', align='C')

        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalPDF(datos)
    return pdf.construir()
