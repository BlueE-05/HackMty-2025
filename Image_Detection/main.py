# Import necessary libraries
from dotenv import load_dotenv
import os

import google.genai as genai
import PIL.Image
import io
import requests
from enum import Enum

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Definimos las categorías de clasificación
class FillLevel(Enum):
    EMPTY = "0%"
    TEN_PERCENT = "10%"
    TWENTY_PERCENT = "20%"
    THIRTY_PERCENT = "30%"
    FORTY_PERCENT = "40%"
    FIFTY_PERCENT = "50%"
    SIXTY_PERCENT = "60%"
    SEVENTY_PERCENT = "70%"
    EIGHTY_PERCENT = "80%"
    NINETY_PERCENT = "90%"
    FULL = "100%"

# Prompt de sistema especializado
SYSTEM_PROMPT = """
Eres un sistema especializado en analizar el nivel de llenado de botellas.
Tu tarea es clasificar la imagen en una de estas categorías exactas:
- 0% (Vacío)
- 10% (Casi vacío)
- 20% 
- 30%
- 40%
- 50% (Mitad)
- 60%
- 70%
- 80%
- 90% (Casi lleno)
- 100% (Completamente lleno)

Consideraciones importantes:
- Analiza la altura del líquido respecto a la altura total de la botella
- Ignora el cuello de la botella si es muy estrecho
- Considera el menisco (curvatura del líquido)
- Para líquidos espumosos, considera el nivel del líquido, no la espuma

Responde ÚNICAMENTE con el porcentaje exacto (ej: "60%") sin texto adicional.
"""

def classify_bottle_fill_level(image_path, bottle_size_ml=None):
    """
    Clasifica el nivel de llenado de una botella
    
    Args:
        image_path: Ruta a la imagen o URL
        bottle_size_ml: Tamaño de la botella en ml (opcional)
    
    Returns:
        dict: Información del nivel de llenado
    """
    
    # Cargar la imagen
    try:
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = PIL.Image.open(io.BytesIO(response.content))
        else:
            image = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"Error cargando imagen: {str(e)}"}
    
    # Inicializar el modelo
    
    # Preparar el prompt con información de tamaño si está disponible
    prompt = SYSTEM_PROMPT
    if bottle_size_ml:
        prompt += f"\n\nInformación adicional: La botella tiene una capacidad de {bottle_size_ml} ml."
    
    try:
        # Realizar la clasificación
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [prompt, image]
        )
        
        response_text = response.text.strip()
        
        # Extraer el porcentaje de la respuesta
        percentage = extract_percentage_from_response(response_text)
        
        # Calcular volumen si se proporcionó el tamaño
        volume_ml = None
        if bottle_size_ml and percentage is not None:
            volume_ml = (percentage / 100) * bottle_size_ml
        
        return {
            "fill_percentage": percentage,
            "fill_level_category": get_fill_level_category(percentage),
            "volume_ml": volume_ml,
            "bottle_size_ml": bottle_size_ml,
            "raw_response": response_text
        }
        
    except Exception as e:
        return {"error": f"Error en la clasificación: {str(e)}"}

def extract_percentage_from_response(response_text):
    """Extrae el porcentaje numérico de la respuesta del modelo"""
    try:
        # Buscar patrones como "60%" o "60 %"
        import re
        match = re.search(r'(\d+)%', response_text)
        if match:
            percentage = int(match.group(1))
            # Asegurarse que esté en el rango 0-100
            return max(0, min(100, percentage))
        return None
    except:
        return None

def get_fill_level_category(percentage):
    """Convierte el porcentaje a categoría descriptiva"""
    if percentage is None:
        return "Unknown"
    
    categories = {
        (0, 5): "Empty",
        (6, 15): "Very Low",
        (16, 35): "Low", 
        (36, 65): "Medium",
        (66, 85): "High",
        (86, 100): "Full"
    }
    
    for range_, category in categories.items():
        if range_[0] <= percentage <= range_[1]:
            return category
    return "Unknown"


if __name__ == "__main__":
    result1 = classify_bottle_fill_level(
    image_path="Botella_Prueba.jpg",
    bottle_size_ml=500
    )

    print(f"Resultado de la clasificación: \n{result1}")

    print(f"Porcentaje de llenado: {result1['fill_percentage']}%")
    print(f"Categoría: {result1['fill_level_category']}")
    print(f"Volumen estimado: {result1['volume_ml']} ml")