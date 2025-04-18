import cv2
import pytesseract
import os
from datetime import datetime
import numpy as np

# Configuración de la ruta para Tesseract
tesseract_path = '/usr/share/tesseract-ocr/5/tessdata'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'  # Asegurarse de que la ruta esté correctamente configurada
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Asegurarse de que la ruta del ejecutable de tesseract esté correcta

# Verificar si el archivo de idioma está presente
if not os.path.exists(os.path.join(tesseract_path, 'spa.traineddata')):
    print("Error: El archivo de idioma 'spa.traineddata' no se encuentra en el directorio de tessdata.")
    exit()

# Función para mejorar el contraste de la imagen (sin convertir a escala de grises)
def aumentar_contraste(imagen):
    alpha = 2.0  # Ajusta el contraste según lo necesites
    beta = 0     # Controla el brillo
    return cv2.convertScaleAbs(imagen, alpha=alpha, beta=beta)

# Filtro de suavizado para reducir el ruido
def reducir_ruido(imagen):
    return cv2.GaussianBlur(imagen, (5, 5), 0)

# Umbralización binaria para mejorar el contraste
def umbralizar_imagen(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, umbralizada = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return umbralizada

# Preprocesar la imagen para mejorar la precisión de OCR
def preprocesar_imagen(imagen):
    # Mejorar el contraste sin convertir la imagen a escala de grises
    imagen_contraste = aumentar_contraste(imagen)
    
    # Suavizar la imagen para reducir el ruido
    imagen_suavizada = reducir_ruido(imagen_contraste)
    
    # Umbralización binaria para hacer el texto más claro
    imagen_binaria = umbralizar_imagen(imagen_suavizada)
    
    return imagen_binaria

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Asegurarse de que la cámara está abierta correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
    exit()

def capturar_imagen():
    print("Presiona 'c' para capturar una imagen y 'q' para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar una imagen.")
            break
        
        cv2.imshow('Captura de imagen', frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('c'):
            fecha_hora = datetime.now().strftime('%Y%m%d-%H%M%S')
            nombre_archivo = f"captura_{fecha_hora}.jpg"
            
            cv2.imwrite(nombre_archivo, frame)
            print(f"Imagen guardada como {nombre_archivo}")

            # Preprocesar la imagen antes de realizar OCR
            imagen_procesada = preprocesar_imagen(frame)

            # Intentar realizar OCR
            try:
                custom_config = r'--oem 3 --psm 6'  # Usar modo híbrido y segmentación de texto lineal
                texto = pytesseract.image_to_string(imagen_procesada, lang='spa', config=custom_config)
                
                if texto.strip():
                    print(f"Texto reconocido: {texto}")
                else:
                    print("No se reconoció texto en la imagen.")
                
                # Guardar el texto en un archivo
                with open('resultado.txt', 'w') as f:
                    f.write(texto)
                print("Texto guardado en resultado.txt")

            except Exception as e:
                print(f"Error al procesar la imagen: {e}")

        elif tecla == ord('q'):  # Salir si se presiona 'q'
            print("Saliendo...")
            break

    cap.release()
    cv2.destroyAllWindows()

capturar_imagen()
