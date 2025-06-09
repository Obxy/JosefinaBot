
import re
import random


async def lanzar_dados(texto):
    patron = r"^j!lanzame\s+([^\s]+)(?:\s+con\s+(ventaja|desventaja))?(?:\s+(\d+)\s+veces)?$"
    m = re.match(patron, texto.strip(), re.IGNORECASE)
    if not m:
        return (
            "Oops, no entendí bien. Porfa probá con algo como:\n"
            "'j!lanzame 2d6+1d4+3 con ventaja 2 veces'"
        )

    expr = m.group(1).replace(" ", "")
    modo = m.group(2)  # ventaja / desventaja / None
    repeticiones = int(m.group(3)) if m.group(3) else 1

    # Parsear términos como "2d6", "1d4", "+3"
    terminos = re.findall(r'([+-]?\d*d\d+|[+-]?\d+)', expr)
    if not terminos:
        return "No encontré dados ni números en la expresión. Revisa el formato."

    def tirar_term():
        total = 0
        detalles = []
        for term in terminos:
            if 'd' in term:
                signo = 1
                if term.startswith('-'):
                    signo = -1
                    term = term[1:]
                elif term.startswith('+'):
                    term = term[1:]

                x, y = term.split('d')
                x = int(x) if x else 1
                y = int(y)

                dados = [random.randint(1, y) for _ in range(x)]
                suma = sum(dados) * signo
                dados_str = ', '.join(str(d) for d in dados)
                desc = f"{signo * x}d{y} me dio **{dados_str}**"
                if signo * suma != suma:
                    desc += f" (aplicando signo {signo})"
                detalles.append((suma, desc))
                total += suma
            else:
                val = int(term)
                total += val
                detalles.append((val, f"con el... {val:+}"))
        return total, detalles

    resultados = []
    suma_acumulada = 0

    for i in range(1, repeticiones + 1):
        if modo:  # ventaja o desventaja
            t1_total, t1_det = tirar_term()
            t2_total, t2_det = tirar_term()
            if modo.lower() == "ventaja":
                elegido = (t1_total, t1_det) if t1_total >= t2_total else (t2_total, t2_det)
            else:
                elegido = (t1_total, t1_det) if t1_total <= t2_total else (t2_total, t2_det)

            suma_acumulada += elegido[0]
            t1_texto = ' '.join(d for _, d in t1_det)
            t2_texto = ' '.join(d for _, d in t2_det)
            if i>1:
                resultados.append(
                    f"🎲 Tirada {i} con {modo}:\n"
                    f" ❤ Primero... {t1_texto} eso es... {t1_total}\n"
                    f" ❤ Segundo... {t2_texto} eso es... {t2_total}\n"
                    f"  Te quedás con el **{elegido[0]}** jiji"
                )
            else:
                resultados.append(
                    f"❤ Primero... {t1_texto} eso es... {t1_total}\n"
                    f"❤ Segundo... {t2_texto} eso es... {t2_total}\n"
                    f"Te quedás con el **{elegido[0]}** jiji"
                )
        else:
            total, detalles = tirar_term()
            suma_acumulada += total
            texto = ' + '.join(desc for _, desc in detalles)
            resultados.append(f"Tirada {i}: {texto} eso es... {total}")

    respuesta = "\n\n".join(resultados)
    respuesta += f"\n\nTotal acumulado: **{suma_acumulada}** Suerte!"

    return respuesta

def calcular_iniciativa(texto: str) -> tuple[int, str]:
    texto = texto.strip().lower()

    # Caso: solo un número (iniciativa fija)
    if re.fullmatch(r"\d+", texto):
        valor = int(texto)
        return valor, f"📟 Iniciativa fija: **{valor}**"

    # Caso: tirada tipo 1d20+3
    match = re.match(r"(\d*)d(\d+)([+-]\d+)?", texto)
    if not match:
        raise ValueError("Formato de iniciativa inválido")

    num_dados = int(match.group(1) or 1)
    caras = int(match.group(2))
    modificador = int(match.group(3) or 0)

    tiradas = [random.randint(1, caras) for _ in range(num_dados)]
    total = sum(tiradas) + modificador

    detalle = (
        f"🎲 Tiraste {num_dados}d{caras}"
        f"{f'{modificador:+}' if modificador else ''}: {tiradas} → total: **{total}**"
    )

    return total, detalle



def generar_estadisticas():
    resultados = []
    for _ in range(6):
        dados = [random.randint(1, 6) for _ in range(4)]
        dados.remove(min(dados))
        total = sum(dados)
        resultados.append(total)
    return resultados


async def comando_generar_estadisticas(message):
    stats =generar_estadisticas()
    await message.channel.send(f"🎲 Estadísticas generadas: {', '.join(map(str, stats))}\n"
                               "Puedes asignarlas como quieras.")
