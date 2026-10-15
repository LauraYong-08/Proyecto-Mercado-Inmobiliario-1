import re
import csv

# Columnas en el orden solicitado
COLUMNAS = [
    "Dirección exacta",
    "Ciudad",
    "Municipio",
    "Tipo de inmueble",
    "Habitaciones",
    "Baños",
    "Pisos",
    "Balcón",
    "Patio/Terraza",
    "Amoblado",
    "Precio",
    "Fecha",
    "Contacto",
    "Gas",
    "Agua",
]

def extraer_direccion(texto):
    """Busca patrones como 'Calle X', 'Avenida Y', 'Carrera Z' seguidos de números."""
    patron = r'\b(?:Calle|Avenida|Ave|Carrera|Carretera|Pasaje|Camino)\s+[\wÁÉÍÓÚáéíóúÑñ\s]+\d+[\w\s]*'
    m = re.search(patron, texto, re.IGNORECASE)
    return m.group(0).strip() if m else ""

def extraer_ciudad(texto):
    # Busca "Ciudad" explícita o nombres conocidos como La Habana
    m = re.search(r'\bCiudad\s+([\wÁÉÍÓÚáéíóúÑñ\s]+)', texto, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    if re.search(r'\bLa Habana\b', texto, re.IGNORECASE):
        return "La Habana"
    return ""

def extraer_municipio(texto):
    # Municipios comunes de La Habana
    municipios = [
        "Centro Habana", "Habana Vieja", "Cerro", "Diez de Octubre",
        "Playa", "Marianao", "La Lisa", "Boyeros", "Arroyo Naranjo",
        "Cotorro", "San Miguel del Padrón", "Guanabacoa", "Regla",
        "Habana del Este", "Plaza de la Revolución", "Vedado",
    ]
    for mun in municipios:
        if re.search(r'\b' + re.escape(mun) + r'\b', texto, re.IGNORECASE):
            return mun
    # A veces se menciona "municipio X"
    m = re.search(r'\bmunicipio\s+([\wÁÉÍÓÚáéíóúÑñ\s]+)', texto, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""

def extraer_tipo(texto):
    if re.search(r'\bapartamento\b|\bapto\b', texto, re.IGNORECASE):
        return "Apartamento"
    if re.search(r'\bcasa\b', texto, re.IGNORECASE):
        return "Casa"
    if re.search(r'\blocal\b', texto, re.IGNORECASE):
        return "Local"
    return ""

def extraer_habitaciones(texto):
    m = re.search(r'(\d+)\s*(?:cuarto|cuartos|habitaci[oó]n|habitaciones|hab\b)', texto, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'(\d+)\s*cuarto', texto, re.IGNORECASE)
    return m.group(1) if m else ""

def extraer_banos(texto):
    m = re.search(r'(\d+)\s*ba[ñn]o', texto, re.IGNORECASE)
    return m.group(1) if m else ""

def extraer_pisos(texto):
    m = re.search(r'(\d+)\s*piso', texto, re.IGNORECASE)
    return m.group(1) if m else ""

def extraer_balcon(texto):
    if re.search(r'\bbalconcito\b|\bbalc[oó]n\b', texto, re.IGNORECASE):
        return "Sí"
    return "No"

def extraer_patio_terraza(texto):
    if re.search(r'\bpatio\b|\bterraza\b|\bbarbacoa\b', texto, re.IGNORECASE):
        return "Sí"
    return "No"

def extraer_amoblado(texto):
    if re.search(r'amueblad|se deja con|llega y vivir|con todo lo q lleva|juego living|aire acondicionado|telefono fijo|tel[eé]fono fijo|cocina de gas', texto, re.IGNORECASE):
        return "Sí"
    return "No"

def extraer_precio(texto):
    m = re.search(r'(\d[\d,\.]*)\s*(?:usd|USD)', texto, re.IGNORECASE)
    if m:
        return m.group(1).replace(",", "").replace(".", "")
    return ""

def extraer_fecha(texto):
    # Formatos: dd/mm/aaaa, dd-mm-aaaa, "12 de mayo de 2024", etc.
    patrones = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+\d{2,4}\b',
    ]
    for p in patrones:
        m = re.search(p, texto, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""

def extraer_contacto(linea_whatsapp):
    # La línea de WhatsApp puede traer teléfonos y/o enlaces
    telefonos = re.findall(r'\d{8,}', linea_whatsapp)
    if telefonos:
        return ", ".join(telefonos)
    # Si no hay números, devolver el texto limpio
    return re.sub(r'(?i)whats?app', '', linea_whatsapp).strip(" :,-")

def extraer_gas(texto):
    if re.search(r'gas de la calle', texto, re.IGNORECASE):
        return "Gas de la calle"
    if re.search(r'\bgas\b', texto, re.IGNORECASE):
        return "Sí"
    return "No"

def extraer_agua(texto):
    if re.search(r'un dia si y otro no', texto, re.IGNORECASE):
        return "Un día sí y otro no"
    if re.search(r'no hay problemas con el agua', texto, re.IGNORECASE):
        return "Sin problemas"
    if re.search(r'\bagua\b', texto, re.IGNORECASE):
        return "Sí"
    return "No"

def parsear_anuncio(bloque):
    texto = "\n".join(bloque).strip()
    # Última línea = WhatsApp, penúltima = ubicación
    linea_whatsapp = bloque[-1]
    linea_ubicacion = bloque[-2] if len(bloque) >= 2 else ""

    # Combinar ubicación con el resto para búsquedas
    texto_completo = texto

    registro = {
        "Dirección exacta": extraer_direccion(texto_completo),
        "Ciudad": extraer_ciudad(texto_completo) or extraer_ciudad(linea_ubicacion),
        "Municipio": extraer_municipio(texto_completo) or extraer_municipio(linea_ubicacion),
        "Tipo de inmueble": extraer_tipo(texto_completo),
        "Habitaciones": extraer_habitaciones(texto_completo),
        "Baños": extraer_banos(texto_completo),
        "Pisos": extraer_pisos(texto_completo),
        "Balcón": extraer_balcon(texto_completo),
        "Patio/Terraza": extraer_patio_terraza(texto_completo),
        "Amoblado": extraer_amoblado(texto_completo),
        "Precio": extraer_precio(texto_completo),
        "Fecha": extraer_fecha(texto_completo),
        "Contacto": extraer_contacto(linea_whatsapp),
        "Gas": extraer_gas(texto_completo),
        "Agua": extraer_agua(texto_completo),
    }
    return registro

def main():
    with open("datos_crudos.txt", "r", encoding="utf-8") as f:
        lineas = f.readlines()

    anuncios = []
    bloque_actual = []

    for linea in lineas:
        linea_limpia = linea.rstrip("\n")
        bloque_actual.append(linea_limpia)
        # Detectamos fin de anuncio: línea que contiene "WhatsApp" (case-insensitive)
        if re.search(r'whats?app', linea_limpia, re.IGNORECASE):
            anuncios.append(bloque_actual)
            bloque_actual = []

    # Si quedó algo pendiente (sin WhatsApp), lo ignoramos o lo añadimos
    # En este caso lo ignoramos porque el enunciado dice que cada anuncio termina con WhatsApp

    registros = [parsear_anuncio(a) for a in anuncios if len(a) >= 2]

    with open("propiedades_limpias.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNAS)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Se procesaron {len(registros)} anuncios. Archivo 'propiedades_limpias.csv' generado.")

if __name__ == "__main__":
    main()