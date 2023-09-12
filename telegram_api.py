import asyncio
from telethon import TelegramClient, events
from fastapi import FastAPI
from uvicorn import run
import logging
import colorlog
from pydantic import BaseModel
import os
from dotenv import load_dotenv


import odoorpc

# Load the environment variables from the .env file
load_dotenv()

# Access the environment variables
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DB = os.getenv('DB')
USER = os.getenv('ODOO_USER')
PWD = os.getenv('PSWD')

#odoo = odoorpc.ODOO(HOST, port=PORT)
print(f'========= MY INFO: {HOST}, {PORT}, {USER}, {DB}, {PWD}')


# SETTING A LOGGER
# Create a colorized formatter
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(reset)s %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# Create a logger and set the formatter
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class TelegramApi:

    instances = []

    def __init__(self, phone_number, api_id, api_hash, session_name, system_version="4.16.30-vxCUSTOM"):
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        TelegramApi.instances.append(self)
        #self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, system_version="4.16.30-vxCUSTOM")

    # async def connect(self):
    #     self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, system_version="4.16.30-vxCUSTOM")
    #     try:
    #         print(f'-------CLASS----- self.client.is_user_authorized = {await self.client.is_user_authorized()}')
    #     except Exception as e:
    #         print(f'-------CLASS____ YOU ARE NOT CONNECTED')
    #     await self.client.start()


    async def disconnect(self):
        await self.disconnect()

    async def send_new_message(self, recipient, message):
        await self.send_message(recipient, message)
#        await self.disconnect()

    async def get_me(self):
        me = await self.client.get_me()
        return me

telegram_api = None

