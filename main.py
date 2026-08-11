import hashlib
import base64
import random
import string
from datetime import datetime

# ============================================================
# CONFIGURACIÓN Y DATOS BASE
# ============================================================

ENTIDADES = {
    'AGUASCALIENTES': 'AS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BS',
    'CAMPECHE': 'CC', 'CHIAPAS': 'CS', 'CHIHUAHUA': 'CH', 'COAHUILA': 'CL',
    'COLIMA': 'CM', 'CIUDAD DE MEXICO': 'DF', 'CDMX': 'DF', 'DURANGO': 'DG',
    'GUANAJUATO': 'GT', 'GUERRERO': 'GR', 'HIDALGO': 'HG', 'JALISCO': 'JC',
    'MEXICO': 'MC', 'ESTADO DE MEXICO': 'MC', 'MICHOACAN': 'MN',
    'MORELOS': 'MS', 'NAYARIT': 'NT', 'NUEVO LEON': 'NL', 'OAXACA': 'OC',
    'PUEBLA': 'PL', 'QUERETARO': 'QT', 'QUINTANA ROO': 'QR',
    'SAN LUIS POTOSI': 'SP', 'SINALOA': 'SL', 'SONORA': 'SR', 'TABASCO': 'TC',
    'TAMAULIPAS': 'TS', 'TLAXCALA': 'TL', 'VERACRUZ': 'VZ', 'YUCATAN': 'YN',
    'ZACATECAS': 'ZS', 'NACIDO EN EL EXTRANJERO': 'NE'
}

HOMOCLAVE_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÑ'

PALABRAS_INVALIDAS = [
    'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'CAKO',
    'COGE', 'COJA', 'COJE', 'COJI', 'COJO', 'CULO', 'FETO', 'GUEY',
    'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA',
    'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MION', 'MOCO', 'MULA',
    'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO', 'QULO', 'RATA', 'RUIN'
]

