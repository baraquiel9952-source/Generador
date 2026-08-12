from fpdf import FPDF
from datetime import datetime
import io
import os


class ConstanciaFiscalBase(FPDF):
    """
    Plantilla base con fondo PNG.
    Coordenadas corregidas según comparación con original NXCA.
    Tamaño ×2.5.
    """

    def __init__(self, datos):
        super().__init__('P', 'mm', 'Letter')
        self.datos = datos
        self.set_auto_page_break(auto=False, margin=0)
        
        base_dir = os.getcwd()
        self.ruta_pag1 = os.path.join(base_dir, 'pagina_1.png')
        self.ruta_pag2 = os.path.join(base_dir, 'pagina_2.png')
        
        # Factor de conversión px → mm (2448px = 215.9mm)
        self.f = 215.9 / 2448

    def _px(self, px):
        """Convierte píxeles a mm."""
        return px * self.f

    def _escribir(self, x_px, y_px, texto, negrita=False, tamanio_pt=20, alineacion='L'):
        """
        Escribe texto en coordenadas px (convertidas a mm).
        tamanio_pt ya viene con ×2.5 aplicado.
        """
        if not texto:
            return
        x_mm = self._px(x_px)
        y_mm = self._px(y_px)
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
        # ENCABEZADO (coordenadas del original NXCA)
        # ============================================================
        # RFC encabezado: original NXCA en (763, 749)
        self._escribir(763, 749, d['rfc'], tamanio_pt=22)

        # Registro Federal de Contribuyentes
        self._escribir(745, 783, 'Registro Federal de', tamanio_pt=18)
        self._escribir(778, 819, 'Contribuyentes', tamanio_pt=18)

        # Nombre línea 1: original en (693, 894)
        nombre_partes = d['nombre'].split()
        linea1 = ' '.join(nombre_partes[:3]) if len(nombre_partes) >= 3 else d['nombre']
        linea2 = ' '.join(nombre_partes[3:]) if len(nombre_partes) > 3 else ''
        self._escribir(693, 894, linea1, tamanio_pt=22)
        if linea2:
            self._escribir(817, 928, linea2, tamanio_pt=22)

        # Fecha emisión: original en (1331, 915)
        estado = dom.get('estado', 'CIUDAD DE MEXICO').upper()
        fecha = datetime.now().strftime('%d DE %B DE %Y').upper()
        meses = {'JANUARY':'ENERO','FEBRUARY':'FEBRERO','MARCH':'MARZO','APRIL':'ABRIL',
                 'MAY':'MAYO','JUNE':'JUNIO','JULY':'JULIO','AUGUST':'AGOSTO',
                 'SEPTEMBER':'SEPTIEMBRE','OCTOBER':'OCTUBRE','NOVEMBER':'NOVIEMBRE','DECEMBER':'DICIEMBRE'}
        for en, es in meses.items():
            fecha = fecha.replace(en, es)
        self._escribir(1331, 915, f"{estado} , {estado} A {fecha}", negrita=True, tamanio_pt=22)

        # IDCIF: original en (1649, 1066)
        self._escribir(1649, 1066, d['idcif'], tamanio_pt=22)

        # VALIDA TU INFORMACIÓN FISCAL
        self._escribir(684, 1100, 'VALIDA TU INFORMACIÓN', tamanio_pt=18)
        self._escribir(830, 1138, 'FISCAL', tamanio_pt=18)

        # RFC repetido: original en (1640, 1151)
        self._escribir(1640, 1151, d['rfc'], tamanio_pt=22)

        # ============================================================
        # TABLA DATOS DE IDENTIFICACIÓN
        # Coordenadas EXACTAS del original NXCA
        # ============================================================
        # Título de sección
        self._escribir(808, 1276, 'Datos de Identificación del Contribuyente:', negrita=True, tamanio_pt=22)

        # Etiquetas (columna izquierda, x≈172-300)
        etiquetas = [
            (172, 1369, 'RFC:'),
            (172, 1456, 'CURP:'),
            (172, 1544, 'Nombre (s):'),
            (172, 1631, 'Primer Apellido:'),
            (172, 1719, 'Segundo Apellido:'),
            (172, 1806, 'Fecha inicio de operaciones:'),
            (172, 1894, 'Estatus en el padrón:'),
            (172, 1980, 'Fecha de último cambio de estado:'),
            (172, 2067, 'Nombre Comercial:'),
        ]
        for x, y, etiqueta in etiquetas:
            self._escribir(x, y, etiqueta, negrita=True, tamanio_pt=20)

        # Valores (columna derecha, x≈942)
        valores_id = [
            (942, 1369, d['rfc']),
            (942, 1456, d['curp']),
            (942, 1544, d.get('nombres', '')),
            (942, 1631, d.get('primer_apellido', '')),
            (942, 1719, d.get('segundo_apellido', '')),
            (942, 1806, d.get('fecha_inicio_operaciones', '31 DE DICIEMBRE DE 2010')),
            (942, 1894, d.get('estatus', 'ACTIVO')),
            (942, 1980, d.get('fecha_cambio_estado', '31 DE DICIEMBRE DE 2010')),
            (942, 2067, d.get('nombre_comercial', d['nombre'])),
        ]
        for x, y, valor in valores_id:
            if valor:
                self._escribir(x, y, str(valor), tamanio_pt=20)

        # ============================================================
        # TABLA DOMICILIO
        # ============================================================
        self._escribir(922, 2195, 'Datos del domicilio registrado', negrita=True, tamanio_pt=22)

        # Columna IZQUIERDA
        dom_izq = [
            (172, 2288, 'Código Postal:', 'codigo_postal'),
            (172, 2376, 'Nombre de Vialidad:', 'calle'),
            (172, 2463, 'Número Interior:', 'numero_interior'),
            (172, 2551, 'Nombre de la Localidad:', 'localidad'),
            (172, 2637, 'Nombre de la Entidad Federativa:', 'estado'),
            (170, 2723, 'Y Calle:', 'y_calle'),
        ]
        for x, y, etiqueta, campo in dom_izq:
            self._escribir(x, y, etiqueta, negrita=True, tamanio_pt=20)
            val = dom.get(campo, '')
            if campo == 'calle':
                val = val.upper()
            elif campo == 'estado':
                val = val.upper()
            if val:
                self._escribir(x + 225, y, str(val), tamanio_pt=20)

        # Columna DERECHA
        dom_der = [
            (1247, 2288, 'Tipo de Vialidad:', 'tipo_vialidad'),
            (1247, 2376, 'Número Exterior:', 'numero_exterior'),
            (1247, 2463, 'Nombre de la Colonia:', 'colonia'),
            (1247, 2532, 'Nombre del Municipio o Demarcación Territorial:', 'municipio'),
            (1247, 2637, 'Entre Calle:', 'entre_calle'),
        ]
        for x, y, etiqueta, campo in dom_der:
            self._escribir(x, y, etiqueta, negrita=True, tamanio_pt=20)
            val = dom.get(campo, '')
            if campo == 'colonia':
                val = val.upper()
            if campo == 'tipo_vialidad' and not val:
                val = 'CALLE'
            if val:
                self._escribir(x + 264, y, str(val), tamanio_pt=20)

    def _pagina_2(self):
        self.add_page()
        
        # FONDO
        if os.path.exists(self.ruta_pag2):
            self.image(self.ruta_pag2, x=0, y=0, w=215.9, h=279.4)
        
        d = self.datos

        # ============================================================
        # ACTIVIDADES ECONÓMICAS (original NXCA)
        # ============================================================
        self._escribir(967, 501, 'Actividades Económicas:', negrita=True, tamanio_pt=22)

        # Cabeceras
        self._escribir(180, 577, 'Orden', negrita=True, tamanio_pt=20)
        self._escribir(705, 577, 'Actividad Económica', negrita=True, tamanio_pt=20)
        self._escribir(1509, 577, 'Porcentaje', negrita=True, tamanio_pt=20)
        self._escribir(1763, 577, 'Fecha Inicio', negrita=True, tamanio_pt=20)
        self._escribir(2065, 577, 'Fecha Fin', negrita=True, tamanio_pt=20)

        # Datos
        self._escribir(150, 637, d.get('actividad_orden', '1'), tamanio_pt=20)
        self._escribir(331, 637, d.get('actividad_economica', 'Asalariado'), tamanio_pt=20)
        self._escribir(1487, 637, d.get('actividad_porcentaje', '100'), tamanio_pt=20)
        self._escribir(1784, 656, d.get('actividad_fecha_inicio', '31/12/2010'), tamanio_pt=20)

        # ============================================================
        # REGÍMENES (original NXCA)
        # ============================================================
        self._escribir(1090, 789, 'Regímenes:', negrita=True, tamanio_pt=22)

        self._escribir(860, 865, 'Régimen', negrita=True, tamanio_pt=20)
        self._escribir(1763, 865, 'Fecha Inicio', negrita=True, tamanio_pt=20)
        self._escribir(2065, 865, 'Fecha Fin', negrita=True, tamanio_pt=20)

        self._escribir(150, 923, d.get('regimen_fiscal', 'Sueldos y Salarios e Ingresos Asimilados a Salarios'), tamanio_pt=20)
        self._escribir(1784, 940, d.get('regimen_fecha_inicio', '31/12/2010'), tamanio_pt=20)

        # ============================================================
        # CADENAS DIGITALES
        # ============================================================
        self._escribir(191, 1508, 'Cadena Original Sello:', negrita=True, tamanio_pt=15)
        cadena = d.get('cadena_digital', '')
        if cadena:
            self._escribir(587, 1506, cadena[:80], tamanio_pt=15)
            self._escribir(587, 1551, cadena[80:160] if len(cadena) > 80 else '', tamanio_pt=15)

        self._escribir(191, 1619, 'Sello Digital:', negrita=True, tamanio_pt=15)
        sello = d.get('sello_digital', '')
        if sello:
            self._escribir(587, 1642, sello[:80], tamanio_pt=15)
            self._escribir(587, 1687, sello[80:160] if len(sello) > 80 else '', tamanio_pt=15)

    def construir(self):
        self._pagina_1()
        self._pagina_2()
        return self.output()


def generar_pdf_constancia(datos):
    pdf = ConstanciaFiscalBase(datos)
    return pdf.construir()
