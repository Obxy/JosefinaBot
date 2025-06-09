import requests
from googletrans import Translator

translator = Translator()
def corregir_traduccion(texto):
    reemplazos = {
        "propenso": "derribado",
        "propensa": "derribada",
        "**Propenso**": "**Derribado**",
        "rollos": "tiradas",
        "lista de ataque": "tirada de ataque",
        "gatear": "arrastrarse",
        "inconsciente '": "inconsciente`",
        "deaf": "deafened",
        "blunt": "blinded",
        "enchanted": "charmed",
        "exhausted": "exhaustion",
        "scared": "frightened",
        "luchado": "apresado",
        "arrested": "grappled",
        "GRAPPLED": "Apresado",
        "disabled": "incapacitated",
        "felled": "prone",
        "restricted": "restrained",
        "Contenido": "Restringido",
        "poisonous": "poisoned",
        "Charmer":"encantador"
    }
    for original, corregido in reemplazos.items():
        texto = texto.replace(original, corregido)
    return texto



async def BusquedaCondicion(message):
    parts = message.content.split()
    status = parts[-1].lower()
  
    traduccionSTATUS= await translator.translate(status, dest='en')
    traduccionSTATUSCORR=corregir_traduccion(traduccionSTATUS.text)
    #print(traduccionSTATUSCORR) AYUDA POSIBLE
    url = f"https://www.dnd5eapi.co/api/conditions/{traduccionSTATUSCORR}"
    #print(url) AYUDA POSIBLE
  
  
    payload = {}
    headers = {
    'Accept': 'application/json'
    }
  
  
    response = requests.request("GET", url, headers=headers, data=payload)
  
  
    #print(response.status_code) AYUDA POSIBLE
    if response.status_code == 200:
        data = response.json()
        name = data.get("name", "Sin condicion.")
        desc = "\n".join(data.get("desc", ["Sin descripcion."]))
        texto=str((f"**{name}**\n{desc}"))
  
        traduccion= await translator.translate(texto, dest='es')
        traduccion = corregir_traduccion(traduccion.text)
  
        return(traduccion)
    else:
        return("❌ Condicion No Encontrada.")

async def comandos():
    with open("ListaComandos.txt", "r", encoding="utf-8") as file:
        comandos = file.read()
    return comandos