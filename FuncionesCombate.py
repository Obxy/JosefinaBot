import discord
import random
import sqlite3
from datetime import datetime
from FuncionesDados import calcular_iniciativa

DB_PATH = 'josefina.db'

# Iniciar combate
async def iniciar_combate(message, client):
    partes = message.content.split("llamado", 1)
    nombre_combate = partes[1].strip() if len(partes) == 2 else f"Combate {random.randint(1000, 9999)}"

    respuesta = await message.channel.send(
        f"Entendido, tomo iniciativas para **{nombre_combate}** (responde con `j!me sumo a [nombre del combate] con X` o `j!sumo N *enemigo* a [nombre del combate] con X`).")

    # Guardar en base de datos
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Combates (nombre, servidor_id, canal_id, iniciado_por_id, fecha_inicio)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nombre_combate,
            str(message.guild.id) if message.guild else None,
            str(message.channel.id),
            str(message.author.id),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
    await respuesta.add_reaction("👍")


# Registrar iniciativa
async def registrar_iniciativa(message: discord.Message):
    contenido = message.content.strip().lower()

    try:
        if contenido.startswith("j!me sumo a"):
            partes = contenido.split("j!me sumo a", 1)[1].strip().split("con", 1)
            if len(partes) != 2:
                raise ValueError("Formato inválido. Usa: j!me sumo a [nombre del combate] con [valor]")

            nombre_combate = partes[0].strip()
            raw = partes[1].strip()

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM Combates WHERE LOWER(nombre) = ?", (nombre_combate.lower(),))
                result = cursor.fetchone()
                if not result:
                    await message.channel.send(f"❌ No encontré un combate llamado **{nombre_combate}**.")
                    return True
                combate_id = result[0]

                nombre = message.author.display_name
                valor, detalle = calcular_iniciativa(raw)
                cursor.execute("""
                    INSERT INTO Iniciativas (combate_id, nombre_combatiente, iniciativa, usuario_id)
                    VALUES (?, ?, ?, ?)
                """, (combate_id, nombre, valor, str(message.author.id)))
                conn.commit()
            await message.channel.send(f"📌 {nombre} entra al combate. {detalle}")
            await message.add_reaction("✅")

        elif contenido.startswith("j!sumo"):
            partes = contenido[7:].split("a", 1)
            if len(partes) != 2:
                raise ValueError("Formato inválido. Usa: j!sumo N [enemigo] a [nombre del combate] con [valor]")

            nombre_parte = partes[0].strip()
            resto = partes[1].strip()
            if "con" not in resto:
                raise ValueError("Falta 'con' en el comando. Usa: j!sumo N [enemigo] a [nombre del combate] con [valor]")

            nombre_combate, raw = map(str.strip, resto.split("con", 1))

            split_nombre = nombre_parte.split()
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM Combates WHERE LOWER(nombre) = ?", (nombre_combate.lower(),))
                result = cursor.fetchone()
                if not result:
                    await message.channel.send(f"❌ No encontré un combate llamado **{nombre_combate}**.")
                    return True
                combate_id = result[0]

                if split_nombre[0].isdigit():
                    cantidad = int(split_nombre[0])
                    nombre_base = " ".join(split_nombre[1:])
                    if nombre_base.endswith("s") and not nombre_base.endswith("ss"):
                        nombre_base = nombre_base[:-1]
                    for i in range(1, cantidad + 1):
                        nombre = f"{nombre_base} {i}"
                        valor, detalle = calcular_iniciativa(raw)
                        cursor.execute("""
                            INSERT INTO Iniciativas (combate_id, nombre_combatiente, iniciativa)
                            VALUES (?, ?, ?)
                        """, (combate_id, nombre, valor))
                        await message.channel.send(f"📌 {nombre} entra al combate. {detalle}")
                    await message.add_reaction("⚔️")
                else:
                    nombre = nombre_parte
                    valor, detalle = calcular_iniciativa(raw)
                    cursor.execute("""
                        INSERT INTO Iniciativas (combate_id, nombre_combatiente, iniciativa)
                        VALUES (?, ?, ?)
                    """, (combate_id, nombre, valor))
                    await message.channel.send(f"📌 {nombre} entra al combate. {detalle}")
                    await message.add_reaction("⚔️")
                conn.commit()

        else:
            return False

    except Exception as e:
        await message.channel.send(f"❌ No pude procesar la iniciativa. Revisa el formato. Error: `{str(e)}`")
    return True

# Mostrar iniciativa
async def mostrar_iniciativa(message):
    contenido = message.content.strip()
    combate_id = None

    if "del combate" in contenido.lower():
        partes = contenido.lower().split("del combate")
        if len(partes) >= 2:
            nombre_buscado = partes[1].strip().lower()
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM Combates WHERE LOWER(nombre) = ?", (nombre_buscado,))
                row = cursor.fetchone()
                if row:
                    combate_id = row[0]
                else:
                    await message.channel.send(f"❌ No encontré un combate llamado **{nombre_buscado}**.")
                    return
    else:
        await message.channel.send("❌ Usa `orden del combate [nombre]` para ver la iniciativa.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre_combatiente, iniciativa FROM Iniciativas
            WHERE combate_id = ?
            ORDER BY iniciativa DESC
        """, (combate_id,))
        filas = cursor.fetchall()

    if not filas:
        await message.channel.send("⚠️ Ese combate no tiene participantes.")
        return

    texto = "**📜 Orden de Iniciativa:**\n"
    for nombre, valor in filas:
        texto += f"- {nombre}: {valor}\n"

    await message.channel.send(texto)
