from fpdf import FPDF
from datetime import datetime
import io
import os


class ConstanciaFiscalBase(FPDF):
    """
    Plantilla base con fondo PNG.
    Sin bordes ni líneas dibujadas (ya vienen en el PNG).
    Tamaño de letra ×2.5.
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)
        
        base_dir = os.getcwd()
        self.ruta_pag1 = os.path.join(base_dir, 'pagina_1.png')
        self.ruta_pag2 = os.path.join(base_dir, 'pagina_2.png')

    def _escribir(self, x_mm, y_mm, texto, negrita=False, tamanio_pt=20, alineacion='L'):
        """
        Escribe texto encima del fondo.
        tamanio_pt ya viene con ×2.5 aplicado.
        """
        if not texto:
            return
        estilo = 'B' if negrita else ''
        self.set_font('Helvetica', estilo, tamanio_pt * 0.3528)
        self.set_xy(x_mm, y_mm)
        self.cell(0, (tamanio_pt * 0.3528) + 2, str(texto), align=alineacion)

    def _pagina_1(self):
        self.add_page()
        
        # FONDO
        if os.path.exists(self.ruta_pag1):
            self.image(self.ruta_pag1, x=0, y=0, w=215.9, h=279.4)
        
        d = self.datos
        dom = d.get('domicilio', {})

        # ============================================================
        # ENCABEZADO (tamaños ×2.5)
        # ============================================================
        # RFC encabezado: 9pt × 2.5 = 22.5 → 22pt
        self._escribir(67, 66, d['rfc'], tamanio_pt=22)

        # Nombre: 9pt × 2.5 = 22pt
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''
        self._escribir(61, 79, linea1, tamanio_pt=22)
        if linea2:
            self._escribir(72, 82, linea2, tamanio_pt=22)

        # Fecha: 9pt × 2.5 = 22pt
        estado = dom.get('estado', 'CIUDAD DE MEXICO').upper()
        fecha = datetime.now().strftime('%d DE %B DE %Y').upper()
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            fecha = fecha.replace(en, es)
        self._escribir(117, 81, f"{estado} , {estado} A {fecha}", negrita=True, tamanio_pt=22)

        # IDCIF: 9pt × 2.5 = 22pt
        self._escribir(76, 94, d['idcif'], tamanio_pt=22)

        # RFC repetido: 9pt × 2.5 = 22pt
        self._escribir(145, 102, d['rfc'], tamanio_pt=22)

        # ============================================================
        # TABLA DATOS DE IDENTIFICACIÓN (8pt × 2.5 = 20pt)
        # ============================================================
        campos = [
            ('rfc', 170), ('curp', 195), ('nombres', 220),
            ('primer_apellido', 245), ('segundo_apellido', 270),
            ('fecha_inicio_operaciones', 295), ('estatus', 295),
            ('fecha_cambio_estado', 320), ('nombre_comercial', 320),
        ]

        valores = {
            'rfc': d['rfc'],
            'curp': d['curp'],
            'nombres': d.get('nombres', ''),
            'primer_apellido': d.get('primer_apellido', ''),
            'segundo_apellido': d.get('segundo_apellido', ''),
            'fecha_inicio_operaciones': d.get('fecha_inicio_operaciones', '31 DE DICIEMBRE DE 2010'),
            'estatus': d.get('estatus', 'ACTIVO'),
            'fecha_cambio_estado': d.get('fecha_cambio_estado', '31 DE DICIEMBRE DE 2010'),
            'nombre_comercial': d.get('nombre_comercial', d['nombre']),
        }

        for campo, y in campos:
            valor = valores.get(campo, '')
            if valor:
                self._escribir(54, y, str(valor), tamanio_pt=20)

        # ============================================================
        # TABLA DOMICILIO (8pt × 2.5 = 20pt)
        # ============================================================
        dom_campos = [
            ('codigo_postal', 405), ('tipo_vialidad', 430), ('calle', 455),
            ('numero_exterior', 480), ('numero_interior', 505), ('colonia', 530),
            ('localidad', 555), ('municipio', 580), ('estado', 605),
            ('entre_calle', 630), ('y_calle', 655),
        ]

        dom_valores = {
            'codigo_postal': dom.get('codigo_postal', ''),
            'tipo_vialidad': dom.get('tipo_vialidad', 'CALLE'),
            'calle': dom.get('calle', '').upper(),
            'numero_exterior': dom.get('numero_exterior', ''),
            'numero_interior': dom.get('numero_interior', ''),
            'colonia': dom.get('colonia', '').upper(),
            'localidad': dom.get('localidad', dom.get('municipio', '')),
            'municipio': dom.get('municipio', ''),
            'estado': dom.get('estado', '').upper(),
            'entre_calle': dom.get('entre_calle', ''),
            'y_calle': dom.get('y_calle', ''),
        }

        for campo, y in dom_campos:
            valor = dom_valores.get(campo, '')
            if valor:
                self._escribir(54, y, str(valor), tamanio_pt=20)

    def _pagina_2(self):
        self.add_page()
        
        # FONDO
        if os.path.exists(self.ruta_pag2):
            self.image(self.ruta_pag2, x=0, y=0, w=215.9, h=279.4)
        
        d = self.datos

        # ============================================================
        # ACTIVIDADES ECONÓMICAS (8pt × 2.5 = 20pt)
        # ============================================================
        self._escribir(13, 56, d.get('actividad_orden', '1'), tamanio_pt=20)
        self._escribir(29, 56, d.get('actividad_economica', 'Asalariado'), tamanio_pt=20)
        self._escribir(131, 56, d.get('actividad_porcentaje', '100'), tamanio_pt=20)
        self._escribir(157, 56, d.get('actividad_fecha_inicio', '31/12/2010'), tamanio_pt=20)

        # ============================================================
        # REGÍMENES (8pt × 2.5 = 20pt)
        # ============================================================
        self._escribir(13, 81, d.get('regimen_fiscal', 'Sueldos y Salarios e Ingresos Asimilados a Salarios'), tamanio_pt=20)
        self._escribir(157, 81, d.get('regimen_fecha_inicio', '31/12/2010'), tamanio_pt=20)

        # ============================================================
        # CADENAS DIGITALES (6pt × 2.5 = 15pt)
        # ============================================================
        cadena = d.get('cadena_digital', '')
        if cadena:
            self._escribir(52, 133, cadena[:80], tamanio_pt=15)
            self._escribir(52, 137, cadena[80:160] if len(cadena) > 80 else '', tamanio_pt=15)

        sello = d.get('sello_digital', '')
        if sello:
            self._escribir(52, 145, sello[:80], tamanio_pt=15)
            self._escribir(52, 149, sello[80:160] if len(sello) > 80 else '', tamanio_pt=15)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalBase(datos)
    return pdf.construir()
