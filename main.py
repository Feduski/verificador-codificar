import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from pymongo import MongoClient

load_dotenv() #loading the telegram key from the env file
TELEGRAM_KEY = os.getenv('TELEGRAM_KEY') #key del bot
URL = os.getenv('URL') #url de la db

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) #basic log config

async def start_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola!\nSoy el bot asistente del equipo de CodificarDev. Mi tarea es indicar cuales son los cursos que ya fueron enviados previamente al grupo, para que no se comentan guardados repetidos.\nPodés probar mi funcionalidad reenviando el curso, gracias! :) ")
    logging.info(f'El usuario: ({update.message.chat.first_name}) ejecutó: start_command.')

async def echo(update: Update, context: CallbackContext) -> None:
    unique_file_id = update.message.document.file_unique_id
    
    files_ids = check_db()

    if unique_file_id in files_ids:
        await update.message.reply_text("Ya habían enviado este archivo anteriormente.\nPor favor, intentá con otro!")
        return
    else:
        data = {
            "file_id": unique_file_id,
            "caption": update.message.caption
        }
        
        save_data(data)
        await update.message.reply_text("Archivo recibido, gracias! :)")

    
def save_data(data : dict) -> None: #guardo en mongodb 
    #guardo en formato json el diccionario que me enviaron
    client = MongoClient(URL)
    data_base = client['cursos_codificar_database']

    collection = data_base['cursos_collection']

    collection.insert_one(data)
    print('Guardado')
    print(f'Se guardó {collection.find_one(data)}')

def check_db():
    #de acá recibo de mongodb los datos y los convierto en un array que luego retorno
    files_ids = [] 
    client = MongoClient(URL)
    data_base = client['cursos_codificar_database']
    collection = data_base['cursos_collection']
    for document in collection.find():
        files_ids.append(document['file_id'])
    print(files_ids)

    return files_ids

def main():
    application = Application.builder().token(TELEGRAM_KEY).build()
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(MessageHandler(~filters.COMMAND, echo)) #permitimos que lea todos los mensajes, aunque no sean comandos
    application.run_polling()

if __name__ == '__main__':
    main()