# This class represents a structure of auth data to use within post requests
class TelegramAuth(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str
    session_name: str
    message_text: str
    recipient: int


app = FastAPI()
logging.basicConfig(level=logging.INFO)



# CHECK CONNECTION
@app.post("/check_auth")
async def check_auth(auth: TelegramAuth): 
    global telegram_api
    try:
        telegram_api = TelegramApi(auth.phone_number, auth.api_id, auth.api_hash, auth.session_name)
        telegram_api.client = TelegramClient(auth.session_name, auth.api_id, auth.api_hash, system_version="4.16.30-vxCUSTOM")
        auth_status = telegram_api.client.is_connected()
        await telegram_api.client.connect()
        auth_status = telegram_api.client.is_connected()
        auth_status = await telegram_api.client.is_user_authorized()
        return {'auth_status': auth_status}
    except Exception as e:
        auth_status = False
        print(f'----4--- {auth_status}')
        return {'auth_status': auth_status}



# GET INFO ABOUT MY TG ACCOUNT
@app.post("/get_my_tg")
async def check_connection(auth: TelegramAuth): #expect data as defined in TelegramAuth class
    global telegram_api
    if telegram_api is None:
        telegram_api = TelegramApi(auth.phone_number, auth.api_id, auth.api_hash, auth.session_name)
        await telegram_api.connect()
    # Check if a current connection is established
    if not telegram_api.client.is_connected():
        print(f'========= MY INFO: TELEGRAM API IS NOT CONNECTED, TRYING TO CONNECT')
        await telegram_api.connect()
        print(f'========= MY INFO: TELEGRAM API IS CONNECTED')
    print(f'========= TRYING TO CONNECT: {telegram_api}')
    me = await telegram_api.get_me()
    return {"username": me.username}


# CREATE AND BROADCAST NEW CHANNEL
@app.get("/create_channel")
def create_broadcast_new_channel(telegram_message_data):
    try:
        odoo = odoorpc.ODOO(HOST, port=PORT)
        odoo.login(DB, USER, PWD)
        if not telegram_message_data['chat_username']:
            print(f'========= MY INFO: chat_username is NONE. Trying to replace with Replaced with chat_dialog_id')
            telegram_message_data['chat_username'] = telegram_message_data['chat_dialog_id']
        channel_data = {
                'name': f"{telegram_message_data['chat_username']} (Telegram)",
                'is_telegram': True,
                'telegram_dialog_id': telegram_message_data['chat_dialog_id'],
                'channel_type': 'channel',
                }
        print(f'========= MY INFO: TRYING TO CREATE NEW CHANNEL WITH DATA: {channel_data}')
        new_channel_id = odoo.env['mail.channel'].channel_create_broadcast(channel_data)
        print(f'========= MY INFO: NEW CHANNEL CREATED {new_channel_id}, type: {type(new_channel_id)}')
        return new_channel_id
    
    except Exception as e:
        # Handle the exception or log the error message
        print(f"Error creating mail.channel: {e}")


# SEND A NEW MESSAGE (OUTGOING)
@app.post("/send_new_message")
async def send_new_message(auth: TelegramAuth): #expect data as defined in TelegramAuth class
    global telegram_api
    if telegram_api is None:
        print(f'========= MY INFO: telegram_api is NONE = {telegram_api}')
        return {'telegram_api': telegram_api}
    print(f'========= MY INFO: telegram_api = {telegram_api}')

    ###############
    # Check if a current connection is established
    if not telegram_api.is_connected():
        print(f'========= MY INFO: TELEGRAM API IS NOT CONNECTED, TRYING TO CONNECT')
        await telegram_api.connect()
        print(f'========= MY INFO: TELEGRAM API IS CONNECTED')

    # Check if the connection is successful
    if telegram_api.is_connected():
        print(f'========= MY INFO: TELEGRAM API IS ALREADY CONNECTED')
    else:
        print("Failed to connect to Telegram")
    ###################
    print(f'========= MY INFO: TRYING TO SEND TG MESSAGE auth.recipient = {auth.recipient}')
    print(f'========= MY INFO: TRYING TO SEND TG MESSAGE auth.message = {auth.message_text}')
    recipient = auth.recipient # in Odoo this is a 'mail.channel' - 'telegram_dialog_id'
    message = auth.message_text# in Odoo this is a 'mail.message' - 'body'
    print(f'========= MY INFO: TRYING TO SEND TG MESSAGE message = {message}')
    await telegram_api.send_message(recipient, message)
    print(f'========= MY INFO: MESSAGE SENT message = {message}')
    return {'send_message': 'message sent', 'telegram_api': True}



# CREATE A NEW ODOO MESSAGE (INCOMING)
@app.get("/create_new_message")
async def create_new_odoo_message(telegram_message_data):
    # Check if a message has telegra_dialog_id in Odoo
    try:
        print(f'========= MY INFO: {HOST}, {PORT}, {USER}, {DB}, {PWD}')
        odoo = odoorpc.ODOO(HOST, port=PORT)
        odoo.login(DB, USER, PWD)
        channel_id = odoo.env['mail.channel'].search([('telegram_dialog_id', '=', telegram_message_data['chat_dialog_id'])])
        print(f'========= MY INFO: {channel_id}')
    except Exception as e:
        # Handle the exception or log the error message
        print(f"Error creating mail.channel: {e}")

    # Check if mail.channel with this ID exist
    if channel_id:
        channel = odoo.env['mail.channel'].browse(channel_id) # get channel instanse if it exist in Odoo
        print(f'========= MY INFO: CHANNEL FOUND: {channel}')
        channel.ensure_one()
    # Create new channel if no Telegram ID found in Odoo 'mail.channel'
    else:
        print(f'========= MY INFO: NO CHANNEL FOUND IN ODOO. TRYING TO CREATE WITH create_new_channel()')
        channel_id = create_broadcast_new_channel(telegram_message_data) # create and get channel instanse
        #channel_id = create_new_channel(telegram_message_data)
        print(f'========= MY INFO: return channel_id {channel_id}')
        channel = odoo.env['mail.channel'].browse(int(channel_id))
        print(f'========= MY INFO: channel {channel}')
        channel.ensure_one()

    # Ensure channel is exist
    if channel:

        # Check if author is exist in Odoo and create new res.partner if not
        odoo.login(DB, USER, PWD)
        author = odoo.env['res.partner'].search([('telegram_id', '=', telegram_message_data['chat_dialog_id'])])
        print(f'========= MY INFO: author =  {author}')
        try:
            author_id = author[0]
            print(f'========= MY INFO: author_id =  {author_id}')
        except:
            author_id = False

        if not author_id:
            author_id = 2
            print(f'========= MY INFO: NO RES.PARTNER FOUND')

        print(f'========= MY INFO: telegram_message_data["chat_dialog_id"] = {telegram_message_data["chat_dialog_id"]}')
        partner_id = odoo.env['res.partner'].search([('telegram_id', '=', telegram_message_data['chat_dialog_id'])])
        print(f'========= MY INFO: "res.partner" partner_id = {partner_id}')
        partner = odoo.env['res.partner'].browse(partner_id)
        print(f'========= MY INFO: "res.partner" partner = {partner}')

        print(f'========= MY INFO: TRYING TO POST MESSAGE with "channel.message_post()" in channel {channel}')
        channel.message_post(body=telegram_message_data['raw_text'],
                             message_type='telegram',
                             author_id=author_id,
                             telegram_message_id=telegram_message_data['message_id'],
                             channel_id=channel.id)

        print(f'========= MY INFO: MESSAGE HAS BEEN POSTED. text: {telegram_message_data["raw_text"]},\
               telegram_message_id: {telegram_message_data["message_id"]}')
    return {'new_message': telegram_message_data}

handler_started = False

# START EVENT LOOP
@app.post("/start_event_loop")
async def check_connection(auth: TelegramAuth): #expect data as defined in TelegramAuth class
    global telegram_api
    global handler_started
    print(f'=====1==== MY INFO: telegram_api = {telegram_api}')
    if telegram_api is None:
        return {'start_loop': 'telegram_api_none'}
        # telegram_api = TelegramApi(auth.phone_number, auth.api_id, auth.api_hash, auth.session_name)
        # print(f'=====2==== MY INFO: telegram_api = {telegram_api}')
        # await telegram_api.connect()
        # print(f'=====3==== after await connect')
   
    
    # LISTEN FOR INCOMING MESSAGES
    @telegram_api.on(events.NewMessage(outgoing=False))
    async def readMessages(event):
    # first we get the user information
        print(f'========= /start_event_loop: INSIDE EVENT LOOP')
        user = await telegram_api.get_entity(event.sender_id) #get an instance of a sender of a message
        print(f'========= /start_event_loop: user = await telegram_api.client.get_entity(event.sender_id) = {user}')
        logger.info('NEW EVENT')
        id = user.id
        print(f'========= id = user.id: {id}')
        username = user.username

        # INFO ABOUT CHAT/USER YOU ARE TALKING IN TELEGRAM
        chat = await event.get_chat() # Get chat info (equivvalent to dialog)
        telegram_dialog_id = chat.id # The Id of the telegram user (or equivalent of the chat id)
        chat_username = chat.username
        telegram_message_data = {'chat_dialog_id': chat.id,
                                 'chat_username': chat.username,
                                 'chat_first_name': chat.first_name,
                                 'chat_last_name': chat.last_name,
                                 'chat_phone': chat.phone,
                                 'raw_text': event.raw_text,
                                 'message_id': event.id}
        
        #info_string = f'Telegram dialog ID: {telegram_dialog_id}, chat_user: {chat_username},\
       #                 chat_phone: {chat_phone}, text: {event.raw_text}'
        logger.info(f'----------telegram_message_data------------{telegram_message_data}')
        print(f'----------telegram_message_data------------{telegram_message_data}')
        print(f'=========={telegram_dialog_id}============')
        print(f'User Id: {user.id} - Username: {user.username} - Text: {event.raw_text} - chat: {chat}')

        # POST MESSAGE IN ODOO
        try:
            await create_new_odoo_message(telegram_message_data)
        except:
            logger.error(f'--- await create_new_odoo_message(telegram_message_data) returned with an error')

    # LAUNCH A LOOP
    start_success = False
    if handler_started:
        print(f'========= MY INFO: handler_started {handler_started}')
        print(f'========= MY INFO:  "Handler already started"')
        return {"Loop_start": "Handler already started", "auth_status": True}
    else:
        try:
            telegram_api.start()
            telegram_api.run_until_disconnected()
            start_success = True
            handler_started = True
            print(f"======= INFO: telegram_api.client started ===========")
        except Exception as e:
            print(f"=======Failed to start telegram_api.client: {e}===========")

        if start_success:
            return {"Loop_start": "OK", "auth_status": True}
        else:
            return {"Loop_start": "Failed", "auth_status": False}


# FIRST AUTHENTICATION 
# Get SMS code
@app.post("/sms_code_request")
async def sms_code_request(session_name, api_id, api_hash, phone_number):
    global telegram_api
    telegram_api = None
    print(f'====INSTANCES (request): {TelegramApi.instances}')
    telegram_api = TelegramClient(session_name, api_id, api_hash, system_version="4.16.30-vxCUSTOM")
        # Check if the client is connected, and connect if it's not
    if not telegram_api.is_connected():
        print(f'=====(/sms_code_request):  client is not connected')
        await telegram_api.connect()
    result = await telegram_api.send_code_request(phone_number)
    phone_hash = result.phone_code_hash
    print(phone_hash)
    #await client.disconnect()  # Disconnect the client
    return {'phone_hash': phone_hash}


#Send code to auth
@app.post("/send_code")
async def verify_sms_code(session_name, api_id, api_hash, phone_number, sms_code, phone_hash):
    print(f"======= INFO[send_code()]: POST REQUEST RECIEVED")
    print(f'====INSTANCES (code): {TelegramApi.instances}')
    global telegram_api
    #telegram_api = TelegramClient(session_name, api_id, api_hash, system_version="4.16.30-vxCUSTOM")
    #await telegram_api.connect()
    await telegram_api.sign_in(phone_number, code=sms_code, phone_code_hash=phone_hash)
    me = await telegram_api.get_me()
    print(f"======= INFO[send_code()]: me.username = {me.username}")
    #await client.disconnect()  # Disconnect the client
    return {"username": me.username}


if __name__ == "__main__":
    uvicorn_app = "telegram_api:app"
    run(uvicorn_app, host='0.0.0.0', port=8000, reload=True, log_level="debug")