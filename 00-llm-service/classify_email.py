import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

email = """
Asunto: hola

che, acordate de pasarme el archivo del otro día
nos vemos
"""
prompt = f"""Analizá el siguiente email y devolvé un JSON con esta estructura exacta:

{{
    "categoria": "prospecto" | "cliente_existente" | "spam" | "soporte" | "otro",
    "prioridad": "alta" | "media" | "baja",
    "razon": "explicación corta de por qué",
    "requiere_respuesta": true | false
}}

Email a analizar:
{email}

Devolvé SOLO el JSON, sin texto adicional, sin markdown.
"""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
    ),
)
result = json.loads(response.text)

print("=== Clasificación del email ===")
print(f"Categoría: {result['categoria']}")
print(f"Prioridad: {result['prioridad']}")
print(f"Requiere respuesta: {result['requiere_respuesta']}")
print(f"Razón: {result['razon']}")
print()
print("=== JSON crudo ===")
print(json.dumps(result, indent=2, ensure_ascii=False))
