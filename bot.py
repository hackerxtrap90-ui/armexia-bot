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
        historico[usuario] = [
            {
                "role": "system",
                "content": "Você é a Armex.ia, uma assistente de inteligência artificial. Responda em português do Brasil de forma clara, amigável e útil."
            }
        ]

    historico[usuario].append({"role": "user", "content": mensagem})
    
    # Mantém a instrução do sistema + as últimas 20 mensagens
    historico[usuario] = [historico[usuario][0]] + historico[usuario][-20:]

    try:
        resposta = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=historico[usuario]
        )
        
        texto = resposta.choices[0].message.content
        
        historico[usuario].append({"role": "assistant", "content": texto})
        
        await update.message.reply_text(texto)
        
    except Exception as erro:
        print("Erro no servidor:", erro)
        await update.message.reply_text(
            "Desculpe, aconteceu um erro ao processar sua mensagem. Tente novamente."
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("Armex.ia está rodando no Railway!")
    app.run_polling()