DOMICILIOS_POR_ESTADO = {
    'AGUASCALIENTES': {
        'colonias': ['Centro', 'Jardines', 'Las Américas', 'Ojocaliente', 'San Marcos'],
        'calles': ['Av. Independencia', 'Calle Madero', 'Av. Universidad', 'Calle Morelos'],
        'cp': ['20000', '20010', '20020', '20030', '20040']
    },
    'BAJA CALIFORNIA': {
        'colonias': ['Zona Centro', 'Playas de Tijuana', 'Otay', 'La Mesa', 'Cacho'],
        'calles': ['Av. Revolución', 'Blvd. Agua Caliente', 'Calle 5ta', 'Av. Constitución'],
        'cp': ['22000', '22010', '22020', '22100', '22200']
    },
    'BAJA CALIFORNIA SUR': {
        'colonias': ['Centro', 'El Esterito', 'La Paz', 'Santa Fe', 'Pueblo Nuevo'],
        'calles': ['Av. Forjadores', 'Calle Márquez de León', 'Blvd. Pino Payas', 'Av. Isabel la Católica'],
        'cp': ['23000', '23010', '23020', '23050', '23100']
    },
    'CAMPECHE': {
        'colonias': ['Centro Histórico', 'San Román', 'Santa Ana', 'Barrio de la Cruz', 'Villa Universidad'],
        'calles': ['Av. 16 de Septiembre', 'Calle 10', 'Calle 59', 'Av. Gobernadores'],
        'cp': ['24000', '24010', '24020', '24030', '24040']
    },
    'CHIAPAS': {
        'colonias': ['Centro', 'Las Arboledas', 'Terán', 'La Pimienta', 'Jardines del Pedregal'],
        'calles': ['Av. Central', 'Calle 5 de Mayo', 'Blvd. Belisario Domínguez', 'Calle Real'],
        'cp': ['29000', '29010', '29020', '29030', '29045']
    },
    'CHIHUAHUA': {
        'colonias': ['Centro', 'Campestre', 'San Felipe', 'La Sierra', 'Las Granjas'],
        'calles': ['Av. Tecnológico', 'Calle Victoria', 'Blvd. Ortiz Mena', 'Av. Homero'],
        'cp': ['31000', '31010', '31020', '31100', '31200']
    },
    'COAHUILA': {
        'colonias': ['Centro', 'Republica', 'Los Pinos', 'Valle Verde', 'Nueva California'],
        'calles': ['Blvd. Venustiano Carranza', 'Calle Hidalgo', 'Av. Universidad', 'Calle Juárez'],
        'cp': ['25000', '25010', '25020', '25100', '25200']
    },
    'COLIMA': {
        'colonias': ['Centro', 'Jardines de la Corregidora', 'Real de Caná', 'Los Pinos', 'San Pablo'],
        'calles': ['Av. Felipe Sevilla del Río', 'Calle Morelos', 'Blvd. Camino Real', 'Av. Venustiano Carranza'],
        'cp': ['28000', '28010', '28020', '28030', '28100']
    },
    'CIUDAD DE MEXICO': {
        'colonias': ['Centro Histórico', 'Condesa', 'Roma Norte', 'Polanco', 'Coyoacán', 'Del Valle', 'Santa María la Ribera'],
        'calles': ['Av. Paseo de la Reforma', 'Av. Insurgentes', 'Calle Madero', 'Eje Central Lázaro Cárdenas', 'Av. Patriotismo'],
        'cp': ['06000', '06100', '06140', '06600', '06700', '11550', '03100']
    },
    'DURANGO': {
        'colonias': ['Centro', 'Jardines de Durango', 'Las Flores', 'Lomas del Parque', 'Valle Verde'],
        'calles': ['Av. 20 de Noviembre', 'Calle Constitución', 'Blvd. Dolores del Río', 'Av. Heroico Colegio Militar'],
        'cp': ['34000', '34010', '34020', '34100', '34200']
    },
    'GUANAJUATO': {
        'colonias': ['Centro', 'San Javier', 'Las Palmas', 'León Moderno', 'San Juan Bosco'],
        'calles': ['Blvd. Torres Landa', 'Calle Miguel Alemán', 'Av. Guanajuato', 'Blvd. Aeropuerto'],
        'cp': ['37000', '37010', '37020', '37100', '37200']
    },
    'GUERRERO': {
        'colonias': ['Centro', 'La Laja', 'Magallanes', 'Las Playas', 'Jardín'],
        'calles': ['Av. Costera Miguel Alemán', 'Calle Cuauhtémoc', 'Blvd. Vicente Guerrero', 'Av. Universidad'],
        'cp': ['39000', '39010', '39020', '39100', '39200']
    },
    'HIDALGO': {
        'colonias': ['Centro', 'La Loma', 'Los Cedros', 'Santa Julia', 'Unidad Habitacional Militar'],
        'calles': ['Blvd. Felipe Ángeles', 'Calle Hidalgo', 'Av. Juárez', 'Blvd. Luis Donaldo Colosio'],
        'cp': ['42000', '42010', '42020', '42100', '42200']
    },
    'JALISCO': {
        'colonias': ['Centro', 'Providencia', 'Americana', 'Chapalita', 'Jardines del Bosque', 'La Estancia'],
        'calles': ['Av. Vallarta', 'Av. López Mateos', 'Calle Morelos', 'Av. Patria', 'Blvd. Puerta de Hierro'],
        'cp': ['44100', '44110', '44120', '44200', '44500', '44600']
    },
    'MEXICO': {
        'colonias': ['Centro', 'La Alborada', 'Las Flores', 'Los Reyes', 'Santa Cruz', 'Valle Verde'],
        'calles': ['Av. Central', 'Calle Hidalgo', 'Blvd. de los Continentes', 'Av. Primero de Mayo'],
        'cp': ['50000', '50010', '50020', '50100', '50200', '52000']
    },
    'MICHOACAN': {
        'colonias': ['Centro', 'Las Delicias', 'Chapultepec', 'La Quinta', 'Los Pinos'],
        'calles': ['Av. Morelos Norte', 'Calle Miguel Hidalgo', 'Blvd. García de León', 'Av. Solidaridad'],
        'cp': ['58000', '58010', '58020', '58100', '58200']
    },
    'MORELOS': {
        'colonias': ['Centro', 'Las Palmas', 'Vista Hermosa', 'Lomas de Cortés', 'Jacarandas'],
        'calles': ['Av. Cuauhtémoc', 'Calle Guerrero', 'Blvd. Benito Juárez', 'Av. Universidad'],
        'cp': ['62000', '62010', '62020', '62100', '62200']
    },
    'NAYARIT': {
        'colonias': ['Centro', 'San José', 'Las Vegas', 'Los Pinos', 'La Aurora'],
        'calles': ['Av. México', 'Calle Hidalgo', 'Blvd. Luis Donaldo Colosio', 'Av. Solidaridad'],
        'cp': ['63000', '63010', '63020', '63100', '63200']
    },
    'NUEVO LEON': {
        'colonias': ['Centro', 'San Pedro', 'Valle Oriente', 'Contry', 'Cumbres', 'San Nicolás'],
        'calles': ['Av. Constitución', 'Av. Gonzalitos', 'Blvd. Díaz Ordaz', 'Calle Morelos', 'Av. Fundadores'],
        'cp': ['64000', '64100', '64200', '64300', '64400', '64500']
    },
    'OAXACA': {
        'colonias': ['Centro', 'Jalatlaco', 'Reforma', 'San Felipe del Agua', 'Guadalupe Victoria'],
        'calles': ['Av. Independencia', 'Calle de los Derechos Humanos', 'Blvd. Eduardo Vasconcelos', 'Av. Juárez'],
        'cp': ['68000', '68010', '68020', '68100', '68200']
    },
    'PUEBLA': {
        'colonias': ['Centro', 'Angelópolis', 'La Paz', 'Las Lajas', 'San Manuel', 'Zavaleta'],
        'calles': ['Av. Reforma', 'Blvd. 5 de Mayo', 'Calle 16 de Septiembre', 'Av. Juárez'],
        'cp': ['72000', '72100', '72200', '72300', '72400', '72500']
    },
    'QUERETARO': {
        'colonias': ['Centro', 'Juriquilla', 'Jardines de la Hacienda', 'Loma Dorada', 'El Refugio'],
        'calles': ['Av. 5 de Febrero', 'Blvd. Bernardo Quintana', 'Calle Madero', 'Av. Constituyentes'],
        'cp': ['76000', '76100', '76200', '76300', '76400']
    },
    'QUINTANA ROO': {
        'colonias': ['Centro', 'Zona Hotelera', 'Bonfil', 'Supermanzana 50', 'Villas del Mar'],
        'calles': ['Blvd. Kukulcán', 'Av. Tulum', 'Calle Playa del Carmen', 'Av. Cobá'],
        'cp': ['77000', '77100', '77200', '77300', '77500', '77710']
    },
    'SAN LUIS POTOSI': {
        'colonias': ['Centro', 'Lomas', 'Morales', 'Jardín', 'Valle Verde'],
        'calles': ['Av. Carranza', 'Av. Salvador Nava', 'Calle Mariano Otero', 'Blvd. Río Santiago'],
        'cp': ['78000', '78100', '78200', '78300', '78400']
    },
    'SINALOA': {
        'colonias': ['Centro', 'Las Quintas', 'Guadalupe', 'Chapultepec', 'Villa Universidad'],
        'calles': ['Av. Obregón', 'Blvd. Diego Valadés', 'Calle Colón', 'Av. Ejército Mexicano'],
        'cp': ['80000', '80100', '80200', '80300', '80400']
    },
    'SONORA': {
        'colonias': ['Centro', 'San Benito', 'Las Lomas', 'Villa Verde', 'Los Arroyos'],
        'calles': ['Blvd. Solidaridad', 'Av. Miguel Alemán', 'Calle Guerrero', 'Av. Navarrete'],
        'cp': ['83000', '83100', '83200', '83300', '83400']
    },
    'TABASCO': {
        'colonias': ['Centro', 'La Herradura', 'Atasta', 'Las Rosas', 'Gaviotas'],
        'calles': ['Av. Paseo de la Sierra', 'Calle Independencia', 'Av. Universidad', 'Blvd. Ruiz Cortines'],
        'cp': ['86000', '86100', '86200', '86300', '86400']
    },
    'TAMAULIPAS': {
        'colonias': ['Centro', 'La Herradura', 'Villa de las Flores', 'Campestre', 'San Francisco'],
        'calles': ['Av. Hidalgo', 'Blvd. Adolfo López Mateos', 'Calle Juárez', 'Av. Universidad'],
        'cp': ['87000', '87100', '87200', '87300', '87400']
    },
    'TLAXCALA': {
        'colonias': ['Centro', 'La Trinidad', 'Santa Ana', 'Ocotlán', 'San Sebastián'],
        'calles': ['Av. Independencia', 'Calle Morelos', 'Blvd. Guillermo Valle', 'Av. Universidad'],
        'cp': ['90000', '90100', '90200', '90300', '90400']
    },
    'VERACRUZ': {
        'colonias': ['Centro', 'Reforma', 'Floresta', 'Costa Verde', 'Virginia'],
        'calles': ['Av. Díaz Mirón', 'Blvd. Ávila Camacho', 'Calle Madero', 'Av. Juan Pablo II'],
        'cp': ['91000', '91100', '91200', '91300', '91400', '91700']
    },
    'YUCATAN': {
        'colonias': ['Centro', 'Altabrisa', 'Vista Alegre', 'Paseo de las Fuentes', 'Jardines de Mérida'],
        'calles': ['Av. Colón', 'Calle 60', 'Blvd. García Lavín', 'Av. Itzáes'],
        'cp': ['97000', '97100', '97200', '97300', '97400']
    },
    'ZACATECAS': {
        'colonias': ['Centro', 'La Bufa', 'Jardines del Sol', 'Lomas de la Pimienta', 'Villas del Sol'],
        'calles': ['Av. Hidalgo', 'Calle Tacuba', 'Blvd. López Mateos', 'Av. Universidad'],
        'cp': ['98000', '98100', '98200', '98300', '98400']
    }
}

