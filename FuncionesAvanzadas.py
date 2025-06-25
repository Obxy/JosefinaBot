import re
import random
import discord

# Formato: j!roll 2d6+1d8+3 adv x4
async def comando_roll_profesional(message):
    contenido = message.content[len("j!roll"):].strip()

    # Parsear opciones especiales
    repetir = 1
    ventaja = None

    # Buscar ventaja/desventaja
    if " adv" in contenido:
        ventaja = "adv"
        contenido = contenido.replace(" adv", "").strip()
    elif " dis" in contenido:
        ventaja = "dis"
        contenido = contenido.replace(" dis", "").strip()

    # Buscar repetición (xN)
    rep_match = re.search(r"x(\d+)$", contenido)
    if rep_match:
        repetir = int(rep_match.group(1))
        contenido = contenido[:rep_match.start()].strip()

    resultados = []

    for _ in range(repetir):
        total, detalle, valor_clave = procesar_formula_dados(contenido, ventaja)
        resultados.append((total, detalle, valor_clave))

    # Crear embed para responder
    embed = discord.Embed(title="Prefijo: rollme ✅", description="", color=0x00ff90)
    for total, detalle, clave in resultados:
        embed.description += f"**{total}** ← **[{clave}]** {detalle}\n"

    await message.channel.send(embed=embed)

def procesar_formula_dados(formula, ventaja=None):
    partes = re.split(r'(\+|\-)', formula)
    total = 0
    valores_detalle = []
    detalle = ""

    operador = 1  # 1 para suma, -1 para resta
    for parte in partes:
        parte = parte.strip()
        if parte == "+":
            operador = 1
            continue
        elif parte == "-":
            operador = -1
            continue

        dado_match = re.match(r"(\d*)d(\d+)(dl1)?", parte)
        if dado_match:
            cantidad = int(dado_match.group(1)) if dado_match.group(1) else 1
            caras = int(dado_match.group(2))
            drop_lowest = bool(dado_match.group(3))
            tiradas = [random.randint(1, caras) for _ in range(cantidad)]

            if ventaja:
                extra = [random.randint(1, caras) for _ in range(cantidad)]
                combinadas = list(zip(tiradas, extra))
                seleccionadas = [max(pair) if ventaja == "adv" else min(pair) for pair in combinadas]
                valor = sum(seleccionadas)
                valores_detalle.append(valor)
                detalle += f"[{', '.join(str(v) for v in seleccionadas)}] {parte} "
            elif drop_lowest and len(tiradas) > 1:
                tiradas_ordenadas = sorted(tiradas)
                descartada = tiradas_ordenadas[0]
                mantenidas = tiradas_ordenadas[1:]
                valor = sum(mantenidas)
                valores_detalle.append(valor)
                representacion = ', '.join(f"~{v}" if v == descartada else str(v) for v in tiradas)
                detalle += f"[{representacion}] {parte} "
            else:
                valor = sum(tiradas)
                valores_detalle.append(valor)
                detalle += f"[{', '.join(str(v) for v in tiradas)}] {parte} "

            total += operador * valor

        elif parte.isdigit():
            num = int(parte)
            total += operador * num
            valores_detalle.append(num)
            detalle += f"+{num} " if operador == 1 else f"-{num} "

    clave = " + ".join([str(v) for v in valores_detalle])
    return total, detalle.strip(), clave
