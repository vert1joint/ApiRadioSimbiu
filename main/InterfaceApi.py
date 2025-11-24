import requests
from datetime import date, datetime
import mysql.connector
from mysql.connector import Error
import paramiko
import time
import os
import json
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import threading
import sys
import logging
import logging.handlers
from mutagen import File

# excepción personalizada para detener el proceso
class ProcesoDetenido(Exception):
    pass

# variable global para controlar la detención
detener_proceso = False

serverDbPrueba = "192.168.168.181"
userDbPrueba = "nexnews"
passDbPrueba = "132lokas1"

nameDbPrueba = "nexnews"
portDbPrueba = "3306"

# token se carga desde token_simbiu.txt
token = ""

# Colores ANSI
COLOR_CLAVE = "\033[94m"   # Azul
COLOR_VALOR = "\033[92m"   # Verde
RESET = "\033[0m"          # Reset color

# Definir variables con rutas relativas basadas en la ubicacion del python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "log")
EXPORT_DIR = os.path.join(BASE_DIR, "img")
TOKEN_FILE = os.path.join(BASE_DIR, "token_simbiu.txt")

# crear directorios si no existen
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

carpetaImgs = 'C:/Pega/Simbiu/img/'
servidor_ftp = '192.168.168.169'
usuario = 'root'
contraseña = 'N3w$.GOj169'
ruta_remota = '/Simbiu/'

# ========================================
# FUNCIÓN DE LOGGING
# ========================================
def GeneraLog(sistema, nivel, mensaje):
    """genera logs rotativos por día con información del proceso"""
    logger = logging.getLogger(sistema)
    logger.setLevel(logging.DEBUG)
    
    nombreFicheroLog = datetime.now().strftime('%d_%m_%Y')
    # limpiar nombre de sistema para usar en archivo (quitar espacios y caracteres especiales)
    sistema_limpio = sistema.replace(' ', '').replace('-', '')
    handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, f"{nombreFicheroLog}_{sistema_limpio}.log"), 
        mode="a", 
        maxBytes=0, 
        backupCount=1
    )
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%y %H:%M:%S"
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if nivel == 1:
        logger.debug(mensaje)
    elif nivel == 2:
        logger.info(mensaje)
    elif nivel == 3:
        logger.warning(mensaje)
    elif nivel == 4:
        logger.error(mensaje)
    else:
        logger.critical(mensaje)
    
    logger.removeHandler(handler)

# ========================================
# FUNCIONES DE VALIDACIÓN Y RENOVACIÓN DE TOKEN
# ========================================
def cargar_token_desde_archivo():
    """carga el token desde archivo si existe"""
    global token
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token_leido = f.read().strip()
                if token_leido:
                    token = token_leido
                    print(f"✅ Token cargado desde archivo")
                    return True
    except Exception as e:
        print(f"⚠️ Error al cargar token desde archivo: {e}")
    return False

def validar_token():
    """carga el token desde el archivo token_simbiu.txt sin validación"""
    global token
    
    print("\n" + "="*80)
    print("🔐 CARGANDO TOKEN DESDE ARCHIVO")
    print("="*80)
    
    # cargar token desde archivo
    if cargar_token_desde_archivo():
        print("✅ Token cargado correctamente")
        print("="*80 + "\n")
        return True
    else:
        print("⚠️ No se pudo cargar token desde archivo, usando token por defecto")
        print("="*80 + "\n")
        return True  # continuar de todas formas con el token global

# ========================================
# CONFIGURACIÓN DE RADIOS Y PROGRAMAS
# estructura mantenible para agregar nuevas radios y programas
# ========================================
radios_programas = {
    '3147': {  # MediaId de Litoral: Radio Bio-Bio Santiago
        'nombre_radio': 'Radio Bio-Bio',
        'id_medio_nex': '171',
        'tipo': '8',
        'programas': {
            '6492': {
                'id_interno': '3170',
                'nombre_interno': 'Radiograma Matinal',
                'nombre_simbiu': 'Radiograma Matinal',
                'horario': '06:00'
            },
            '4932': {
                'id_interno': '3170',
                'nombre_interno': 'Radiograma Matinal',
                'nombre_simbiu': 'Radiograma Matinal',
                'horario': '06:00'
            },
            '1954': {  
                'id_interno': '3663',
                'nombre_interno': 'Radiograma Mediodía',
                'nombre_simbiu': 'Radiograma Mediodía',
                'horario': '13:00'
            },
            '2315': {
                'id_interno': '3175',
                'nombre_interno': 'Radiograma Vespertino',
                'nombre_simbiu': 'Radiograma Vespertino',
                'horario': '18:00'
            },
            '1999': {  
                'id_interno': '3172',
                'nombre_interno': 'Expreso Biobío',
                'nombre_simbiu': 'Expreso Bio Bio',
                'horario': '10:30'
            },
            '2000': {  
                'id_interno': '5485',
                'nombre_interno': 'Expreso PM',
                'nombre_simbiu': 'Expreso PM',
                'horario': '14:00'
            },
            '2001': {
                'id_interno': '3174',
                'nombre_interno': 'Podría Ser Peor',
                'nombre_simbiu': 'Podría Ser Peor',
                'horario': '16:00'
            },
            '2002': {
                'id_interno': '3176',
                'nombre_interno': 'Bio Bio Deportes',
                'nombre_simbiu': 'Bio Bio Deportes',
                'horario': '20:00'
            },
            '2003': {
                'id_interno': '8101',
                'nombre_interno': 'Hoy en la Radio',
                'nombre_simbiu': 'Hoy en la Radio',
                'horario': '21:00'
            },'2325': {
                'id_interno': '3177',
                'nombre_interno': 'Radiograma Medianoche',
                'nombre_simbiu': 'Radiograma Medianoche',
                'horario': '00:00'
            },'2323': {
                'id_interno': '8103',
                'nombre_interno': 'Una Semana en La Radio',
                'nombre_simbiu': 'Una semana en la radio',
                'horario': '09:00'
            },
            '2331': {
                'id_interno': '8105',
                'nombre_interno': 'A Tiempo y Sin Pauta',
                'nombre_simbiu': 'A tiempo y sin pauta',
                'horario': '14:00'
            },
        }
    },
    '3148': {  # MediaId de litoral: Radio Cooperativa
        'nombre_radio': 'Radio Cooperativa',
        'id_medio_nex': '172',
        'tipo': '8',
        'programas': {
            '6531': {
                'id_interno': '3178',
                'nombre_interno': 'El Diario de Cooperativa 1° Edición',
                'nombre_simbiu': 'El Diario de Cooperativa 1ª Edición',
                'horario': '06:00'
            },
            '1978': {
                'id_interno': '3179',
                'nombre_interno': 'El Primer Café',
                'nombre_simbiu': 'El Primer Café',
                'horario': '09:00'
            },
            '1982': {
                'id_interno': '3181',
                'nombre_interno': 'El Diario de Cooperativa 2° Edición',
                'nombre_simbiu': 'El Diario de Cooperativa 2ª Edición',
                'horario': '13:00'
            },
            '1985': {
                'id_interno': '3180',
                'nombre_interno': 'Cooperativa Deportes',
                'nombre_simbiu': 'Cooperativa Deportes',
                'horario': '14:00'
            },
            '1983': {
                'id_interno': '3859',
                'nombre_interno': 'Cooperativa Deportes PM',
                'nombre_simbiu': 'Cooperativa Deportes PM',
                'horario': '20:00'
            },
        }
    },
    '3146': {  # MediaId de Radio Agricultura
        'nombre_radio': 'Radio Agricultura',
        'id_medio_nex': '170',
        'tipo': '8',
        'programas': {
            '1990': {
                'id_interno': '3193',
                'nombre_interno': '1era Edición - Noticias en Agricultura',
                'nombre_simbiu': 'Noticias en Agricultura',
                'horario': '06:00'
            },
            '1986': {
                'id_interno': '6259',
                'nombre_interno': 'La Mañana de Agricultura',
                'nombre_simbiu': 'La Mañana en Agricultura',
                'horario': '08:00'
            },
            '1987': {
                'id_interno': '4245',
                'nombre_interno': 'Directo al Grano',
                'nombre_simbiu': 'Directo al Grano',
                'horario': '12:00'
            },
            '2282': {
                'id_interno': '6277',
                'nombre_interno': 'La Voz de la Gente',
                'nombre_simbiu': 'La Voz de la Gente',
                'horario': '14:00'
            },
            '1989': {
                'id_interno': '3441',
                'nombre_interno': 'Conectados con Agricultura',
                'nombre_simbiu': 'Conectados en Agricultura',
                'horario': '16:00'
            },
            '1991': {
                'id_interno': '6039',
                'nombre_interno': 'Nuevas Voces',
                'nombre_simbiu': 'Nuevas Voces',
                'horario': '18:00'
            },
            '2237': {
                'id_interno': '3252',
                'nombre_interno': '1era Edición - Deportes en Agricultura',
                'nombre_simbiu': 'Deportes en Agricultura - AM',
                'horario': '07:00'
            },
            '1951': {
                'id_interno': '3200',
                'nombre_interno': 'Deportes en Agricultura Medio Día',
                'nombre_simbiu': 'Deportes en Agricultura - PM',
                'horario': '13:00'
            },
        }
    },
}

# mapeo de programIds de Simbiu a IDs internos (para compatibilidad)
mapeo_programas = {}
for media_id, radio_data in radios_programas.items():
    mapeo_programas.update(radio_data['programas'])

def obtener_programa_interno(programId_simbiu):
    """convierte el programId de Simbiu al ID interno correspondiente"""
    programId_str = str(programId_simbiu)
    if programId_str in mapeo_programas:
        return mapeo_programas[programId_str]['id_interno'], mapeo_programas[programId_str]['nombre_interno']
    return programId_str, None  # si no hay mapeo, retorna el mismo ID

