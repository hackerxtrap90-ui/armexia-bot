import os
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]

openai = AsyncOpenAI(api_key=OPENAI_KEY)

historico = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou a Armex.ia.\n\n"
        "Pode me perguntar qualquer coisa!"
    )

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.effective_user.id
    mensagem = update.message.text

    if usuario not in historico:
        historico[usuario] = []

    historico[usuario].append({
        "role": "user",
        "content": mensagem
    })

    historico[usuario] = historico[usuario][-20:]

    try:
        resposta = await openai.responses.create(
            model="gpt-6-luna",
            instructions=(
                "Você é a Armex.ia, uma assistente de inteligência artificial. "
                "Responda em português do Brasil de forma clara, amigável e útil."
            ),
            input=historico[usuario]
        )

        texto = resposta.output_text

        historico[usuario].append({
            "role": "assistant",
            "content": texto
        })

        await update.message.reply_text(texto)

    except Exception as erro:
        print("Erro:", erro)
        await update.message.reply_text(
            "Desculpe, aconteceu um erro. Tente novamente."
        )

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("Armex.ia está funcionando!")

app.run_polling()
