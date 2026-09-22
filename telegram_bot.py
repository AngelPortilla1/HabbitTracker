import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
)

from storage import cargar_usuarios, guardar_usuarios
from models import Usuario


# Cargamos las variables del archivo .env al iniciar
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Cargamos los usuarios al iniciar el bot
# Se mantiene en memoria mientras el bot esta corriendo
usuarios = cargar_usuarios()


# ============================================================
# Funcion auxiliar para reducir codigo repetido
# ============================================================

def _verificar_usuario(update):
    """
    Verifica que el usuario haya hecho /start.
    Retorna el usuario si existe, None si no.
    """
    user_id = str(update.effective_user.id)
    return usuarios.get(user_id)


# ============================================================
# Handlers de comandos
# ============================================================

async def start(update, context):
    """Comando /start - registra al usuario."""
    user_id = str(update.effective_user.id)
    nombre = update.effective_user.first_name

    if user_id not in usuarios:
        usuarios[user_id] = Usuario(user_id=user_id, nombre=nombre)
        guardar_usuarios(usuarios)
        mensaje = "Hola " + nombre + "! Te registre en mi base de datos."
    else:
        mensaje = "Hola de nuevo " + nombre + "!"

    await update.message.reply_text(mensaje)


async def agregar(update, context):
    """Comando /agregar <nombre> - agrega un habito nuevo."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not context.args:
        await update.message.reply_text("Uso: /agregar <nombre del habito>")
        return

    nombre = " ".join(context.args)

    try:
        usuario.agregar_habito(nombre)
        guardar_usuarios(usuarios)
        await update.message.reply_text(
            "Listo. Habito '" + nombre.lower() + "' agregado"
        )
    except ValueError as error:
        await update.message.reply_text("Aviso: " + str(error))


async def marcar(update, context):
    """Comando /marcar <nombre> - marca un habito como hecho hoy."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not context.args:
        await update.message.reply_text("Uso: /marcar <nombre>")
        return

    nombre = " ".join(context.args)

    try:
        mensaje = usuario.check(nombre)
        guardar_usuarios(usuarios)
        await update.message.reply_text(mensaje)
    except KeyError as error:
        await update.message.reply_text("Aviso: " + str(error))


async def hoy(update, context):
    """Comando /hoy - muestra el estado de hoy."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not usuario.habitos:
        await update.message.reply_text("No tienes habitos registrados.")
        return

    lineas = ["Habitos de hoy:"]
    for nombre, habito in usuario.habitos.items():
        if habito.hecho_hoy():
            estado = "[X]"
        else:
            estado = "[ ]"
        lineas.append("  " + estado + " " + nombre)

    await update.message.reply_text("\n".join(lineas))


async def streaks(update, context):
    """Comando /streaks - muestra las rachas actuales."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not usuario.habitos:
        await update.message.reply_text("No tienes habitos registrados.")
        return

    lineas = ["Streaks actuales:"]
    for nombre, habito in usuario.habitos.items():
        lineas.append("  " + nombre + ": " + str(habito.streak()) + " dias")

    await update.message.reply_text("\n".join(lineas))


async def listar(update, context):
    """Comando /listar - lista todos los habitos con detalle."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not usuario.habitos:
        await update.message.reply_text("No tienes habitos registrados.")
        return

    lineas = ["Todos tus habitos:"]
    for nombre, habito in usuario.habitos.items():
        total = len(habito.checks)
        lineas.append(
            "  - " + nombre +
            " (creado: " + habito.creado + ", " +
            "total checks: " + str(total) + ")"
        )

    await update.message.reply_text("\n".join(lineas))


async def eliminar(update, context):
    """Comando /eliminar <nombre> - elimina un habito."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not context.args:
        await update.message.reply_text("Uso: /eliminar <nombre>")
        return

    nombre = " ".join(context.args)

    if usuario.eliminar_habito(nombre):
        guardar_usuarios(usuarios)
        await update.message.reply_text(
            "Listo. Habito '" + nombre.lower() + "' eliminado"
        )
    else:
        await update.message.reply_text("Aviso: no se encontro ese habito")


async def stats(update, context):
    """Comando /stats - muestra estadísticas de los habitos."""
    usuario = _verificar_usuario(update)
    if usuario is None:
        await update.message.reply_text("Usa /start primero")
        return

    if not usuario.habitos:
        await update.message.reply_text("No tienes habitos registrados.")
        return

    total_habitos = len(usuario.habitos)
    total_checks = sum(len(habito.checks) for habito in usuario.habitos.values())
    rachas_totales = sum(habito.streak() for habito in usuario.habitos.values())
    mejor_racha = max((habito.streak() for habito in usuario.habitos.values()), default=0)

    mensaje = (
        "Estadísticas:\n"
        f"  - Total de habitos: {total_habitos}\n"
        f"  - Total de checks: {total_checks}\n"
        f"  - Rachas totales: {rachas_totales}\n"
        f"  - Mejor racha: {mejor_racha} dias"
    )
    await update.message.reply_text(mensaje)


async def help_command(update, context):
    """Comando /help - muestra los comandos disponibles."""
    mensaje = (
        "Comandos disponibles:\n"
        "/start - registrarse\n"
        "/agregar <nombre> - agregar un habito\n"
        "/marcar <nombre> - marcar como hecho hoy\n"
        "/hoy - ver estado de hoy\n"
        "/streaks - ver rachas actuales\n"
        "/listar - listar todos los habitos\n"
        "/eliminar <nombre> - eliminar un habito\n"
        "/help - mostrar esta ayuda"
    )
    await update.message.reply_text(mensaje)


# ============================================================
# Funcion principal
# ============================================================

def main():
    """Inicia el bot."""
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN no esta configurado en .env")
        return

    app = Application.builder().token(TOKEN).build()

    # Registramos los handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("marcar", marcar))
    app.add_handler(CommandHandler("hoy", hoy))
    app.add_handler(CommandHandler("streaks", streaks))
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("eliminar", eliminar))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))

    print("Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()
