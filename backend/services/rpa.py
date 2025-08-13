# =====================================
# Componentes RPA Avanzados para Agentiqware
# =====================================

import asyncio
import base64
import io
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Computer Vision y OCR
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Automatización
import pyautogui
import pygetwindow as gw
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

# Machine Learning
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import tensorflow as tf

# Web Automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

# PDF Processing
import PyPDF2
import pdfplumber

# Email Automation
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# API Integration
import requests
from google.cloud import vision
from google.cloud import documentai_v1 as documentai

# =====================================
# OCR y Procesamiento de Documentos
# =====================================

class DocumentProcessor:
    """Procesador avanzado de documentos con OCR y AI"""
    
    def __init__(self):
        self.vision_client = vision.ImageAnnotatorClient()
        self.doc_ai_client = documentai.DocumentProcessorServiceClient()
        self.tesseract_config = r'--oem 3 --psm 6'
        
    async def extract_text_from_image(
        self,
        image_path: str,
        language: str = 'eng',
        enhance: bool = True
    ) -> Dict[str, Any]:
        """
        Extraer texto de una imagen usando OCR
        
        Args:
            image_path: Ruta de la imagen
            language: Idioma del texto (eng, spa, fra, etc.)
            enhance: Si mejorar la imagen antes del OCR
        
        Returns:
            Texto extraído y metadatos
        """
        # Cargar imagen
        image = cv2.imread(image_path)
        
        if enhance:
            # Mejorar imagen para mejor OCR
            image = self._enhance_image_for_ocr(image)
        
        # OCR con Tesseract
        text = pytesseract.image_to_string(
            image,
            lang=language,
            config=self.tesseract_config
        )
        
        # Obtener datos detallados
        data = pytesseract.image_to_data(
            image,
            lang=language,
            output_type=pytesseract.Output.DICT
        )
        
        # Procesar resultados
        words = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:
                words.append({
                    'text': data['text'][i],
                    'confidence': data['conf'][i],
                    'bbox': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                })
        
        return {
            'full_text': text,
            'words': words,
            'language': language,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def extract_from_pdf(
        self,
        pdf_path: str,
        extract_tables: bool = True,
        extract_images: bool = False
    ) -> Dict[str, Any]:
        """
        Extraer contenido de un PDF
        
        Args:
            pdf_path: Ruta del PDF
            extract_tables: Si extraer tablas
            extract_images: Si extraer imágenes
        
        Returns:
            Contenido extraído del PDF
        """
        results = {
            'text': [],
            'tables': [],
            'images': [],
            'metadata': {}
        }
        
        # Extraer texto con pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Metadatos
            results['metadata'] = {
                'pages': len(pdf.pages),
                'author': pdf.metadata.get('Author', ''),
                'title': pdf.metadata.get('Title', ''),
                'subject': pdf.metadata.get('Subject', ''),
                'creation_date': str(pdf.metadata.get('CreationDate', ''))
            }
            
            # Procesar cada página
            for page_num, page in enumerate(pdf.pages):
                # Extraer texto
                page_text = page.extract_text()
                if page_text:
                    results['text'].append({
                        'page': page_num + 1,
                        'content': page_text
                    })
                
                # Extraer tablas
                if extract_tables:
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        results['tables'].append({
                            'page': page_num + 1,
                            'table_index': table_idx,
                            'data': table
                        })
                
                # Extraer imágenes
                if extract_images and hasattr(page, 'images'):
                    for img_idx, img in enumerate(page.images):
                        results['images'].append({
                            'page': page_num + 1,
                            'image_index': img_idx,
                            'bbox': img['bbox']
                        })
        
        return results
    
    async def extract_structured_data(
        self,
        document_path: str,
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extraer datos estructurados usando plantilla
        
        Args:
            document_path: Ruta del documento
            template: Plantilla con campos a extraer
        
        Returns:
            Datos estructurados extraídos
        """
        # Usar Google Document AI para extracción avanzada
        with open(document_path, 'rb') as f:
            content = f.read()
        
        # Configurar solicitud
        document = documentai.Document(
            content=content,
            mime_type='application/pdf'
        )
        
        # Procesar documento
        # Aquí se usaría un procesador entrenado específico
        
        extracted_data = {}
        
        for field_name, field_config in template.items():
            field_type = field_config.get('type', 'text')
            
            if field_type == 'text':
                # Buscar texto con regex o keywords
                extracted_data[field_name] = self._extract_text_field(
                    document,
                    field_config
                )
            elif field_type == 'date':
                # Extraer fecha
                extracted_data[field_name] = self._extract_date_field(
                    document,
                    field_config
                )
            elif field_type == 'amount':
                # Extraer cantidad/monto
                extracted_data[field_name] = self._extract_amount_field(
                    document,
                    field_config
                )
            elif field_type == 'table':
                # Extraer tabla
                extracted_data[field_name] = self._extract_table_field(
                    document,
                    field_config
                )
        
        return extracted_data
    
    def _enhance_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Mejorar imagen para OCR"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Eliminar ruido
        denoised = cv2.medianBlur(thresh, 3)
        
        # Ajustar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def _extract_text_field(self, document: Any, config: Dict) -> str:
        """Extraer campo de texto"""
        # Implementación específica
        return ""
    
    def _extract_date_field(self, document: Any, config: Dict) -> str:
        """Extraer campo de fecha"""
        # Implementación específica
        return ""
    
    def _extract_amount_field(self, document: Any, config: Dict) -> float:
        """Extraer campo de monto"""
        # Implementación específica
        return 0.0
    
    def _extract_table_field(self, document: Any, config: Dict) -> List:
        """Extraer tabla"""
        # Implementación específica
        return []

# =====================================
# Computer Vision y Detección de UI
# =====================================

class UIElementDetector:
    """Detector de elementos UI usando Computer Vision"""
    
    def __init__(self):
        self.templates = {}
        self.load_ui_templates()
        
    def load_ui_templates(self):
        """Cargar plantillas de elementos UI comunes"""
        template_dir = "ui_templates"
        if os.path.exists(template_dir):
            for template_file in os.listdir(template_dir):
                if template_file.endswith(('.png', '.jpg')):
                    name = os.path.splitext(template_file)[0]
                    path = os.path.join(template_dir, template_file)
                    self.templates[name] = cv2.imread(path)
    
    async def find_element(
        self,
        element_type: str,
        screenshot: Optional[np.ndarray] = None,
        confidence: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        Encontrar elemento UI en la pantalla
        
        Args:
            element_type: Tipo de elemento (button, input, checkbox, etc.)
            screenshot: Captura de pantalla (opcional)
            confidence: Nivel de confianza mínimo
        
        Returns:
            Información del elemento encontrado
        """
        if screenshot is None:
            # Capturar pantalla
            screenshot = np.array(pyautogui.screenshot())
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # Buscar elemento según tipo
        if element_type == 'button':
            return await self._find_button(screenshot, confidence)
        elif element_type == 'input':
            return await self._find_input_field(screenshot, confidence)
        elif element_type == 'checkbox':
            return await self._find_checkbox(screenshot, confidence)
        elif element_type == 'dropdown':
            return await self._find_dropdown(screenshot, confidence)
        else:
            # Búsqueda genérica por plantilla
            if element_type in self.templates:
                return await self._find_by_template(
                    screenshot,
                    self.templates[element_type],
                    confidence
                )
        
        return None
    
    async def _find_button(
        self,
        screenshot: np.ndarray,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Encontrar botón en la pantalla"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detectar bordes
        edges = cv2.Canny(gray, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        buttons = []
        
        for contour in contours:
            # Obtener rectángulo delimitador
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filtrar por proporciones típicas de botón
            aspect_ratio = w / h if h > 0 else 0
            if 1.5 < aspect_ratio < 6 and 20 < h < 100:
                # Verificar si parece un botón
                roi = screenshot[y:y+h, x:x+w]
                if self._looks_like_button(roi):
                    buttons.append({
                        'type': 'button',
                        'position': {'x': x + w//2, 'y': y + h//2},
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': self._calculate_button_confidence(roi)
                    })
        
        # Retornar el botón con mayor confianza
        if buttons:
            return max(buttons, key=lambda b: b['confidence'])
        
        return None
    
    async def _find_input_field(
        self,
        screenshot: np.ndarray,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Encontrar campo de entrada"""
        # Buscar rectángulos con características de input
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Encontrar líneas horizontales
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(
            horizontal_lines,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        inputs = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Verificar proporciones de input field
            if w > 100 and 20 < h < 60:
                inputs.append({
                    'type': 'input',
                    'position': {'x': x + w//2, 'y': y + h//2},
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 0.7
                })
        
        return inputs[0] if inputs else None
    
    async def _find_checkbox(
        self,
        screenshot: np.ndarray,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Encontrar checkbox"""
        # Buscar cuadrados pequeños
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detectar cuadrados
        squares = self._detect_squares(gray, min_size=10, max_size=30)
        
        checkboxes = []
        
        for square in squares:
            x, y, w, h = square
            roi = screenshot[y:y+h, x:x+w]
            
            # Verificar si está marcado
            is_checked = self._is_checkbox_checked(roi)
            
            checkboxes.append({
                'type': 'checkbox',
                'position': {'x': x + w//2, 'y': y + h//2},
                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                'checked': is_checked,
                'confidence': 0.8
            })
        
        return checkboxes[0] if checkboxes else None
    
    async def _find_dropdown(
        self,
        screenshot: np.ndarray,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Encontrar dropdown/combobox"""
        # Buscar elemento con flecha hacia abajo
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Template matching para flecha de dropdown
        if 'dropdown_arrow' in self.templates:
            result = cv2.matchTemplate(
                gray,
                self.templates['dropdown_arrow'],
                cv2.TM_CCOEFF_NORMED
            )
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = self.templates['dropdown_arrow'].shape[:2]
                return {
                    'type': 'dropdown',
                    'position': {
                        'x': max_loc[0] + w//2,
                        'y': max_loc[1] + h//2
                    },
                    'bbox': {
                        'x': max_loc[0],
                        'y': max_loc[1],
                        'width': w,
                        'height': h
                    },
                    'confidence': max_val
                }
        
        return None
    
    async def _find_by_template(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Buscar elemento por plantilla"""
        # Template matching
        result = cv2.matchTemplate(
            screenshot,
            template,
            cv2.TM_CCOEFF_NORMED
        )
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            h, w = template.shape[:2]
            return {
                'type': 'template_match',
                'position': {
                    'x': max_loc[0] + w//2,
                    'y': max_loc[1] + h//2
                },
                'bbox': {
                    'x': max_loc[0],
                    'y': max_loc[1],
                    'width': w,
                    'height': h
                },
                'confidence': max_val
            }
        
        return None
    
    def _looks_like_button(self, roi: np.ndarray) -> bool:
        """Verificar si una región parece un botón"""
        # Análisis simple basado en características visuales
        # Verificar si tiene texto
        has_text = self._contains_text(roi)
        
        # Verificar si tiene bordes definidos
        has_borders = self._has_defined_borders(roi)
        
        # Verificar colores consistentes
        has_consistent_color = self._has_consistent_color(roi)
        
        return has_text or (has_borders and has_consistent_color)
    
    def _calculate_button_confidence(self, roi: np.ndarray) -> float:
        """Calcular confianza de que sea un botón"""
        confidence = 0.5
        
        if self._contains_text(roi):
            confidence += 0.2
        
        if self._has_defined_borders(roi):
            confidence += 0.15
        
        if self._has_consistent_color(roi):
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _detect_squares(
        self,
        image: np.ndarray,
        min_size: int,
        max_size: int
    ) -> List[Tuple[int, int, int, int]]:
        """Detectar cuadrados en la imagen"""
        squares = []
        
        # Detectar contornos
        contours, _ = cv2.findContours(
            image,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            # Aproximar contorno
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Verificar si es cuadrado (4 vértices)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                
                # Verificar tamaño y proporciones
                if min_size < w < max_size and min_size < h < max_size:
                    aspect_ratio = w / h
                    if 0.8 < aspect_ratio < 1.2:  # Casi cuadrado
                        squares.append((x, y, w, h))
        
        return squares
    
    def _is_checkbox_checked(self, roi: np.ndarray) -> bool:
        """Verificar si un checkbox está marcado"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Calcular cantidad de píxeles oscuros en el centro
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        
        # Si hay muchos píxeles oscuros en el centro, está marcado
        dark_pixels = np.sum(center_region < 128)
        total_pixels = center_region.size
        
        return (dark_pixels / total_pixels) > 0.3
    
    def _contains_text(self, roi: np.ndarray) -> bool:
        """Verificar si la región contiene texto"""
        try:
            text = pytesseract.image_to_string(roi).strip()
            return len(text) > 0
        except:
            return False
    
    def _has_defined_borders(self, roi: np.ndarray) -> bool:
        """Verificar si tiene bordes definidos"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Contar píxeles de borde
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        
        return (edge_pixels / total_pixels) > 0.05
    
    def _has_consistent_color(self, roi: np.ndarray) -> bool:
        """Verificar si tiene color consistente"""
        # Calcular desviación estándar del color
        std_dev = np.std(roi)
        
        # Si la desviación es baja, el color es consistente
        return std_dev < 50

# =====================================
# Automatización Web Avanzada
# =====================================

class WebAutomation:
    """Automatización web avanzada con Selenium"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.wait = None
        
    async def initialize(self):
        """Inicializar navegador"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    async def navigate_to(self, url: str):
        """Navegar a URL"""
        self.driver.get(url)
        await asyncio.sleep(1)  # Esperar carga inicial
    
    async def find_and_click(
        self,
        selector: str,
        selector_type: str = "css"
    ) -> bool:
        """
        Encontrar y hacer clic en elemento
        
        Args:
            selector: Selector del elemento
            selector_type: Tipo de selector (css, xpath, id, name, etc.)
        
        Returns:
            True si se hizo clic exitosamente
        """
        try:
            by_type = self._get_by_type(selector_type)
            element = self.wait.until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            return True
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False
    
    async def fill_form(
        self,
        form_data: Dict[str, Any]
    ) -> bool:
        """
        Llenar formulario
        
        Args:
            form_data: Diccionario con selector -> valor
        
        Returns:
            True si se llenó exitosamente
        """
        try:
            for selector, value in form_data.items():
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Limpiar campo primero
                element.clear()
                
                # Enviar valor
                element.send_keys(str(value))
                
                # Pequeña pausa entre campos
                await asyncio.sleep(0.2)
            
            return True
        except Exception as e:
            print(f"Error filling form: {e}")
            return False
    
    async def extract_table_data(
        self,
        table_selector: str
    ) -> List[List[str]]:
        """
        Extraer datos de tabla
        
        Args:
            table_selector: Selector de la tabla
        
        Returns:
            Datos de la tabla como lista de listas
        """
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, table_selector)
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:  # Podría ser header
                    cells = row.find_elements(By.TAG_NAME, "th")
                
                row_data = [cell.text for cell in cells]
                if row_data:
                    data.append(row_data)
            
            return data
        except Exception as e:
            print(f"Error extracting table: {e}")
            return []
    
    async def wait_for_element(
        self,
        selector: str,
        timeout: int = 10
    ) -> bool:
        """Esperar a que aparezca un elemento"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except:
            return False
    
    async def take_screenshot(
        self,
        filename: str
    ) -> str:
        """Tomar captura de pantalla"""
        self.driver.save_screenshot(filename)
        return filename
    
    async def execute_javascript(
        self,
        script: str
    ) -> Any:
        """Ejecutar JavaScript"""
        return self.driver.execute_script(script)
    
    async def close(self):
        """Cerrar navegador"""
        if self.driver:
            self.driver.quit()
    
    def _get_by_type(self, selector_type: str):
        """Obtener tipo de selector de Selenium"""
        types = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'link': By.LINK_TEXT,
            'partial_link': By.PARTIAL_LINK_TEXT
        }
        return types.get(selector_type, By.CSS_SELECTOR)

# =====================================
# Automatización de Aplicaciones Desktop
# =====================================

class DesktopAutomation:
    """Automatización de aplicaciones desktop"""
    
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    async def open_application(
        self,
        app_name: str,
        wait_time: int = 3
    ) -> bool:
        """
        Abrir aplicación
        
        Args:
            app_name: Nombre de la aplicación
            wait_time: Tiempo de espera después de abrir
        
        Returns:
            True si se abrió exitosamente
        """
        try:
            # Windows
            if os.name == 'nt':
                os.system(f'start {app_name}')
            # macOS
            elif os.name == 'posix':
                os.system(f'open -a "{app_name}"')
            # Linux
            else:
                os.system(f'{app_name} &')
            
            await asyncio.sleep(wait_time)
            return True
        except Exception as e:
            print(f"Error opening application: {e}")
            return False
    
    async def find_and_click_image(
        self,
        image_path: str,
        confidence: float = 0.8,
        timeout: int = 10
    ) -> bool:
        """
        Buscar imagen en pantalla y hacer clic
        
        Args:
            image_path: Ruta de la imagen a buscar
            confidence: Nivel de confianza
            timeout: Tiempo máximo de espera
        
        Returns:
            True si se encontró y se hizo clic
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateCenterOnScreen(
                    image_path,
                    confidence=confidence
                )
                
                if location:
                    pyautogui.click(location)
                    return True
            except:
                pass
            
            await asyncio.sleep(0.5)
        
        return False
    
    async def type_text(
        self,
        text: str,
        interval: float = 0.05
    ):
        """Escribir texto"""
        pyautogui.typewrite(text, interval=interval)
    
    async def press_key(
        self,
        key: str,
        modifier: Optional[str] = None
    ):
        """
        Presionar tecla o combinación
        
        Args:
            key: Tecla a presionar
            modifier: Modificador (ctrl, alt, shift, cmd)
        """
        if modifier:
            pyautogui.hotkey(modifier, key)
        else:
            pyautogui.press(key)
    
    async def drag_and_drop(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 1.0
    ):
        """Arrastrar y soltar"""
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration)
    
    async def get_window_info(
        self,
        window_title: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener información de ventana
        
        Args:
            window_title: Título de la ventana
        
        Returns:
            Información de la ventana
        """
        try:
            windows = gw.getWindowsWithTitle(window_title)
            
            if windows:
                window = windows[0]
                return {
                    'title': window.title,
                    'position': {'x': window.left, 'y': window.top},
                    'size': {'width': window.width, 'height': window.height},
                    'is_active': window.isActive,
                    'is_minimized': window.isMinimized,
                    'is_maximized': window.isMaximized
                }
        except:
            pass
        
        return None
    
    async def focus_window(
        self,
        window_title: str
    ) -> bool:
        """Enfocar ventana"""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            
            if windows:
                window = windows[0]
                window.activate()
                return True
        except:
            pass
        
        return False
    
    async def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """Capturar región de pantalla"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return np.array(screenshot)

# =====================================
# Orquestador de RPA
# =====================================

class RPAOrchestrator:
    """Orquestador principal de procesos RPA"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.ui_detector = UIElementDetector()
        self.web_automation = None
        self.desktop_automation = DesktopAutomation()
        self.execution_log = []
    
    async def execute_workflow(
        self,
        workflow: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Ejecutar flujo de trabajo RPA
        
        Args:
            workflow: Lista de pasos del flujo
        
        Returns:
            Resultado de la ejecución
        """
        results = {
            'status': 'started',
            'steps_completed': 0,
            'total_steps': len(workflow),
            'outputs': {},
            'errors': []
        }
        
        for step_index, step in enumerate(workflow):
            try:
                step_type = step.get('type')
                step_config = step.get('config', {})
                
                self._log(f"Executing step {step_index + 1}: {step_type}")
                
                if step_type == 'open_app':
                    await self.desktop_automation.open_application(
                        step_config.get('app_name')
                    )
                    
                elif step_type == 'web_navigate':
                    if not self.web_automation:
                        self.web_automation = WebAutomation()
                        await self.web_automation.initialize()
                    
                    await self.web_automation.navigate_to(
                        step_config.get('url')
                    )
                    
                elif step_type == 'find_and_click':
                    element = await self.ui_detector.find_element(
                        step_config.get('element_type')
                    )
                    
                    if element:
                        pyautogui.click(
                            element['position']['x'],
                            element['position']['y']
                        )
                        
                elif step_type == 'extract_text':
                    text_data = await self.document_processor.extract_text_from_image(
                        step_config.get('image_path')
                    )
                    results['outputs'][f'step_{step_index}'] = text_data
                    
                elif step_type == 'type_text':
                    await self.desktop_automation.type_text(
                        step_config.get('text')
                    )
                    
                elif step_type == 'wait':
                    await asyncio.sleep(step_config.get('seconds', 1))
                    
                elif step_type == 'conditional':
                    condition = step_config.get('condition')
                    if self._evaluate_condition(condition, results):
                        # Ejecutar rama verdadera
                        true_branch = step_config.get('true_branch', [])
                        branch_result = await self.execute_workflow(true_branch)
                        results['outputs'][f'branch_{step_index}'] = branch_result
                    else:
                        # Ejecutar rama falsa
                        false_branch = step_config.get('false_branch', [])
                        branch_result = await self.execute_workflow(false_branch)
                        results['outputs'][f'branch_{step_index}'] = branch_result
                
                results['steps_completed'] += 1
                self._log(f"Step {step_index + 1} completed successfully")
                
            except Exception as e:
                error_msg = f"Error in step {step_index + 1}: {str(e)}"
                self._log(error_msg, level='ERROR')
                results['errors'].append({
                    'step': step_index + 1,
                    'type': step_type,
                    'error': str(e)
                })
                
                # Decidir si continuar o abortar
                if step.get('critical', False):
                    results['status'] = 'failed'
                    break
        
        # Limpiar recursos
        if self.web_automation:
            await self.web_automation.close()
        
        if not results['errors']:
            results['status'] = 'completed'
        elif results['status'] != 'failed':
            results['status'] = 'completed_with_errors'
        
        return results
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluar condición"""
        # Implementación simple de evaluación
        # En producción, esto sería más robusto
        return True
    
    def _log(self, message: str, level: str = 'INFO'):
        """Registrar mensaje de log"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        }
        self.execution_log.append(log_entry)
        print(f"[{level}] {message}")