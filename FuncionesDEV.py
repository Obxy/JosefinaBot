import sqlite3
import discord
from datetime import datetime, timedelta

DB_PATH = 'josefina.db'
DEV_ID = 743531557863817237

# Comando: listar combates
async def listar_combates_para_dev(user: discord.User):
    if user.id != DEV_ID:
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, fecha_inicio FROM Combates")
        filas = cursor.fetchall()

    if not filas:
        await user.send("No hay combates en la base de datos.")
        return

    mensaje = "**Lista de Combates:**\n"
    for nombre, fecha in filas:
        mensaje += f"- {nombre} | iniciado el {fecha}\n"

    await user.send(mensaje)


# Comando: borrar todos los combates
async def borrar_todos_los_combates(user: discord.User):
    if user.id != DEV_ID:
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Iniciativas")
        cursor.execute("DELETE FROM Combates")
        conn.commit()

    await user.send("🗑️ Todos los combates y sus iniciativas han sido eliminados.")


# Comando: borrar combates con más de 2 meses
async def borrar_combates_viejos(user: discord.User):
    if user.id != DEV_ID:
        return

    hace_dos_meses = datetime.utcnow() - timedelta(days=60)
    fecha_limite = hace_dos_meses.isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Obtener combates antiguos
        cursor.execute("SELECT id FROM Combates WHERE fecha_inicio < ?", (fecha_limite,))
        ids = [fila[0] for fila in cursor.fetchall()]

        if not ids:
            await user.send("✅ No hay combates con más de dos meses.")
            return

        for combate_id in ids:
            cursor.execute("DELETE FROM Iniciativas WHERE combate_id = ?", (combate_id,))
            cursor.execute("DELETE FROM Combates WHERE id = ?", (combate_id,))

        conn.commit()

    await user.send(f"🧹 Se eliminaron {len(ids)} combates con más de dos meses de antigüedad.")


async def borrar_combate_por_nombre(user: discord.User, nombre_buscado: str):
    if user.id != DEV_ID:
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Combates WHERE LOWER(nombre) = ?", (nombre_buscado.lower(),))
        row = cursor.fetchone()

        if not row:
            await user.send(f"❌ No encontré ningún combate llamado **{nombre_buscado}**.")
            return

        combate_id = row[0]
        cursor.execute("DELETE FROM Iniciativas WHERE combate_id = ?", (combate_id,))
        cursor.execute("DELETE FROM Combates WHERE id = ?", (combate_id,))
        conn.commit()

    await user.send(f"🗑️ El combate **{nombre_buscado}** y sus iniciativas fueron eliminados.")