def descargar_y_extraer_duracion(url, sourceTypeId=None, nombre_radio="Radio"):
    """descarga archivo temporal y extrae su duración antes del INSERT"""
    headers = {
        'Authorization': f'Bearer {token}',
        'x-version': '1'
    }
    
    print(f"📥 Descargando archivo temporal...")
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        # detectar extensión
        content_type = response.headers.get('Content-Type', '')
        if sourceTypeId == 3:
            extension = ".mp3"
        elif 'video/mp4' in content_type or url.lower().endswith('.mp4'):
            extension = ".mp4"
        else:
            extension = ".mp3"
        
        # guardar temporalmente
        temp_file = os.path.join(BASE_DIR, f"temp_audio{extension}")
        
        total_size = 0
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
        
        print(f"✅ Archivo descargado: {total_size / 1024:.2f} KB")
        
        # extraer duración del archivo completo usando mutagen
        try:
            audio = File(temp_file)
            if audio is None or not hasattr(audio, "info"):
                print(f"⚠️ No se pudo leer info de audio")
                duracion = "0min. 00seg."
            else:
                duracion_segundos = audio.info.length
                minutos = int(duracion_segundos // 60)
                segundos = int(duracion_segundos % 60)
                # formato: "3min. 01seg."
                duracion = f"{minutos}min. {segundos:02d}seg."
                print(f"⏱️ Duración detectada: {duracion} ({duracion_segundos:.2f}s)")
        except Exception as e:
            print(f"⚠️ Error al extraer duración: {e}")
            duracion = "0min. 00seg."
        
        return {
            'duracion': duracion,
            'archivo_temp': temp_file,
            'extension': extension,
            'tamaño': total_size
        }
    else:
        print(f"❌ Error al descargar: {response.status_code}")
        GeneraLog(nombre_radio, 4, f"ERROR descarga | Status: {response.status_code} | URL: {url[:100]}")
        return None

def subir_archivo_sftp(archivo_local, nombre_archivo, id_noticia, titulo, nombre_radio="Radio", fecha_noticia=None):
    """sube el archivo ya renombrado al SFTP"""
    try:
        # conexión SFTP
        transport = paramiko.Transport((servidor_ftp, 22))
        transport.connect(username=usuario, password=contraseña)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print(f"✅ Conectado al SFTP {servidor_ftp}:22")

        # obtener ruta dinámica y crear carpetas usando la fecha de la noticia
        ruta_dinamica = obtener_ruta_ftp_dinamica(fecha_noticia)
        print(f"📁 Ruta destino: {ruta_dinamica}")
        crear_carpetas_sftp(sftp, ruta_dinamica)
        
        # subir el archivo
        print(f"⬆️ Subiendo: {nombre_archivo}")
        ruta_remota_completa = ruta_dinamica.rstrip('/') + '/' + nombre_archivo
        sftp.put(archivo_local, ruta_remota_completa)
        print(f"✅ Archivo enviado correctamente")
        print(f"🌐 Ruta: {ruta_remota_completa}")
        
        # log subida exitosa
        GeneraLog(nombre_radio, 2, f"Archivo subido a SFTP | ID: {id_noticia} | Archivo: {nombre_archivo} | Destino: {ruta_remota_completa} | Título: {titulo[:100]}")
        
        # cerrar conexión
        sftp.close()
        transport.close()
        print(f"🔌 Conexión SFTP cerrada")
        
        # eliminar archivo local
        try:
            os.remove(archivo_local)
            print(f"🗑️ Archivo local eliminado: {nombre_archivo}")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo local: {e}")
            
    except Exception as e:
        print(f"❌ Error al subir archivo por SFTP:")
        print(f"   {str(e)}")
        import traceback
        print(traceback.format_exc())
        GeneraLog(nombre_radio, 4, f"ERROR SFTP | ID: {id_noticia} | Archivo: {nombre_archivo} | Error: {str(e)}")

def obtener_ruta_ftp_dinamica(fecha_noticia=None):
    """genera la ruta FTP dinámica basada en la fecha de la noticia: /storage/2025c/mes/dia/"""
    if fecha_noticia:
        # si viene como string con formato 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'
        if isinstance(fecha_noticia, str):
            fecha_str = fecha_noticia.split('T')[0] if 'T' in fecha_noticia else fecha_noticia.split(' ')[0]
            from datetime import datetime
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            fecha_obj = fecha_noticia
    else:
        fecha_obj = date.today()
    
    año = fecha_obj.year
    mes = str(fecha_obj.month).zfill(2)  # mes con 2 dígitos
    dia = str(fecha_obj.day).zfill(2)    # día con 2 dígitos
    return f'/storage/{año}c/{mes}/{dia}/'

def crear_carpetas_sftp(sftp, ruta):
    """crea las carpetas necesarias en el SFTP si no existen"""
    carpetas = ruta.strip('/').split('/')
    ruta_actual = ''
    
    for carpeta in carpetas:
        if carpeta:  # evitar carpetas vacías
            ruta_actual = ruta_actual + '/' + carpeta
            try:
                sftp.stat(ruta_actual)
                # print(f"✓ Carpeta existe: {ruta_actual}")
            except FileNotFoundError:
                try:
                    sftp.mkdir(ruta_actual)
                    print(f"📁 Carpeta creada: {ruta_actual}")
                except Exception as e:
                    print(f"⚠️ No se pudo crear carpeta {ruta_actual}: {e}")

def validarSiExiste(id):
    q = f"SELECT * FROM nex_noticia WHERE id = {id}"
    # print(q)
    res = run_queryPrueba(q)
    # print(res)
    if res == []:
        return False
    else:
        return True

def descargar_imagen(linkImg,numeroPagina,nombremed,fecha_noticia=None):
    #numeroPagina = next(iter(numeroPagina))
    nomrbreMedio = nombremed
    nomrbreMedio = nomrbreMedio.replace(" ", "")

    respuesta = requests.get(linkImg)
    
    if respuesta.status_code == 200:
        nombreimg = f'{nomrbreMedio}-{numeroPagina}.jpg'
        ruta_guardado = EXPORT_DIR + f'{nomrbreMedio}-{numeroPagina}.jpg'
        with open(ruta_guardado, 'wb') as archivo:
            archivo.write(respuesta.content)
        print("Imagen",ruta_guardado," descargada con éxito.")
        try:
            # Conexión al servidor SFTP
            transport = paramiko.Transport((servidor_ftp, 22))
            transport.connect(username=usuario, password=contraseña)
            sftp = paramiko.SFTPClient.from_transport(transport)
            print(f"✅ Conectado al SFTP")

            # obtener ruta dinámica y crear carpetas usando la fecha de la noticia
            ruta_dinamica = obtener_ruta_ftp_dinamica(fecha_noticia)
            crear_carpetas_sftp(sftp, ruta_dinamica)
            
            # subir el archivo
            ruta_remota_completa = ruta_dinamica.rstrip('/') + '/' + nombreimg
            sftp.put(ruta_guardado, ruta_remota_completa)

            print(f"✅ Imagen enviada correctamente a {ruta_remota_completa}")
        except Exception as e:
            print("Error al enviar el archivo por SFTP:", str(e))
            import traceback
            print(traceback.format_exc())
        finally:
            # Cerrar la conexión SFTP
            try:
                sftp.close()
                transport.close()
            except:
                pass
    else:
        print("Error al descargar la imagen:", respuesta.status_code)


def run_queryPrueba(query='', params=None):
    try:
        connection = mysql.connector.connect(host=serverDbPrueba,
                                             database=nameDbPrueba,
                                             user=userDbPrueba,
                                             password=passDbPrueba)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            # print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            
            # usar parámetros preparados si se proporcionan
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.upper().startswith('SELECT'):
                data = cursor.fetchall()  # Traer los resultados de un select
            else:
                connection.commit()  # Hacer efectiva la escritura de datos
                data = cursor.lastrowid
            return data
            # record = cursor.fetchone()
            # print("You're connected to database: ", record)
    except Error as e:
        print(f"Error BD: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def escapeString(valor):
    # escapar correctamente para MySQL: comillas simples se duplican
    valor = str(valor).replace("\\", "\\\\")  # primero escapar backslashes
    valor = valor.replace("'", "''")  # duplicar comillas simples
    valor = valor.replace('"', '\\"')  # escapar comillas dobles
    return valor

def crear_query(nota,idmedioreferencianex,idmedionex,nombrenex,tipo,idprogramSim,nombreprogram,transcripcion_unificada="",horario=""):
    print(f"\n{'='*80}")
    print(f"🔨 CREANDO QUERY PARA INSERT")
    print(f"{'='*80}")
    
    pieImagen = ""
    sobretitulo = ""
    bajada = ""
    ctexto = ""
    
    # procesar título: si encuentra un punto, divide ahí
    titulo_original = nota['titulo']
    titulo_final = titulo_original
    contenido_adicional = ""
    
    punto_pos = titulo_original.find('.')
    
    if punto_pos != -1 and punto_pos > 0:
        # dividir en el primer punto encontrado
        titulo_final = titulo_original[:punto_pos + 1].strip()
        contenido_adicional = titulo_original[punto_pos + 1:].strip()
        print(f"✅ Título dividido en el primer punto (posición {punto_pos})")
        print(f"   • Nuevo título ({len(titulo_final)} chars): {titulo_final[:80]}...")
        if contenido_adicional:
            print(f"   • Contenido adicional ({len(contenido_adicional)} chars): {contenido_adicional[:80]}...")
    
    # truncar a 255 caracteres para evitar errores de BD
    titulo_final = titulo_final[:255]
    
    # usar transcripción unificada en cache Y ctexto
    if transcripcion_unificada:
        transcripcion_unificadaX = transcripcion_unificada.split("|")[0]
        pieImagen = transcripcion_unificada.split("|")[1]
        cache = transcripcion_unificadaX  # transcripción completa
        ctexto = transcripcion_unificadaX  # transcripción completa también en ctexto
        print(f"✅ Transcripción guardada en cache y ctexto ({len(transcripcion_unificadaX)} caracteres)")
    else:
        cache = titulo_final
        ctexto = ""
        print(f"⚠️ No hay transcripción, usando título en cache")
    
    # el cuerpo SOLO contiene el contenido adicional del título (después del punto)
    if contenido_adicional:
        cuerpo_texto = contenido_adicional
        print(f"✅ Cuerpo establecido con contenido después del punto ({len(contenido_adicional)} caracteres)")
    else:
        cuerpo_texto = ""
        print(f"⚠️ No hay contenido después del punto, cuerpo vacío")
    
    # actualizar el título en la nota (ya truncado)
    nota['titulo'] = titulo_final
    
    noticia = 6
    nota['paginas'] = ""
    
    # validar y limpiar el autor
    autor = nota['autor']
    if autor is None or str(autor) == 'None' or str(autor).strip() == '':
        autor = ""
    
    print(f"\n📋 Datos del INSERT:")
    print(f"   • Título: {nota['titulo'][:60]}...")
    print(f"   • Medio: {nombrenex}")
    print(f"   • Fecha: {nota['fecha']}")
    print(f"   • Sección: {nota['seccion']}")
    print(f"   • Programa: {nombreprogram}")
    print(f"   • Autor: {autor if autor else '(vacío)'}")
    print(f"   • Horario: {horario if horario else '(vacío)'}")
    print(f"   • SourceTypeId: {nota.get('sourceTypeId', 'N/A')}")
    print(f"   • Cuerpo (primeros 100 chars): {str(cuerpo_texto)[:100]}...")
    print(f"   • Cache (primeros 100 chars): {str(cache)[:100]}...")
    print(f"   • URL: {nota['url'][:60]}...")
    
    # PASO 1: descargar archivo y extraer duración
    print(f"\n{'='*80}")
    print(f"PASO 1: DESCARGAR ARCHIVO Y EXTRAER DURACIÓN")
    print(f"{'='*80}")
    
    archivo_info = descargar_y_extraer_duracion(nota['url'], nota.get('sourceTypeId'), nombrenex)
    
    if not archivo_info:
        print(f"❌ No se pudo descargar el archivo, abortando operación")
        GeneraLog(nombrenex, 4, f"ERROR: No se pudo descargar archivo | Título: {nota['titulo'][:100]}")
        return
    
    duracion = archivo_info['duracion']
    archivo_temp = archivo_info['archivo_temp']
    extension = archivo_info['extension']
    tamaño = archivo_info['tamaño']
    
    print(f"✅ Archivo listo: {duracion} | {tamaño / 1024:.2f} KB")
    
    # PASO 2: hacer INSERT con la duración
    print(f"\n{'='*80}")
    print(f"PASO 2: INSERT EN BASE DE DATOS CON DURACIÓN")
    print(f"{'='*80}")
    print(f"   • Duración: {duracion}")
    
    InserQuery = "INSERT INTO nex_noticia (producto,areanot,pieimagen,ctexto,autor,bajada,sobretitulo,pagina,seccion,pais,fecha,nex_medio_id,nex_medio_referencia, nombremedio,titulo,cuerpo,empresa,hora,duracion,noticia,created_by,`cache`,urlfuente) VALUES (\"\",\"\",\"\",\""+escapeString(str(ctexto))+"\",\""+escapeString(str(autor))+"\",\""+escapeString(str(bajada))+"\",\""+escapeString(str(sobretitulo))+"\",\""+str(nota['paginas'])+"\",\""+escapeString(str(nota['seccion']))+"\",\"Chile\",\""+str(nota['fecha'])+"\","+str(idmedionex)+","+str(idmedioreferencianex)+",\""+escapeString(str(nombrenex))+"\",\""+escapeString(str(nota['titulo']))+"\",\""+escapeString(str(cuerpo_texto))+"\",\""+str(nombreprogram)+"\",\""+str(horario)+"\",\""+duracion+"\","+str(noticia)+",0,\""+escapeString(str(cache))+"\",\"\");"
    
    try:
        res = run_queryPrueba(InserQuery)
        print(f'✅ INSERT exitoso! ID generado: {res}')
        
        # log del insert exitoso
        log_insert = f"INSERT exitoso | ID: {res} | Título: {nota['titulo'][:100]} | Medio: {nombrenex} | Programa: {nombreprogram} | Fecha: {nota['fecha']} | Duración: {duracion}"
        GeneraLog(nombrenex, 2, log_insert)
        
        # PASO 2.5: INSERT en nex_transcript
        print(f"\n{'='*80}")
        print(f"PASO 2.5: INSERT EN TABLA nex_transcript")
        print(f"{'='*80}")
        
        # guardar el id de Simbiu en notasolicitud
        id_simbiu = nota.get('idSimbiu', '')
        print(f"   📌 ID Simbiu a guardar: {id_simbiu}")
        
        InsertTranscriptQuery = "INSERT INTO nex_transcript (id, texto, mencion, men_client, fecha, alturacion, notasolicitud) VALUES ("+str(res)+",\""+escapeString(str(ctexto))+"\",\"\",\"\",\""+str(nota['fecha'])+"\",\""+escapeString(str(pieImagen))+"\",\""+str(id_simbiu)+"\");"
        
        try:
            run_queryPrueba(InsertTranscriptQuery)
            print(f'✅ INSERT en nex_transcript exitoso para ID: {res}')
            print(f'   📌 notasolicitud: {id_simbiu}')
            GeneraLog(nombrenex, 2, f"INSERT nex_transcript exitoso | ID: {res} | ID Simbiu: {id_simbiu}")
        except Exception as e_transcript:
            print(f'⚠️ ERROR en INSERT nex_transcript: {str(e_transcript)}')
            GeneraLog(nombrenex, 3, f"ERROR en INSERT nex_transcript | ID: {res} | Error: {str(e_transcript)}")
        
        # PASO 3: renombrar archivo con el ID
        print(f"\n{'='*80}")
        print(f"PASO 3: RENOMBRAR ARCHIVO CON ID")
        print(f"{'='*80}")
        
        nombre_final = str(res) + extension
        archivo_final = os.path.join(BASE_DIR, nombre_final)
        
        try:
            os.rename(archivo_temp, archivo_final)
            print(f"✅ Archivo renombrado: {nombre_final}")
        except Exception as e:
            print(f"⚠️ Error al renombrar, copiando: {e}")
            import shutil
            shutil.copy2(archivo_temp, archivo_final)
            os.remove(archivo_temp)
        
        # PASO 4: subir al SFTP
        print(f"\n{'='*80}")
        print(f"PASO 4: SUBIR ARCHIVO AL SFTP")
        print(f"{'='*80}")
        
        subir_archivo_sftp(archivo_final, nombre_final, res, nota['titulo'], nombrenex, nota['fecha'])
        
        print(f"\n{'='*80}")
        print(f"✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f'❌ ERROR en INSERT o procesamiento:')
        print(f'   {str(e)}')
        print(f"{'='*80}\n")
        GeneraLog(nombrenex, 4, f"ERROR en INSERT o procesamiento: {str(e)}")
        
        # limpiar archivo temporal si hay error
        try:
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)
                print(f"🗑️ Archivo temporal eliminado por error")
        except:
            pass

def consultarApi(idMedio,lastId,idmedioreferencianex,idmedionex,nombre,tipo,idprogramSim,nombreprogram,fecha_consulta=None,horario=""):
    # usar fecha proporcionada o fecha actual
    if fecha_consulta:
        fecha_actual = fecha_consulta
    else:
        fecha_actual = date.today().strftime("%Y-%m-%d")
    
    # log inicio consulta API
    GeneraLog(nombre, 2, f"Consultando API | Fecha: {fecha_actual} | Radio: {nombre} | Programa: {nombreprogram} | ID Medio: {idMedio}")
    
    queryvalidCargado = "SELECT * FROM nex_noticia WHERE fecha = '"+str(fecha_actual)+"' AND nex_medio_id = "+str(idmedionex)
    resultvalid = run_queryPrueba(queryvalidCargado)
    print(f'✅ Noticias ya cargadas hoy: {len(resultvalid)}')
    
    # comentado para permitir reprocesamiento
    # if len(resultvalid)==0:
    if True:  # siempre procesar
        #fecha_actual = '2024-05-12'
        url = f'https://api.simbiu.es/api/MediaRecords/News?Page=1&RecordsByPage=100&DateIni={fecha_actual}&DateEnd={fecha_actual}&MediasIds=[{idMedio}]&PaisId=CL'
        print(url)
        # Encabezados que deseamos enviar con la solicitud GET
        headers = {
            'Authorization': f'Bearer {token}',
            'x-version': 'production'
        }

        response = requests.get(url, headers=headers)
        # Verificar si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            print('Solicitud exitosa!')
            data = response.json()
            total_noticias = len(data.get('news', []))
            GeneraLog(nombre, 2, f"API respuesta exitosa | Total noticias: {total_noticias} | Programa: {nombreprogram}")
            # print('data',data)
            lastId = procesarResultados(data,idmedioreferencianex,idmedionex,nombre,tipo,idprogramSim,nombreprogram,horario)
        elif response.status_code == 401:
            print('Error al hacer la solicitud:', response.status_code)
            print(response.headers)
            print('⚠️ Token expirado, renovando...')
            GeneraLog(nombre, 3, f"Token expirado | Renovando token | Programa: {nombreprogram}")
            
            # intentar renovar token
            if renovar_token():
                print('✅ Token renovado, reintentando consulta...')
                # reintentar la consulta con el nuevo token
                headers['Authorization'] = f'Bearer {token}'
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    print('✅ Solicitud exitosa después de renovar token!')
                    data = response.json()
                    total_noticias = len(data.get('news', []))
                    GeneraLog(nombre, 2, f"API respuesta exitosa (post-renovación) | Total noticias: {total_noticias} | Programa: {nombreprogram}")
                    lastId = procesarResultados(data,idmedioreferencianex,idmedionex,nombre,tipo,idprogramSim,nombreprogram,horario)
                else:
                    print(f'❌ Error después de renovar token: {response.status_code}')
                    GeneraLog(nombre, 4, f"ERROR API después de renovar token | Status Code: {response.status_code} | Programa: {nombreprogram}")
                    lastId = None
            else:
                print('❌ No se pudo renovar el token')
                GeneraLog(nombre, 4, f"ERROR: No se pudo renovar token | Programa: {nombreprogram}")
                lastId = None
        else:
            #print(response.headers)
            print('Error al hacer la solicitud:', response.status_code)
            print(response.headers)
            GeneraLog(nombre, 4, f"ERROR API | Status Code: {response.status_code} | Programa: {nombreprogram}")
            lastId = None

        return lastId
    # else:
    #     print("medio cargado "+str(nombre))
    #     return None

def imprimir_diccionario(d, nivel=0):
    COLOR_CLAVE = "\033[94m"
    COLOR_VALOR = "\033[92m"
    COLOR_DICT = "\033[93m"
    COLOR_LIST = "\033[95m"
    RESET = "\033[0m"

    indent = "  " * nivel

    if isinstance(d, dict):
        for k, v in d.items():
            print(f"{indent}{COLOR_CLAVE}{k}{RESET}:", end=" ")
            if isinstance(v, dict):
                print(f"{COLOR_DICT}(diccionario){RESET}")
                imprimir_diccionario(v, nivel + 1)
            elif isinstance(v, list):
                print(f"{COLOR_LIST}[lista con {len(v)} elementos]{RESET}")
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        print(f"{indent}  {COLOR_LIST}[{i}]{RESET}")
                        imprimir_diccionario(item, nivel + 2)
                    elif isinstance(item, list):
                        print(f"{indent}  {COLOR_LIST}[{i}]{RESET}")
                        imprimir_diccionario(item, nivel + 2)
                    else:
                        print(f"{indent}  {COLOR_LIST}[{i}]{RESET}: {COLOR_VALOR}{item}{RESET}")
            else:
                print(f"{COLOR_VALOR}{v}{RESET}")
    else:
        print(f"{indent}{COLOR_VALOR}{d}{RESET}")

def obtener_transcripcion_unificada(pathWordsPosition):
    """obtiene la transcripción por palabras y la unifica en un solo texto"""
    if not pathWordsPosition:
        print("⚠️ pathWordsPosition está vacío")
        return ""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'x-version': '1'
    }
    
    print(f"🔗 URL de transcripción: {pathWordsPosition[:80]}...")
    
    try:
        response = requests.get(pathWordsPosition, headers=headers)
        print(f"📡 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Tipo de respuesta: {type(data)}")
            
            if isinstance(data, list):
                print(f"   Lista con {len(data)} elementos")
                if len(data) > 0:
                    print(f"   Primer elemento: {data[0]}")
            elif isinstance(data, dict):
                print(f"   Diccionario con keys: {list(data.keys())}")
            
            # convertir data a string JSON
            data_string = json.dumps(data, ensure_ascii=False)
            
            # extraer las palabras y unirlas
            palabras = []
            
            # caso 1: es una lista directa de palabras
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        # manejar tanto 'w' minúscula como 'W' mayúscula
                        if 'w' in item:
                            palabras.append(item['w'])
                        elif 'W' in item:
                            palabras.append(item['W'])
                    elif isinstance(item, str):
                        palabras.append(item)
            
            # caso 2: es un diccionario con 'words'
            elif isinstance(data, dict):
                if 'words' in data:
                    for item in data['words']:
                        if isinstance(item, dict):
                            if 'w' in item:
                                palabras.append(item['w'])
                            elif 'W' in item:
                                palabras.append(item['W'])
                        elif isinstance(item, str):
                            palabras.append(item)
                # caso 3: otras posibles keys
                elif 'data' in data:
                    for item in data['data']:
                        if isinstance(item, dict):
                            if 'w' in item:
                                palabras.append(item['w'])
                            elif 'W' in item:
                                palabras.append(item['W'])
                # caso 4: puede ser que la transcripción ya venga como texto
                elif 'transcription' in data:
                    return str(data['transcription']) + "|" + data_string
                elif 'text' in data:
                    return str(data['text']) + "|" + data_string
            
            # unir las palabras con espacios
            if palabras:
                transcripcion_completa = ' '.join(palabras)
                print(f"✅ Transcripción obtenida: {len(palabras)} palabras")
                print(f"   Primeros 150 caracteres: {transcripcion_completa[:150]}...")
                return transcripcion_completa + "|" + data_string
            else:
                print(f"⚠️ No se encontraron palabras en la respuesta")
                print(f"   Estructura recibida: {str(data)[:200]}...")
                return ""
        else:
            print(f"⚠️ Error al obtener transcripción: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return ""
    except Exception as e:
        print(f"❌ Error al procesar transcripción: {e}")
        import traceback
        print(traceback.format_exc())
        return ""

def consultar_urls_posicion(pathWordsPosition, pathWordsPositionForCut):
    headers = {
        'Authorization': f'Bearer {token}',
        'x-version': 'production'
    }
    
    print("\n" + "="*80)
    print("📍 Consultando pathWordsPosition:")
    print(pathWordsPosition)
    print("="*80)
    
    try:
        response = requests.get(pathWordsPosition, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("\n🔍 Estructura de pathWordsPosition:")
            print("   w: palabra")
            print("   ci: character index inicio")
            print("   ce: character index end")
            print("   ti: time inicio (milisegundos)")
            print("   te: time end (milisegundos)")
            print("   p: posición\n")
            # imprimir_diccionario(data)
            input("\n⏸️  PAUSA - Presiona Enter para analizar los datos...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error al consultar pathWordsPosition: {e}")
    
    continuar = input("\n¿Continuar con pathWordsPositionForCut? (s/n): ")
    if continuar.lower() != 's':
        print("⏩ Omitiendo pathWordsPositionForCut\n")
        return
    
    print("\n" + "="*80)
    print("✂️  Consultando pathWordsPositionForCut:")
    print(pathWordsPositionForCut)
    print("="*80)

    headers = {
        'Authorization': f'Bearer {token}',
        'x-version': '1'
    }
    
    try:
        headers = {
        'Authorization': f'Bearer {token}',
        'x-version': '1'
        }

        response = requests.get(pathWordsPositionForCut, headers=headers)
        
        content_type = response.headers.get('Content-Type', '')
        print(f"\n📋 Content-Type: {content_type if content_type else '(vacío)'}")
        print(f"📋 Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("⚠️  Recurso no encontrado (404) - El archivo no existe o el token expiró")
        elif response.status_code == 403:
            print("⚠️  Acceso denegado (403) - No tienes permisos o el token expiró")
        elif response.status_code == 200:
            print(f"📦 Tamaño: {len(response.content)} bytes")
            
            # verificar si es JSON o archivo binario
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    print("✅ Respuesta JSON:")
                    imprimir_diccionario(data)
                    input("\n⏸️  Presiona Enter para imprimir el diccionario...")
                except:
                    print("⚠️  Content-Type dice JSON pero no se puede parsear")
                    print(f"   Primeros 100 bytes: {response.content[:100]}")
            elif 'audio' in content_type or 'octet-stream' in content_type:
                print("🎵 Es un archivo de audio (MP3 u otro formato)")
                print(f"   Primeros 20 bytes: {response.content[:20]}")
            else:
                # intentar detectar por contenido
                if len(response.content) > 3:
                    if response.content[:3] == b'ID3' or response.content[:2] == b'\xff\xfb':
                        print("🎵 Detectado como archivo MP3 por firma de archivo")
                        print(f"   Primeros 20 bytes: {response.content[:20]}")
                    else:
                        print(f"⚠️  Tipo de contenido desconocido: {content_type}")
                        try:
                            print(f"   Primeros 200 caracteres: {response.text[:200]}")
                        except:
                            print(f"   Primeros 100 bytes: {response.content[:100]}")
                else:
                    print("⚠️  Respuesta vacía")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            if len(response.content) > 0:
                try:
                    print(response.text[:500])
                except:
                    print(f"Contenido binario: {response.content[:100]}")
    except Exception as e:
        print(f"❌ Error al consultar pathWordsPositionForCut: {e}")
    
    input("\n⏸️  Presiona Enter para continuar...\n")

# Función DescargaVid eliminada - ahora la descarga se hace dentro de crear_query() 
# con extracción de duración ANTES del INSERT/UPDATE

def procesarResultados(resultados,idmedioreferencianex,idmedionex,nombre,tipo,idprogramSim,nombreprogram,horario=""):
    cont = 0
    lastId = None
    print('='*80)
    print(f'📊 Total de noticias recibidas: {len(resultados["news"])}')
    print(f'🎯 Programa interno a usar: {idprogramSim} ({nombreprogram})')
    print('='*80)
    validDescargapag = []
    
    try:
        for data in resultados['news']:
            cont += 1
            print(f"\n🔍 Procesando noticia {cont}/{len(resultados['news'])}")
            print(f"   ID: {data.get('id')}")
            print(f"   Título: {data.get('title', 'Sin título')[:80]}...")
            print(f"   ProgramId Simbiu: {data.get('programId')} ({data.get('program')})")
            
            # obtener el programa interno correspondiente
            programId_interno, nombre_interno = obtener_programa_interno(data.get('programId'))
            
            if nombre_interno:
                print(f"   🔄 Mapeado a programa interno: {programId_interno} ({nombre_interno})")
            
            imprimir_diccionario(data)
            
            # verificar si el programa mapeado coincide con el que buscamos
            if str(programId_interno) == str(idprogramSim):
                print(f"\n✅ MATCH! Procesando noticia (Simbiu: {data['programId']} → Interno: {programId_interno})")
                lastId = data['id']
                
                # obtener transcripción unificada desde pathWordsPositionForCut (audio cortado)
                transcripcion_unificada = ""
                if 'pathWordsPositionForCut' in data and data['pathWordsPositionForCut']:
                    print(f"✂️ Obteniendo transcripción desde pathWordsPositionForCut (audio cortado)...")
                    transcripcion_unificada = obtener_transcripcion_unificada(data['pathWordsPositionForCut'])
                    if transcripcion_unificada:
                        print(f"   ✅ Transcripción obtenida: {len(transcripcion_unificada)} caracteres")
                        print(f"   Primeros 100 caracteres: {transcripcion_unificada[:100]}...")
                else:
                    print("⚠️ No hay pathWordsPositionForCut disponible")
                
                # usar el nombre interno si existe mapeo, sino usar el de Simbiu
                nombre_programa_final = nombre_interno if nombre_interno else nombreprogram
                
                # usar el nombre interno también en la sección
                seccion_final = nombre_programa_final
                print(f"📂 Sección a insertar: {seccion_final}")
                
                nota = {
                    'idSimbiu'          : data['id'],
                    'idPagina'          : "",
                    'idDoc'             : "",
                    'idMedioSimbiu'     : data['mediaId'],
                    'fecha'             : data['published'],
                    'nombremedio'       : data['mediaName'],
                    'seccion'           : seccion_final,  # usar nombre interno del programa
                    'titulo'            : data['title'],
                    'texto'             : data['text'],
                    'autor'             : "" if data['author'] is None or str(data['author']) == 'None' else str(data['author']),
                    'program'           : nombre_programa_final,
                    'programId'         : programId_interno,  # usar el ID interno
                    'transcription'     : str(data['transcription']),
                    'url'               : str(data['pathMedia']),
                    'sourceTypeId'      : data.get('sourceTypeId'),  # para determinar extensión del archivo
                }
                
                # verificar si la noticia ya existe por notasolicitud en nex_transcript
                id_simbiu = nota['idSimbiu']
                print(f"\n🔍 Verificando duplicados por ID Simbiu: {id_simbiu}")
                
                # buscar en nex_transcript si ya existe ese notasolicitud
                query_check = f"SELECT id, notasolicitud FROM nex_transcript WHERE notasolicitud = '{id_simbiu}'"
                resultados_bd = run_queryPrueba(query_check)
                
                duplicado_encontrado = False
                id_duplicado = None
                
                if resultados_bd and len(resultados_bd) > 0:
                    duplicado_encontrado = True
                    id_duplicado = resultados_bd[0][0]
                    print(f"   ⚠️ ¡DUPLICADO ENCONTRADO!")
                    print(f"   📌 ID existente en BD: {id_duplicado}")
                    print(f"   📌 notasolicitud: {id_simbiu}")
                else:
                    print(f"   ✅ No se encontró duplicado (notasolicitud: {id_simbiu})")
                
                if duplicado_encontrado:
                    print(f"⚠️ ❌ DUPLICADO DETECTADO - Noticia ya existe en BD:")
                    print(f"   📌 ID existente: {id_duplicado}")
                    print(f"   📌 ID Simbiu: {id_simbiu}")
                    print(f"   📌 Título: {nota['titulo'][:80]}...")
                    print(f"   ⏭️ SALTANDO INSERT y continuando con siguiente noticia")
                    GeneraLog(nombre, 3, f"DUPLICADO detectado | ID existente: {id_duplicado} | ID Simbiu: {id_simbiu} | Título: {nota['titulo'][:100]}")
                else:
                    print(f"✅ No se encontró duplicado, procediendo con INSERT...")
                    crear_query(nota,idmedioreferencianex,idmedionex,nombre,tipo,idprogramSim,nombre_programa_final,transcripcion_unificada,horario)
                
                # pausa después de procesar cada noticia
                # input("\n⏸️  Presiona Enter para procesar la siguiente noticia...")
            else:
                print(f"⏭️ SKIP - ProgramId no coincide (Mapeado: {programId_interno} != Buscado: {idprogramSim})")
    
    except ProcesoDetenido:
        print(f"\n{'='*80}")
        print(f"🛑 Proceso detenido después de procesar {cont} noticias")
        print('='*80)
        return lastId
    
    print(f"\n{'='*80}")
    print(f"✅ Procesamiento completado. Noticias procesadas: {cont}")
    print('='*80)
    return lastId

# ========================================
# INTERFAZ GRÁFICA
# ========================================

class AppRadio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Descarga y Actualización de Noticias - Simbiu")
        self.geometry("950x750")
        self.resizable(True, True)
        self.minsize(800, 900)
        
        # configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # frame principal con padding
        container = ttk.Frame(self, padding="10")
        container.pack(fill=tk.BOTH, expand=True)
        
        # crear notebook (pestañas)
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # crear las tres pestañas
        self.tab_comparacion = ttk.Frame(self.notebook, padding="10")
        self.tab_cargar = ttk.Frame(self.notebook, padding="10")
        self.tab_actualizar = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.tab_comparacion, text="📊 Comparación Simbiu vs NexNews")
        self.notebook.add(self.tab_cargar, text="📥 Cargar Noticias")
        self.notebook.add(self.tab_actualizar, text="🔄 Actualizar Noticia")
        
        # construir la interfaz de cada pestaña
        self.build_tab_comparacion()
        self.build_tab_cargar()
        self.build_tab_actualizar()
    
    # ========================================
    # PESTAÑA 0: COMPARACIÓN SIMBIU VS NEXNEWS
    # ========================================
    def build_tab_comparacion(self):
        """construye la interfaz de comparación de noticias"""
        # título
        title_label = tk.Label(self.tab_comparacion, text="📊 PROGRAMAS CARGADOS", 
                               font=("Arial", 14, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))
        
        # ========== SELECTOR DE FECHA ==========
        fecha_frame = ttk.LabelFrame(self.tab_comparacion, text="📅 Fecha a Comparar", padding="10")
        fecha_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.comp_fecha_entry = DateEntry(fecha_frame, width=30, background='darkblue',
                                          foreground='white', borderwidth=2, 
                                          date_pattern='yyyy-mm-dd', locale='es_ES')
        self.comp_fecha_entry.pack(pady=5)
        
        # ========== SELECTOR DE RADIO ==========
        radio_frame = ttk.LabelFrame(self.tab_comparacion, text="📻 Seleccionar Radio", padding="10")
        radio_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.comp_radio_var = tk.StringVar()
        self.comp_radio_combo = ttk.Combobox(radio_frame, textvariable=self.comp_radio_var, 
                                             state="readonly", width=50)
        
        # llenar opciones de radios
        radio_options = []
        self.comp_nombre_a_mediaid = {}
        
        for media_id, radio_data in radios_programas.items():
            nombre_radio = radio_data['nombre_radio']
            radio_options.append(nombre_radio)
            self.comp_nombre_a_mediaid[nombre_radio] = media_id
        
        self.comp_radio_combo['values'] = radio_options
        self.comp_radio_combo.pack(pady=5)
        
        # ========== BOTONES COMPARAR Y SALIR ==========
        button_frame = ttk.Frame(self.tab_comparacion)
        button_frame.pack(pady=10)
        
        self.btn_comparar = ttk.Button(button_frame, text="🔍 Comparar", 
                                       command=self.ejecutar_comparacion)
        self.btn_comparar.pack(side=tk.LEFT, padx=5)
        
        self.btn_salir_comparacion = ttk.Button(button_frame, text="🚪 Salir", 
                                                command=self.salir_programa)
        self.btn_salir_comparacion.pack(side=tk.LEFT, padx=5)
        
        # ========== ÁREA DE RESULTADOS ==========
        resultados_frame = ttk.LabelFrame(self.tab_comparacion, text="📈 Resultados", padding="15")
        resultados_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # crear frame con scroll
        canvas = tk.Canvas(resultados_frame, bg='white')
        scrollbar = ttk.Scrollbar(resultados_frame, orient="vertical", command=canvas.yview)
        self.comp_resultados_frame = ttk.Frame(canvas)
        
        self.comp_resultados_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.comp_resultados_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # label inicial
        self.comp_estado_label = tk.Label(self.comp_resultados_frame, 
                                          text="Selecciona una radio y fecha para comparar", 
                                          font=("Arial", 10), fg="#7f8c8d")
        self.comp_estado_label.pack(pady=20)
    
    # ========================================
    # PESTAÑA 1: CARGAR NOTICIAS
    # ========================================
    def build_tab_cargar(self):
        """construye la interfaz de la pestaña de cargar noticias"""
        # título
        title_label = tk.Label(self.tab_cargar, text="🎙️ DESCARGA DE NOTICIAS DE RADIO", 
                               font=("Arial", 14, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))
        
        # ========== SELECTOR DE FECHA ==========
        fecha_frame = ttk.LabelFrame(self.tab_cargar, text="📅 Fecha de las Noticias", padding="10")
        fecha_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fecha_entry = DateEntry(fecha_frame, width=30, background='darkblue',
                                     foreground='white', borderwidth=2, 
                                     date_pattern='yyyy-mm-dd', locale='es_ES')
        self.fecha_entry.pack(pady=5)
        
        # ========== SELECTOR DE RADIO ==========
        radio_frame = ttk.LabelFrame(self.tab_cargar, text="📻 Seleccionar Radio", padding="10")
        radio_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.radio_var = tk.StringVar()
        self.radio_combo = ttk.Combobox(radio_frame, textvariable=self.radio_var, 
                                        state="readonly", width=50)
        
        # llenar opciones de radios (solo nombres, sin IDs)
        radio_options = []
        self.nombre_a_mediaid = {}  # mapeo de nombre_radio -> media_id
        
        for media_id, radio_data in radios_programas.items():
            nombre_radio = radio_data['nombre_radio']
            radio_options.append(nombre_radio)
            self.nombre_a_mediaid[nombre_radio] = media_id
        
        self.radio_combo['values'] = radio_options
        self.radio_combo.pack(pady=5)
        self.radio_combo.bind('<<ComboboxSelected>>', self.on_radio_selected)
        
        # ========== SELECTOR DE PROGRAMA ==========
        programa_frame = ttk.LabelFrame(self.tab_cargar, text="🎤 Seleccionar Programa", padding="10")
        programa_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.programa_var = tk.StringVar()
        self.programa_combo = ttk.Combobox(programa_frame, textvariable=self.programa_var, 
                                          state="readonly", width=50)
        self.programa_combo.pack(pady=5)
        self.programa_combo['values'] = ["Primero selecciona una radio"]
        
        # ========== BOTONES INICIAR/SALIR ==========
        button_frame = ttk.Frame(self.tab_cargar)
        button_frame.pack(pady=10)
        
        self.btn_iniciar = ttk.Button(button_frame, text="🚀 Iniciar Descarga", 
                                      command=self.iniciar_descarga)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_salir_cargar = ttk.Button(button_frame, text="🚪 Salir", 
                                           command=self.salir_programa)
        self.btn_salir_cargar.pack(side=tk.LEFT, padx=5)
        
        # ========== BARRA DE PROGRESO ==========
        progress_frame = ttk.Frame(self.tab_cargar)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', 
                                       length=700, mode='determinate')
        self.progress.pack(pady=5)
        
        # ========== LABEL DE ESTADO ==========
        self.label_estado = tk.Label(self.tab_cargar, text="Listo para comenzar", 
                                     font=("Arial", 10), fg="#27ae60")
        self.label_estado.pack(pady=10)
        
        # variables internas
        self.media_id_seleccionado = None
        self.program_id_seleccionado = None
        self.radio_data_seleccionada = None
        self.nombre_a_programid = {}  # mapeo de nombre_interno -> program_id
    
    def on_radio_selected(self, event):
        """actualiza el selector de programas según la radio seleccionada"""
        nombre_radio = self.radio_var.get()
        
        # obtener media_id desde el mapeo
        media_id = self.nombre_a_mediaid.get(nombre_radio)
        if not media_id:
            return
        
        self.media_id_seleccionado = media_id
        self.radio_data_seleccionada = radios_programas[media_id]
        
        # llenar programas y crear mapeo inverso
        programa_options = []
        self.nombre_a_programid = {}  # resetear el mapeo
        programas = self.radio_data_seleccionada['programas']
        
        for prog_id, prog_data in programas.items():
            nombre = prog_data['nombre_interno']
            programa_options.append(nombre)
            self.nombre_a_programid[nombre] = prog_id  # guardar mapeo
        
        self.programa_combo['values'] = programa_options
        self.programa_combo.set('')
        self.label_estado.config(
            text=f"Radio seleccionada: {self.radio_data_seleccionada['nombre_radio']}", 
            fg="#3498db"
        )
    
    def ejecutar_comparacion(self):
        """ejecuta la comparación entre Simbiu y NexNews"""
        # validaciones
        if not self.comp_radio_var.get():
            self.comp_estado_label.config(text="⚠️ Debes seleccionar una radio", fg="#e74c3c")
            return
        
        # deshabilitar botón
        self.btn_comparar.config(state='disabled')
        
        # ejecutar en segundo plano
        threading.Thread(
            target=self.realizar_comparacion,
            daemon=True
        ).start()
    
    def realizar_comparacion(self):
        """realiza la comparación en segundo plano"""
        try:
            # obtener datos
            nombre_radio = self.comp_radio_var.get()
            media_id = self.comp_nombre_a_mediaid.get(nombre_radio)
            fecha_str = self.comp_fecha_entry.get_date().strftime("%Y-%m-%d")
            
            radio_data = radios_programas[media_id]
            
            # limpiar resultados anteriores
            for widget in self.comp_resultados_frame.winfo_children():
                widget.destroy()
            
            # mostrar estado
            estado = tk.Label(self.comp_resultados_frame, 
                            text=f"🔍 Consultando datos para {nombre_radio} - {fecha_str}...", 
                            font=("Arial", 10), fg="#3498db")
            estado.pack(pady=10)
            self.comp_resultados_frame.update()
            
            # validar token
            print("\n🔐 Validando token...")
            if not validar_token():
                estado.config(text="❌ Error: Token inválido", fg="#e74c3c")
                self.btn_comparar.after(0, self.btn_comparar.config, {'state': 'normal'})
                return
            
            # consultar Simbiu
            print(f"\n{'='*80}")
            print(f"📡 CONSULTANDO SIMBIU")
            print(f"{'='*80}")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'x-version': 'production'
            }
            
            url = f'https://api.simbiu.es/api/MediaRecords/News?Page=1&RecordsByPage=500&DateIni={fecha_str}&DateEnd={fecha_str}&MediasIds=[{media_id}]&PaisId=CL'
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                estado.config(text=f"❌ Error al consultar Simbiu: {response.status_code}", fg="#e74c3c")
                self.btn_comparar.after(0, self.btn_comparar.config, {'state': 'normal'})
                return
            
            data_simbiu = response.json()
            noticias_simbiu = data_simbiu.get('news', [])
            
            print(f"✅ Noticias recibidas de Simbiu: {len(noticias_simbiu)}")
            
            # contar por programa en Simbiu
            conteo_simbiu = {}
            for noticia in noticias_simbiu:
                program_id = str(noticia.get('programId'))
                program_name = noticia.get('program', 'Sin programa')
                
                if program_id not in conteo_simbiu:
                    conteo_simbiu[program_id] = {
                        'nombre': program_name,
                        'cantidad': 0
                    }
                conteo_simbiu[program_id]['cantidad'] += 1
            
            print(f"📊 Conteo Simbiu: {conteo_simbiu}")
            
            # consultar NexNews
            print(f"\n{'='*80}")
            print(f"📡 CONSULTANDO NEXNEWS")
            print(f"{'='*80}")
            
            conteo_nexnews = {}
            
            # obtener el id_medio_nex de la radio
            id_medio_nex = radio_data['id_medio_nex']
            
            # consultar para cada programa
            for program_id_simbiu, program_data in radio_data['programas'].items():
                id_interno = program_data['id_interno']
                nombre_programa = program_data['nombre_interno']
                
                query = f"""SELECT COUNT(*) 
                           FROM nex_noticia 
                           WHERE fecha = '{fecha_str}' 
                           AND nex_medio_referencia = {id_medio_nex}
                           AND nex_medio_id = {id_interno}"""
                
                print(f"Query para {nombre_programa}: {query}")
                
                resultado = run_queryPrueba(query)
                cantidad = resultado[0][0] if resultado else 0
                
                conteo_nexnews[program_id_simbiu] = {
                    'nombre': nombre_programa,
                    'cantidad': cantidad
                }
                
                print(f"✅ {nombre_programa}: {cantidad} noticias")
            
            print(f"📊 Conteo NexNews: {conteo_nexnews}")
            
            # limpiar y mostrar resultados
            for widget in self.comp_resultados_frame.winfo_children():
                widget.destroy()
            
            # título de resultados
            titulo = tk.Label(self.comp_resultados_frame, 
                            text=f"Resultados para {nombre_radio} - {fecha_str}", 
                            font=("Arial", 12, "bold"), fg="#2c3e50")
            titulo.pack(pady=(10, 15))
            
            # contenedor centrado para la tabla
            tabla_container = tk.Frame(self.comp_resultados_frame)
            tabla_container.pack(anchor="center", pady=10)
            
            # encabezado de la tabla (ancho fijo)
            header_frame = tk.Frame(tabla_container, bg="#34495e", height=40, width=600)
            header_frame.pack(pady=(0, 2))
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="PROGRAMA", font=("Arial", 10, "bold"), 
                    fg="white", bg="#34495e", width=30, anchor="w", padx=10).pack(side=tk.LEFT)
            tk.Label(header_frame, text="SIMBIU", font=("Arial", 10, "bold"), 
                    fg="white", bg="#34495e", width=12, anchor="center").pack(side=tk.LEFT)
            tk.Label(header_frame, text="NEXNEWS", font=("Arial", 10, "bold"), 
                    fg="white", bg="#34495e", width=12, anchor="center").pack(side=tk.LEFT)
            
            # obtener todos los programas (unión de ambos conteos)
            todos_programas = set(conteo_simbiu.keys()) | set(conteo_nexnews.keys())
            
            # mostrar comparación para cada programa
            row_color_toggle = True
            for program_id in sorted(todos_programas):
                # obtener datos
                simbiu_data = conteo_simbiu.get(program_id, {'nombre': 'Desconocido', 'cantidad': 0})
                nexnews_data = conteo_nexnews.get(program_id, {'nombre': 'Desconocido', 'cantidad': 0})
                
                cantidad_simbiu = simbiu_data['cantidad']
                cantidad_nexnews = nexnews_data['cantidad']
                
                # usar el nombre del programa interno si existe
                if program_id in radio_data['programas']:
                    nombre_programa = radio_data['programas'][program_id]['nombre_interno']
                else:
                    nombre_programa = simbiu_data['nombre']
                
                # determinar color de fondo alternado
                bg_color = "#ecf0f1" if row_color_toggle else "white"
                row_color_toggle = not row_color_toggle
                
                # frame para cada programa (ancho fijo)
                prog_frame = tk.Frame(tabla_container, bg=bg_color, height=35, width=600)
                prog_frame.pack(pady=1)
                prog_frame.pack_propagate(False)
                
                # nombre del programa
                tk.Label(prog_frame, text=nombre_programa, font=("Arial", 9), 
                        bg=bg_color, width=30, anchor="w", padx=10).pack(side=tk.LEFT)
                
                # cantidad Simbiu (izquierda)
                simbiu_color = "#27ae60" if cantidad_simbiu == cantidad_nexnews else "#3498db"
                tk.Label(prog_frame, text=str(cantidad_simbiu), font=("Arial", 11, "bold"), 
                        fg=simbiu_color, bg=bg_color, width=12, anchor="center").pack(side=tk.LEFT)
                
                # cantidad NexNews (derecha)
                nexnews_color = "#27ae60" if cantidad_simbiu == cantidad_nexnews else "#e74c3c"
                tk.Label(prog_frame, text=str(cantidad_nexnews), font=("Arial", 11, "bold"), 
                        fg=nexnews_color, bg=bg_color, width=12, anchor="center").pack(side=tk.LEFT)
            
            # separador (ancho fijo)
            separator_frame = tk.Frame(tabla_container, width=600, height=2)
            separator_frame.pack(pady=15)
            ttk.Separator(separator_frame, orient='horizontal').pack(fill=tk.X)
            
            # totales (ancho fijo)
            total_simbiu = sum(d['cantidad'] for d in conteo_simbiu.values())
            total_nexnews = sum(d['cantidad'] for d in conteo_nexnews.values())
            
            total_frame = tk.Frame(tabla_container, bg="#2c3e50", height=45, width=600)
            total_frame.pack(pady=(0, 10))
            total_frame.pack_propagate(False)
            
            tk.Label(total_frame, text="TOTAL", font=("Arial", 11, "bold"), 
                    fg="white", bg="#2c3e50", width=30, anchor="w", padx=10).pack(side=tk.LEFT)
            
            # total Simbiu
            total_simbiu_color = "#27ae60" if total_simbiu == total_nexnews else "#3498db"
            tk.Label(total_frame, text=str(total_simbiu), font=("Arial", 12, "bold"), 
                    fg=total_simbiu_color, bg="#2c3e50", width=12, anchor="center").pack(side=tk.LEFT)
            
            # total NexNews
            total_nexnews_color = "#27ae60" if total_simbiu == total_nexnews else "#e74c3c"
            tk.Label(total_frame, text=str(total_nexnews), font=("Arial", 12, "bold"), 
                    fg=total_nexnews_color, bg="#2c3e50", width=12, anchor="center").pack(side=tk.LEFT)
            
            print(f"\n{'='*80}")
            print(f"✅ COMPARACIÓN COMPLETADA")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"❌ Error en comparación: {e}")
            import traceback
            print(traceback.format_exc())
            
            # mostrar error en UI
            for widget in self.comp_resultados_frame.winfo_children():
                widget.destroy()
            
            error_label = tk.Label(self.comp_resultados_frame, 
                                  text=f"❌ Error: {str(e)}", 
                                  font=("Arial", 10), fg="#e74c3c")
            error_label.pack(pady=20)
        
        finally:
            # habilitar botón
            self.btn_comparar.after(0, self.btn_comparar.config, {'state': 'normal'})
    
    # ========================================
    # PESTAÑA 2: ACTUALIZAR NOTICIA
    # ========================================
    def build_tab_actualizar(self):
        """construye la interfaz de la pestaña de actualizar noticia"""
        # título
        title_label = tk.Label(self.tab_actualizar, text="🔄 ACTUALIZAR NOTICIA EXISTENTE", 
                               font=("Arial", 14, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))
        
        # ========== INPUT DE ID INTERNO ==========
        id_frame = ttk.LabelFrame(self.tab_actualizar, text="🔍 Buscar Noticia por ID Interno", padding="15")
        id_frame.pack(fill=tk.X, pady=(0, 15))
        
        # input y botón en la misma línea
        input_row = ttk.Frame(id_frame)
        input_row.pack(fill=tk.X, pady=5)
        
        tk.Label(input_row, text="ID Interno:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.id_interno_var = tk.StringVar()
        self.id_interno_entry = ttk.Entry(input_row, textvariable=self.id_interno_var, width=20, font=("Arial", 11))
        self.id_interno_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_verificar = ttk.Button(input_row, text="🔎 Verificar", command=self.verificar_noticia)
        self.btn_verificar.pack(side=tk.LEFT)
        
        # ========== INFORMACIÓN DE LA NOTICIA ==========
        info_frame = ttk.LabelFrame(self.tab_actualizar, text="📋 Información de la Noticia", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # crear labels para mostrar la información
        self.info_id_label = tk.Label(info_frame, text="ID: -", font=("Arial", 10), anchor="w")
        self.info_id_label.pack(fill=tk.X, pady=2)
        
        self.info_fecha_label = tk.Label(info_frame, text="Fecha: -", font=("Arial", 10), anchor="w")
        self.info_fecha_label.pack(fill=tk.X, pady=2)
        
        self.info_programa_label = tk.Label(info_frame, text="Programa: -", font=("Arial", 10), anchor="w")
        self.info_programa_label.pack(fill=tk.X, pady=2)
        
        self.info_titulo_label = tk.Label(info_frame, text="Título: -", font=("Arial", 10), anchor="w", wraplength=700, justify="left")
        self.info_titulo_label.pack(fill=tk.X, pady=2)
        
        self.info_simbiu_label = tk.Label(info_frame, text="ID Simbiu: -", font=("Arial", 10), anchor="w")
        self.info_simbiu_label.pack(fill=tk.X, pady=2)
        
        # ========== OPCIONES DE ACTUALIZACIÓN ==========
        opciones_frame = ttk.LabelFrame(self.tab_actualizar, text="⚙️ Opciones de Actualización", padding="15")
        opciones_frame.pack(fill=tk.X, pady=(0, 10))
        
        # variable para la selección
        self.opcion_actualizacion_var = tk.StringVar(value="")
        
        # radiobuttons
        ttk.Radiobutton(opciones_frame, text="📝 Actualizar Transcripción", 
                       variable=self.opcion_actualizacion_var, value="transcripcion").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(opciones_frame, text="🎬 Actualizar Video/Audio", 
                       variable=self.opcion_actualizacion_var, value="video").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(opciones_frame, text="📄 Actualizar Cuerpo", 
                       variable=self.opcion_actualizacion_var, value="cuerpo").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(opciones_frame, text="📰 Actualizar Título", 
                       variable=self.opcion_actualizacion_var, value="titulo").pack(anchor=tk.W, pady=5)
        
        # ========== BOTÓN EJECUTAR ==========
        button_frame = ttk.Frame(self.tab_actualizar)
        button_frame.pack(pady=10)
        
        self.btn_ejecutar_actualizacion = ttk.Button(button_frame, text="✅ Ejecutar Actualización", 
                                                     command=self.ejecutar_actualizacion, state='disabled')
        self.btn_ejecutar_actualizacion.pack(side=tk.LEFT, padx=5)
        
        self.btn_salir_actualizar = ttk.Button(button_frame, text="🚪 Salir", 
                                               command=self.salir_programa)
        self.btn_salir_actualizar.pack(side=tk.LEFT, padx=5)
        
        # ========== LABEL DE ESTADO ACTUALIZACIÓN ==========
        self.label_estado_actualizacion = tk.Label(self.tab_actualizar, text="Ingresa un ID para comenzar", 
                                                   font=("Arial", 10), fg="#7f8c8d")
        self.label_estado_actualizacion.pack(pady=10)
        
        # variable interna para guardar datos de la noticia
        self.noticia_actual = None
    
    def verificar_noticia(self):
        """verifica si existe la noticia con el ID interno ingresado"""
        id_interno = self.id_interno_var.get().strip()
        
        if not id_interno:
            self.label_estado_actualizacion.config(text="⚠️ Debes ingresar un ID", fg="#e74c3c")
            return
        
        if not id_interno.isdigit():
            self.label_estado_actualizacion.config(text="⚠️ El ID debe ser numérico", fg="#e74c3c")
            return
        
        self.label_estado_actualizacion.config(text="🔍 Buscando noticia...", fg="#3498db")
        
        # buscar la noticia en la BD
        query = f"""SELECT n.id, n.fecha, n.empresa, n.titulo, t.notasolicitud 
                    FROM nex_noticia n 
                    LEFT JOIN nex_transcript t ON n.id = t.id 
                    WHERE n.id = {id_interno}"""
        
        try:
            resultado = run_queryPrueba(query)
            
            if not resultado or len(resultado) == 0:
                self.label_estado_actualizacion.config(text="❌ No se encontró noticia con ese ID", fg="#e74c3c")
                self.info_id_label.config(text="ID: -")
                self.info_fecha_label.config(text="Fecha: -")
                self.info_programa_label.config(text="Programa: -")
                self.info_titulo_label.config(text="Título: -")
                self.info_simbiu_label.config(text="ID Simbiu: -")
                self.btn_ejecutar_actualizacion.config(state='disabled')
                self.noticia_actual = None
                return
            
            # extraer datos
            row = resultado[0]
            id_bd = row[0]
            fecha = row[1]
            programa = row[2] if row[2] else "Sin programa"
            titulo = row[3]
            id_simbiu = row[4] if row[4] else "No disponible"
            
            # guardar datos
            self.noticia_actual = {
                'id': id_bd,
                'fecha': fecha,
                'programa': programa,
                'titulo': titulo,
                'id_simbiu': id_simbiu
            }
            
            # mostrar información
            self.info_id_label.config(text=f"ID: {id_bd}")
            self.info_fecha_label.config(text=f"Fecha: {fecha}")
            self.info_programa_label.config(text=f"Programa: {programa}")
            self.info_titulo_label.config(text=f"Título: {titulo}")
            self.info_simbiu_label.config(text=f"ID Simbiu: {id_simbiu}")
            
            self.label_estado_actualizacion.config(text="✅ Noticia encontrada - Selecciona una opción", fg="#27ae60")
            self.btn_ejecutar_actualizacion.config(state='normal')
            
        except Exception as e:
            self.label_estado_actualizacion.config(text=f"❌ Error: {str(e)}", fg="#e74c3c")
            print(f"Error al buscar noticia: {e}")
    
    def ejecutar_actualizacion(self):
        """ejecuta la actualización seleccionada"""
        if not self.noticia_actual:
            self.label_estado_actualizacion.config(text="⚠️ Primero verifica una noticia", fg="#e74c3c")
            return
        
        opcion = self.opcion_actualizacion_var.get()
        
        if not opcion:
            self.label_estado_actualizacion.config(text="⚠️ Selecciona una opción de actualización", fg="#e74c3c")
            return
        
        # validar que exista ID de Simbiu
        if self.noticia_actual['id_simbiu'] == "No disponible" and opcion in ['transcripcion', 'video', 'titulo']:
            self.label_estado_actualizacion.config(
                text="❌ Esta noticia no tiene ID de Simbiu - No se puede actualizar desde API", 
                fg="#e74c3c"
            )
            return
        
        # deshabilitar botón mientras procesa
        self.btn_ejecutar_actualizacion.config(state='disabled')
        
        # ejecutar en hilo separado
        threading.Thread(
            target=self.realizar_actualizacion,
            args=(opcion,),
            daemon=True
        ).start()
    
    def realizar_actualizacion(self, opcion):
        """realiza la actualización seleccionada en segundo plano"""
        try:
            if opcion == "transcripcion":
                self.actualizar_transcripcion()
            elif opcion == "video":
                self.actualizar_video()
            elif opcion == "cuerpo":
                self.actualizar_cuerpo()
            elif opcion == "titulo":
                self.actualizar_titulo()
        except Exception as e:
            print(f"Error en actualización: {e}")
            import traceback
            print(traceback.format_exc())
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': f"❌ Error: {str(e)}",
                'fg': '#e74c3c'
            })
        finally:
            self.btn_ejecutar_actualizacion.after(0, self.btn_ejecutar_actualizacion.config, {'state': 'normal'})
    
    def actualizar_transcripcion(self):
        """actualiza la transcripción desde la API de Simbiu"""
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '📝 Obteniendo transcripción desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        # validar token antes de continuar
        print("\n🔐 Validando token...")
        if not validar_token():
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '❌ Error: Token inválido',
                'fg': '#e74c3c'
            })
            return
        
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '📝 Obteniendo transcripción desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        id_simbiu = self.noticia_actual['id_simbiu']
        id_interno = self.noticia_actual['id']
        fecha = self.noticia_actual['fecha']
        
        print(f"\n{'='*80}")
        print(f"🔄 ACTUALIZANDO TRANSCRIPCIÓN")
        print(f"{'='*80}")
        print(f"ID Interno: {id_interno}")
        print(f"ID Simbiu: {id_simbiu}")
        print(f"Fecha: {fecha}")
        
        # extraer fecha en formato YYYY-MM-DD
        fecha_str = str(fecha).split('T')[0] if 'T' in str(fecha) else str(fecha).split(' ')[0]
        
        headers = {
            'Authorization': f'Bearer {token}',
            'x-version': 'production'
        }
        
        # buscar en todas las páginas hasta encontrar el ID (paginación)
        print(f"🔍 Buscando ID Simbiu exacto: {id_simbiu}")
        print(f"📅 Fecha: {fecha_str}")
        
        data = None
        page = 1
        records_per_page = 200
        total_noticias_revisadas = 0
        
        try:
            while data is None:
                url = f'https://api.simbiu.es/api/MediaRecords/News?Page={page}&RecordsByPage={records_per_page}&DateIni={fecha_str}&DateEnd={fecha_str}&PaisId=CL'
                
                print(f"📄 Consultando página {page}...")
                print(f"🔗 URL: {url}")
                
                response = requests.get(url, headers=headers)
                
                print(f"📡 Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error al consultar API: {response.status_code}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ Error al consultar API: {response.status_code}',
                        'fg': '#e74c3c'
                    })
                    return
                
                result = response.json()
                
                # la respuesta viene en formato { "news": [...] }
                if not result.get('news') or len(result['news']) == 0:
                    # no hay más noticias, no se encontró el ID
                    print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                    print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                        'fg': '#e74c3c'
                    })
                    return
                
                print(f"✅ Respuesta obtenida - {len(result['news'])} noticias en esta página")
                total_noticias_revisadas += len(result['news'])
                
                # buscar el ID específico en esta página
                for noticia in result['news']:
                    noticia_id = str(noticia.get('id'))
                    if noticia_id == str(id_simbiu):
                        data = noticia
                        print(f"   ✅ ¡MATCH! Noticia encontrada - ID: {data.get('id')}")
                        print(f"      Título: {data.get('title', '')[:60]}...")
                        print(f"      Página: {page}")
                        print(f"      Total revisadas: {total_noticias_revisadas}")
                        break
                
                # si no se encontró en esta página, pasar a la siguiente
                if data is None:
                    # si la página no está completa, significa que no hay más páginas
                    if len(result['news']) < records_per_page:
                        print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                        print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                            'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                            'fg': '#e74c3c'
                        })
                        return
                    page += 1
            
            # obtener transcripción desde pathWordsPositionForCut
            transcripcion_unificada = ""
            if 'pathWordsPositionForCut' in data and data['pathWordsPositionForCut']:
                print(f"✂️ Obteniendo transcripción desde pathWordsPositionForCut...")
                transcripcion_unificada = obtener_transcripcion_unificada(data['pathWordsPositionForCut'])
            
            if transcripcion_unificada:
                transcripcion_texto = transcripcion_unificada.split("|")[0]
                pieImagen = transcripcion_unificada.split("|")[1]
                
                print(f"✅ Transcripción obtenida: {len(transcripcion_texto)} caracteres")
                
                # actualizar en BD
                UpdateQuery = f"""UPDATE nex_noticia SET 
                    ctexto=\"{escapeString(str(transcripcion_texto))}\",
                    `cache`=\"{escapeString(str(transcripcion_texto))}\"
                    WHERE id={id_interno};"""
                
                run_queryPrueba(UpdateQuery)
                print(f"✅ nex_noticia actualizada")
                
                # actualizar nex_transcript
                UpdateTranscriptQuery = f"""UPDATE nex_transcript SET 
                    texto=\"{escapeString(str(transcripcion_texto))}\",
                    alturacion=\"{escapeString(str(pieImagen))}\"
                    WHERE id={id_interno};"""
                
                run_queryPrueba(UpdateTranscriptQuery)
                print(f"✅ nex_transcript actualizada")
                
                self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                    'text': '✅ Transcripción actualizada exitosamente',
                    'fg': '#27ae60'
                })
            else:
                self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                    'text': '⚠️ No se pudo obtener transcripción de Simbiu',
                    'fg': '#e67e22'
                })
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def actualizar_video(self):
        """actualiza el archivo de video/audio desde Simbiu"""
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '🎬 Descargando archivo desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        # validar token antes de continuar
        print("\n🔐 Validando token...")
        if not validar_token():
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '❌ Error: Token inválido',
                'fg': '#e74c3c'
            })
            return
        
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '🎬 Descargando archivo desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        id_simbiu = self.noticia_actual['id_simbiu']
        id_interno = self.noticia_actual['id']
        fecha = self.noticia_actual['fecha']
        
        print(f"\n{'='*80}")
        print(f"🔄 ACTUALIZANDO VIDEO/AUDIO")
        print(f"{'='*80}")
        print(f"ID Interno: {id_interno}")
        print(f"ID Simbiu: {id_simbiu}")
        print(f"Fecha: {fecha}")
        
        # extraer fecha en formato YYYY-MM-DD
        fecha_str = str(fecha).split('T')[0] if 'T' in str(fecha) else str(fecha).split(' ')[0]
        
        headers = {
            'Authorization': f'Bearer {token}',
            'x-version': 'production'
        }
        
        # buscar en todas las páginas hasta encontrar el ID (paginación)
        print(f"🔍 Buscando ID Simbiu exacto: {id_simbiu}")
        print(f"📅 Fecha: {fecha_str}")
        
        data = None
        page = 1
        records_per_page = 200
        total_noticias_revisadas = 0
        
        try:
            while data is None:
                url = f'https://api.simbiu.es/api/MediaRecords/News?Page={page}&RecordsByPage={records_per_page}&DateIni={fecha_str}&DateEnd={fecha_str}&PaisId=CL'
                
                print(f"📄 Consultando página {page}...")
                print(f"🔗 URL: {url}")
                
                response = requests.get(url, headers=headers)
                
                print(f"📡 Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error al consultar API: {response.status_code}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ Error al consultar API: {response.status_code}',
                        'fg': '#e74c3c'
                    })
                    return
                
                result = response.json()
                
                # la respuesta viene en formato { "news": [...] }
                if not result.get('news') or len(result['news']) == 0:
                    # no hay más noticias, no se encontró el ID
                    print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                    print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                        'fg': '#e74c3c'
                    })
                    return
                
                print(f"✅ Respuesta obtenida - {len(result['news'])} noticias en esta página")
                total_noticias_revisadas += len(result['news'])
                
                # buscar el ID específico en esta página
                for noticia in result['news']:
                    noticia_id = str(noticia.get('id'))
                    if noticia_id == str(id_simbiu):
                        data = noticia
                        print(f"   ✅ ¡MATCH! Noticia encontrada - ID: {data.get('id')}")
                        print(f"      Título: {data.get('title', '')[:60]}...")
                        print(f"      Página: {page}")
                        print(f"      Total revisadas: {total_noticias_revisadas}")
                        break
                
                # si no se encontró en esta página, pasar a la siguiente
                if data is None:
                    # si la página no está completa, significa que no hay más páginas
                    if len(result['news']) < records_per_page:
                        print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                        print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                            'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                            'fg': '#e74c3c'
                        })
                        return
                    page += 1
            
            url_media = data.get('pathMedia')
            source_type_id = data.get('sourceTypeId')
            
            if not url_media:
                self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                    'text': '❌ No se encontró URL del archivo en Simbiu',
                    'fg': '#e74c3c'
                })
                return
            
            # descargar archivo
            print(f"📥 Descargando archivo...")
            archivo_info = descargar_y_extraer_duracion(url_media, source_type_id, "Actualización")
            
            if not archivo_info:
                self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                    'text': '❌ Error al descargar archivo',
                    'fg': '#e74c3c'
                })
                return
            
            duracion = archivo_info['duracion']
            archivo_temp = archivo_info['archivo_temp']
            extension = archivo_info['extension']
            
            print(f"✅ Archivo descargado: {duracion}")
            
            # renombrar con el ID interno
            nombre_final = str(id_interno) + extension
            archivo_final = os.path.join(BASE_DIR, nombre_final)
            
            try:
                os.rename(archivo_temp, archivo_final)
                print(f"✅ Archivo renombrado: {nombre_final}")
            except:
                import shutil
                shutil.copy2(archivo_temp, archivo_final)
                os.remove(archivo_temp)
            
            # subir al SFTP
            print(f"⬆️ Subiendo al SFTP...")
            subir_archivo_sftp(archivo_final, nombre_final, id_interno, "Actualización", "Actualización", fecha)
            
            # actualizar duración en BD
            UpdateQuery = f"UPDATE nex_noticia SET duracion=\"{duracion}\" WHERE id={id_interno};"
            run_queryPrueba(UpdateQuery)
            print(f"✅ Duración actualizada en BD")
            
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '✅ Video/Audio actualizado exitosamente',
                'fg': '#27ae60'
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def actualizar_cuerpo(self):
        """actualiza el cuerpo de la noticia desde Simbiu"""
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '📄 Obteniendo cuerpo desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        # validar token antes de continuar
        print("\n🔐 Validando token...")
        if not validar_token():
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '❌ Error: Token inválido',
                'fg': '#e74c3c'
            })
            return
        
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '📄 Obteniendo cuerpo desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        id_simbiu = self.noticia_actual['id_simbiu']
        id_interno = self.noticia_actual['id']
        fecha = self.noticia_actual['fecha']
        
        print(f"\n{'='*80}")
        print(f"🔄 ACTUALIZANDO CUERPO")
        print(f"{'='*80}")
        print(f"ID Interno: {id_interno}")
        print(f"ID Simbiu: {id_simbiu}")
        print(f"Fecha: {fecha}")
        
        # extraer fecha en formato YYYY-MM-DD
        fecha_str = str(fecha).split('T')[0] if 'T' in str(fecha) else str(fecha).split(' ')[0]
        
        headers = {
            'Authorization': f'Bearer {token}',
            'x-version': 'production'
        }
        
        # buscar en todas las páginas hasta encontrar el ID (paginación)
        print(f"🔍 Buscando ID Simbiu exacto: {id_simbiu}")
        print(f"📅 Fecha: {fecha_str}")
        
        data = None
        page = 1
        records_per_page = 200
        total_noticias_revisadas = 0
        
        try:
            while data is None:
                url = f'https://api.simbiu.es/api/MediaRecords/News?Page={page}&RecordsByPage={records_per_page}&DateIni={fecha_str}&DateEnd={fecha_str}&PaisId=CL'
                
                print(f"📄 Consultando página {page}...")
                print(f"🔗 URL: {url}")
                
                response = requests.get(url, headers=headers)
                
                print(f"📡 Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error al consultar API: {response.status_code}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ Error al consultar API: {response.status_code}',
                        'fg': '#e74c3c'
                    })
                    return
                
                result = response.json()
                
                # la respuesta viene en formato { "news": [...] }
                if not result.get('news') or len(result['news']) == 0:
                    # no hay más noticias, no se encontró el ID
                    print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                    print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                        'fg': '#e74c3c'
                    })
                    return
                
                print(f"✅ Respuesta obtenida - {len(result['news'])} noticias en esta página")
                total_noticias_revisadas += len(result['news'])
                
                # buscar el ID específico en esta página
                for noticia in result['news']:
                    noticia_id = str(noticia.get('id'))
                    if noticia_id == str(id_simbiu):
                        data = noticia
                        print(f"   ✅ ¡MATCH! Noticia encontrada - ID: {data.get('id')}")
                        print(f"      Título: {data.get('title', '')[:60]}...")
                        print(f"      Página: {page}")
                        print(f"      Total revisadas: {total_noticias_revisadas}")
                        break
                
                # si no se encontró en esta página, pasar a la siguiente
                if data is None:
                    # si la página no está completa, significa que no hay más páginas
                    if len(result['news']) < records_per_page:
                        print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                        print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                            'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                            'fg': '#e74c3c'
                        })
                        return
                    page += 1
            
            # obtener título
            titulo_original = data.get('title', '')
            
            # procesar título igual que en crear_query
            titulo_final = titulo_original
            contenido_adicional = ""
            
            punto_pos = titulo_original.find('.')
            
            if punto_pos != -1 and punto_pos > 0:
                titulo_final = titulo_original[:punto_pos + 1].strip()
                contenido_adicional = titulo_original[punto_pos + 1:].strip()
            
            # truncar
            titulo_final = titulo_final[:255]
            
            print(f"✅ Título: {titulo_final}")
            print(f"✅ Cuerpo: {contenido_adicional[:100]}...")
            
            # actualizar en BD
            UpdateQuery = f"""UPDATE nex_noticia SET 
                titulo=\"{escapeString(str(titulo_final))}\",
                cuerpo=\"{escapeString(str(contenido_adicional))}\"
                WHERE id={id_interno};"""
            
            run_queryPrueba(UpdateQuery)
            print(f"✅ Noticia actualizada")
            
            # actualizar el label con el nuevo título
            self.info_titulo_label.config(text=f"Título: {titulo_final}")
            
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '✅ Cuerpo actualizado exitosamente',
                'fg': '#27ae60'
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def actualizar_titulo(self):
        """actualiza el título de la noticia desde Simbiu"""
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '🔐 Validando token...',
            'fg': '#3498db'
        })
        
        # validar token antes de continuar
        print("\n🔐 Validando token...")
        if not validar_token():
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '❌ Error: Token inválido',
                'fg': '#e74c3c'
            })
            return
        
        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
            'text': '📰 Obteniendo título desde API de Simbiu...',
            'fg': '#3498db'
        })
        
        id_simbiu = self.noticia_actual['id_simbiu']
        id_interno = self.noticia_actual['id']
        fecha = self.noticia_actual['fecha']
        
        print(f"\n{'='*80}")
        print(f"🔄 ACTUALIZANDO TÍTULO")
        print(f"{'='*80}")
        print(f"ID Interno: {id_interno}")
        print(f"ID Simbiu: {id_simbiu}")
        print(f"Fecha: {fecha}")
        
        # extraer fecha en formato YYYY-MM-DD
        fecha_str = str(fecha).split('T')[0] if 'T' in str(fecha) else str(fecha).split(' ')[0]
        
        headers = {
            'Authorization': f'Bearer {token}',
            'x-version': 'production'
        }
        
        # buscar en todas las páginas hasta encontrar el ID (paginación)
        print(f"🔍 Buscando ID Simbiu exacto: {id_simbiu}")
        print(f"📅 Fecha: {fecha_str}")
        
        data = None
        page = 1
        records_per_page = 200
        total_noticias_revisadas = 0
        
        try:
            while data is None:
                url = f'https://api.simbiu.es/api/MediaRecords/News?Page={page}&RecordsByPage={records_per_page}&DateIni={fecha_str}&DateEnd={fecha_str}&PaisId=CL'
                
                print(f"📄 Consultando página {page}...")
                print(f"🔗 URL: {url}")
                
                response = requests.get(url, headers=headers)
                
                print(f"📡 Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error al consultar API: {response.status_code}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ Error al consultar API: {response.status_code}',
                        'fg': '#e74c3c'
                    })
                    return
                
                result = response.json()
                
                # la respuesta viene en formato { "news": [...] }
                if not result.get('news') or len(result['news']) == 0:
                    # no hay más noticias, no se encontró el ID
                    print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                    print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                    self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                        'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                        'fg': '#e74c3c'
                    })
                    return
                
                print(f"✅ Respuesta obtenida - {len(result['news'])} noticias en esta página")
                total_noticias_revisadas += len(result['news'])
                
                # buscar el ID específico en esta página
                for noticia in result['news']:
                    noticia_id = str(noticia.get('id'))
                    if noticia_id == str(id_simbiu):
                        data = noticia
                        print(f"   ✅ ¡MATCH! Noticia encontrada - ID: {data.get('id')}")
                        print(f"      Título: {data.get('title', '')[:60]}...")
                        print(f"      Página: {page}")
                        print(f"      Total revisadas: {total_noticias_revisadas}")
                        break
                
                # si no se encontró en esta página, pasar a la siguiente
                if data is None:
                    # si la página no está completa, significa que no hay más páginas
                    if len(result['news']) < records_per_page:
                        print(f"📊 Total de noticias revisadas: {total_noticias_revisadas}")
                        print(f"❌ No se encontró noticia con ID exacto: {id_simbiu}")
                        self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                            'text': f'❌ No se encontró noticia con ID Simbiu {id_simbiu} (revisadas {total_noticias_revisadas} noticias)',
                            'fg': '#e74c3c'
                        })
                        return
                    page += 1
            
            # procesar título igual que en NoInterfaceApi.py y crear_query
            titulo_original = data.get('title', '')
            
            print(f"\n{'='*80}")
            print(f"PROCESANDO TÍTULO")
            print(f"{'='*80}")
            print(f"Título original: {titulo_original}")
            
            titulo_final = titulo_original
            contenido_adicional = ""
            
            punto_pos = titulo_original.find('.')
            
            if punto_pos != -1 and punto_pos > 0:
                # dividir en el primer punto encontrado
                titulo_final = titulo_original[:punto_pos + 1].strip()
                contenido_adicional = titulo_original[punto_pos + 1:].strip()
                print(f"✅ Título dividido en el primer punto (posición {punto_pos})")
                print(f"   • Nuevo título ({len(titulo_final)} chars): {titulo_final[:80]}...")
                if contenido_adicional:
                    print(f"   • Contenido adicional ({len(contenido_adicional)} chars): {contenido_adicional[:80]}...")
            else:
                print(f"⚠️ No se encontró punto en el título, se usará completo")
            
            # truncar a 255 caracteres para evitar errores de BD
            titulo_final = titulo_final[:255]
            
            print(f"\n✅ Título final: {titulo_final}")
            print(f"✅ Cuerpo: {contenido_adicional[:100]}..." if contenido_adicional else "✅ Cuerpo: (vacío)")
            
            # actualizar en BD
            print(f"\n{'='*80}")
            print(f"ACTUALIZANDO EN BASE DE DATOS")
            print(f"{'='*80}")
            
            UpdateQuery = f"""UPDATE nex_noticia SET 
                titulo=\"{escapeString(str(titulo_final))}\",
                cuerpo=\"{escapeString(str(contenido_adicional))}\"
                WHERE id={id_interno};"""
            
            run_queryPrueba(UpdateQuery)
            print(f"✅ Noticia actualizada - ID: {id_interno}")
            
            # actualizar el label con el nuevo título
            self.info_titulo_label.config(text=f"Título: {titulo_final}")
            
            self.label_estado_actualizacion.after(0, self.label_estado_actualizacion.config, {
                'text': '✅ Título actualizado exitosamente',
                'fg': '#27ae60'
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    # ========================================
    # MÉTODOS DE LA PESTAÑA CARGAR NOTICIAS
    # ========================================
    def iniciar_descarga(self):
        """inicia el proceso de descarga en segundo plano"""
        # validaciones
        if not self.radio_var.get():
            self.label_estado.config(text="⚠️ Debes seleccionar una radio", fg="#e74c3c")
            return
        
        if not self.programa_var.get():
            self.label_estado.config(text="⚠️ Debes seleccionar un programa", fg="#e74c3c")
            return
        
        # obtener program_id desde el mapeo inverso
        nombre_programa = self.programa_var.get()
        program_id = self.nombre_a_programid.get(nombre_programa)
        
        if not program_id:
            self.label_estado.config(text="⚠️ Error: No se pudo identificar el programa", fg="#e74c3c")
            return
        
        self.program_id_seleccionado = program_id
        
        # obtener fecha
        fecha_seleccionada = self.fecha_entry.get_date().strftime("%Y-%m-%d")
        
        # obtener datos del programa
        programa_data = self.radio_data_seleccionada['programas'][program_id]
        
        # información para la consola
        print("\n" + "="*80)
        print("🚀 INICIANDO DESCARGA")
        print("="*80)
        print(f"📅 Fecha: {fecha_seleccionada}")
        print(f"📻 Radio: {self.radio_data_seleccionada['nombre_radio']}")
        print(f"🎤 Programa: {programa_data['nombre_interno']}")
        print(f"🆔 ID Interno: {programa_data['id_interno']}")
        print("="*80 + "\n")
        
        # validar token antes de continuar
        self.label_estado.config(text="🔐 Validando token...", fg="#3498db")
        if not validar_token():
            self.label_estado.config(text="❌ Error: Token inválido. No se puede continuar", fg="#e74c3c")
            print("❌ No se pudo validar el token. Abortando proceso.")
            pass
        
        # actualizar UI
        self.label_estado.config(
            text=f"Descargando noticias de {programa_data['nombre_interno']}...", 
            fg="#f39c12"
        )
        self.btn_iniciar.config(state='disabled')
        
        # iniciar descarga en hilo separado
        threading.Thread(
            target=self.ejecutar_descarga,
            args=(fecha_seleccionada, programa_data),
            daemon=True
        ).start()
    
    def salir_programa(self):
        """cierra el programa completamente"""
        print("\n" + "="*80)
        print("🚪 SALIENDO DEL PROGRAMA...")
        print("="*80 + "\n")
        
        # cerrar la aplicación completamente
        os._exit(0)
    
    def ejecutar_descarga(self, fecha, programa_data):
        """ejecuta la descarga en segundo plano"""
        try:
            # llamar a consultarApi con los parámetros correctos
            consultarApi(
                idMedio=self.media_id_seleccionado,
                lastId=0,
                idmedioreferencianex=self.radio_data_seleccionada['id_medio_nex'],  # ID de la radio (171, 172, etc.)
                idmedionex=programa_data['id_interno'],  # ID del programa interno (3170, 3663, etc.)
                nombre=self.radio_data_seleccionada['nombre_radio'],
                tipo=self.radio_data_seleccionada['tipo'],
                idprogramSim=programa_data['id_interno'],
                nombreprogram=programa_data['nombre_interno'],
                fecha_consulta=fecha,
                horario=programa_data.get('horario', '')
            )
            
            # descarga completada
            self.finalizar_descarga(nombre_programa=programa_data['nombre_interno'])
        
        except Exception as e:
            print(f"❌ Error durante la descarga: {e}")
            import traceback
            print(traceback.format_exc())
            
            self.label_estado.after(0, self.label_estado.config, {
                'text': f"❌ Error: {str(e)}",
                'fg': '#e74c3c'
            })
            self.btn_iniciar.after(0, self.btn_iniciar.config, {'state': 'normal'})
    
    def finalizar_descarga(self, nombre_programa=""):
        """finaliza la descarga y restaura la UI"""
        self.label_estado.after(0, self.label_estado.config, {
            'text': f"✅ Descarga completada: {nombre_programa}",
            'fg': '#27ae60'
        })
        
        # restaurar botón iniciar
        self.btn_iniciar.after(0, self.btn_iniciar.config, {'state': 'normal'})

def main():
    """función principal que inicia la aplicación"""
    app = AppRadio()
    app.mainloop()

if __name__ == "__main__":
    main()
