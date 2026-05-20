import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

crm_fake = {
    "Acindar": {
        "razon_social": "Acindar S.A.",
        "cuit": "30-50001234-5",
        "ultimo_pedido": "200 chapas galvanizadas - $1.500.000",
        "fecha_ultimo_pedido": "2026-05-15",
        "estado": "cliente_activo"
    },
    "Tenaris": {
        "razon_social": "Tenaris S.A.",
        "cuit": "30-50009876-1",
        "ultimo_pedido": "Caños sin costura - $3.200.000",
        "fecha_ultimo_pedido": "2026-04-22",
        "estado": "cliente_inactivo"
    },
}

def buscar_cliente_en_crm(nombre_empresa:str) -> dict:
    """Busca un cliente en el CRM por nombre de empresa."""
    print(f"  → [Tool] Buscando '{nombre_empresa}' en CRM...")

    for key, cliente in crm_fake.items():
        if nombre_empresa.lower() in key.lower():
            print(f"  → [Tool] Encontrado: {cliente['razon_social']}")
            return cliente
    print(f"  → [Tool] No encontrado.")
    return {"error": "Cliente no encontrado en CRM"}

buscar_cliente_tool = {
      "name": "buscar_cliente_en_crm",
        "description": (
        "Busca un cliente en el CRM por nombre de empresa. "
        "Útil cuando recibimos un email y queremos saber si quien escribe "
        "es un cliente existente, qué historial tiene, y su último pedido."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "nombre_empresa": {
                "type": "string",
                "description": "Nombre de la empresa a buscar en el CRM"
            }
        },
        "required": ["nombre_empresa"]
    }
}
email = """
Asunto: Consulta por presupuesto

Hola, soy Juan de Acindar. Necesitamos cotización urgente 
de 200 chapas galvanizadas calibre 22, medidas 1.22 x 2.44m. 
Necesitamos entrega en planta Villa Constitución antes del 
fin de mes.

Saludos,
Juan Pérez
Acindar S.A.
"""

prompt = f"Analizá este email y, si es de un cliente potencial o existente, buscalo en el CRM:\n\n{email}"

print("=" * 60)
print("PASO 1: Modelo analiza el email y decide qué hacer")
print("=" * 60)

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=[buscar_cliente_tool])]
    )
)

candidate = response.candidates[0]
function_call = None

for part in candidate.content.parts:
    if hasattr(part, 'function_call') and part.function_call is not None:
        function_call = part.function_call
        break

if function_call:
    print(f"\n  → Modelo decidió llamar a: {function_call.name}")
    print(f"  → Con argumentos: {dict(function_call.args)}")

    # === PASO 2: Tu código ejecuta la tool ===
    print("\n" + "=" * 60)
    print("PASO 2: Ejecutamos la tool")
    print("=" * 60)

    resultado_crm = buscar_cliente_en_crm(**dict(function_call.args))

    # === PASO 3: Modelo genera respuesta final con el resultado ===
    print("\n" + "=" * 60)
    print("PASO 3: Modelo genera respuesta final usando datos del CRM")
    print("=" * 60)

    response_final = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            prompt,
            candidate.content,
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": resultado_crm}
                )]
            )
        ],
        config=types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=[buscar_cliente_tool])]
        )
    )

    print(f"\n{response_final.text}")
else:
    print("\n  → El modelo no usó ninguna tool.")
    print(f"\n  Respuesta directa: {response.text}")