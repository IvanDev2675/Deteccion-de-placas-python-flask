import cv2
import pytesseract

# Configura la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def procesar_imagen(archivo_imagen):
    try:
        # Cargar la imagen
        image = cv2.imread(archivo_imagen)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Opcional: Aplicar threshold binario para aumentar el contraste
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Extraer texto usando Tesseract directamente
        texto_detectado = pytesseract.image_to_string(thresh, config='--psm 7').strip()

        # Mostrar la imagen de umbralización (si lo necesitas)
       # cv2.imshow('Imagen Procesada', thresh)
       # cv2.waitKey(0)
       # cv2.destroyAllWindows()

        return texto_detectado  # Devuelve el texto extraído
    except Exception as e:
        return f'Error al procesar la imagen: {str(e)}'