REGIMENES = [
    'Sueldos y Salarios e Ingresos Asimilados a Salarios',
    'Actividades Empresariales y Profesionales',
    'Arrendamiento de Inmuebles',
    'Régimen de Incorporación Fiscal',
    'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras',
    'Régimen Simplificado de Confianza (RESICO)',
    'Sin obligaciones fiscales',
]


def limpiar_texto(texto):
    texto = texto.upper().strip()
    reemplazos = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'Ü': 'U', 'ñ': 'Ñ', 'Ñ': 'Ñ'
    }
    for acento, sin_acento in reemplazos.items():
        texto = texto.replace(acento, sin_acento)
    texto = ''.join(c for c in texto if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZÑ ')
    return texto


def generar_domicilio(estado):
    estado_key = estado.upper()
    if estado_key not in DOMICILIOS_POR_ESTADO:
        estado_key = 'CIUDAD DE MEXICO'

    datos = DOMICILIOS_POR_ESTADO[estado_key]

    calle = random.choice(datos['calles'])
    numero_exterior = random.randint(100, 9999)
    numero_interior = random.choice(['', '', '', '', f'Int. {random.randint(1, 50)}'])
    colonia = random.choice(datos['colonias'])
    cp = random.choice(datos['cp'])

    direccion = f"{calle} {numero_exterior}"
    if numero_interior:
        direccion += f" {numero_interior}"
    direccion += f", Col. {colonia}, CP {cp}"

    return {
        'calle': calle,
        'numero_exterior': str(numero_exterior),
        'numero_interior': numero_interior.replace('Int. ', '') if numero_interior else '',
        'colonia': colonia,
        'codigo_postal': cp,
        'localidad': '',
        'municipio': '',
        'estado': estado,
        'direccion_completa': direccion
    }


def generar_curp(nombre_completo, fecha_nac, estado, sexo='H'):
    partes = limpiar_texto(nombre_completo).split()

    if len(partes) < 3:
        apellido1 = partes[0] if len(partes) > 0 else 'X'
        apellido2 = partes[1] if len(partes) > 1 else 'X'
        nombres = ' '.join(partes[2:]) if len(partes) > 2 else 'X'
    else:
        apellido1 = partes[0]
        apellido2 = partes[1]
        nombres = ' '.join(partes[2:])

    for prep in ['DE', 'DEL', 'LA', 'LAS', 'LOS', 'MC', 'MAC', 'VON', 'VAN']:
        if apellido1 == prep and len(partes) > 1:
            apellido1 = partes[1]
            apellido2 = partes[2] if len(partes) > 2 else ''
            nombres = ' '.join(partes[3:]) if len(partes) > 3 else ''

    primer_nombre = nombres.split()[0] if nombres else ''
    if primer_nombre in ['MARIA', 'MA.', 'JOSE', 'J.']:
        nombres_split = nombres.split()
        primer_nombre = nombres_split[1] if len(nombres_split) > 1 else nombres_split[0]

    curp = apellido1[0] if apellido1 else 'X'

    vocales_ap1 = [c for c in apellido1[1:] if c in 'AEIOU']
    curp += vocales_ap1[0] if vocales_ap1 else 'X'

    curp += apellido2[0] if apellido2 else 'X'
    curp += primer_nombre[0] if primer_nombre else 'X'

    curp += fecha_nac.strftime('%y%m%d')
    curp += sexo.upper()

    entidad_clave = ENTIDADES.get(estado.upper(), 'NE')
    curp += entidad_clave

    def consonantes_internas(palabra):
        return [c for c in palabra[1:] if c not in 'AEIOU']

    cons = (consonantes_internas(apellido1) +
            consonantes_internas(apellido2) +
            consonantes_internas(primer_nombre))
    curp += ''.join(cons[:2]).ljust(2, 'X')

    digito = (sum(ord(c) * (i + 1) for i, c in enumerate(curp)) % 10)
    curp += str(digito)

    return curp


def generar_rfc(nombre_completo, fecha_nac):
    partes = limpiar_texto(nombre_completo).split()
    apellido1 = partes[0] if len(partes) > 0 else 'X'
    apellido2 = partes[1] if len(partes) > 1 else 'X'
    nombres = ' '.join(partes[2:]) if len(partes) > 2 else 'X'

    rfc = apellido1[:2].ljust(2, 'X')
    rfc += apellido2[0] if apellido2 else 'X'
    rfc += nombres[0] if nombres else 'X'

    rfc += fecha_nac.strftime('%y%m%d')

    hash_nombre = hashlib.md5(nombre_completo.encode()).hexdigest()[:3]
    homoclave = ''
    for c in hash_nombre:
        idx = int(c, 16) % len(HOMOCLAVE_CHARS)
        homoclave += HOMOCLAVE_CHARS[idx]

    rfc += homoclave

    for palabra in PALABRAS_INVALIDAS:
        if rfc[:4] == palabra:
            rfc = rfc[:3] + 'X' + rfc[4:]

    return rfc


def generar_idcif():
    return ''.join(random.choices(string.digits, k=11))


def generar_regimen():
    return random.choice(REGIMENES)


def generar_cadena_digital(rfc, nombre, fecha_nac, idcif):
    fecha_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    cadena = (
        f"||{fecha_str}|"
        f"SAT|"
        f"ConstanciaSituacionFiscal|"
        f"{rfc}|"
        f"{nombre.upper()}|"
        f"{fecha_nac.strftime('%Y-%m-%d')}|"
        f"{idcif}|"
        f"Mexico||"
    )
    return cadena


def generar_sello_digital(cadena_original):
    sha = hashlib.sha256(cadena_original.encode('utf-8')).digest()
    sello = base64.b64encode(sha).decode('utf-8')
    return sello


def generar_datos_completos(nombre_completo, fecha_nacimiento_str, estado, sexo='H'):
    fecha_nac = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d')

    curp = generar_curp(nombre_completo, fecha_nac, estado, sexo)
    rfc = generar_rfc(nombre_completo, fecha_nac)
    idcif = generar_idcif()
    regimen = generar_regimen()
    domicilio = generar_domicilio(estado)
    cadena_digital = generar_cadena_digital(rfc, nombre_completo, fecha_nac, idcif)
    sello_digital = generar_sello_digital(cadena_digital)

    url_qr = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    fecha_emision = datetime.now().strftime('%Y-%m-%d')

    datos = {
        'nombre': nombre_completo.upper(),
        'fecha_nacimiento': fecha_nac.strftime('%d/%m/%Y'),
        'fecha_nacimiento_iso': fecha_nacimiento_str,
        'estado': estado,
        'sexo': 'HOMBRE' if sexo == 'H' else 'MUJER',
        'curp': curp,
        'rfc': rfc,
        'idcif': idcif,
        'regimen_fiscal': regimen,
        'domicilio': domicilio,
        'codigo_postal': domicilio['codigo_postal'],
        'cadena_digital': cadena_digital,
        'sello_digital': sello_digital,
        'url_qr': url_qr,
        'fecha_emision': fecha_emision,
        'vigencia': 'Indefinida (según disposiciones fiscales)'
    }

    return datos
