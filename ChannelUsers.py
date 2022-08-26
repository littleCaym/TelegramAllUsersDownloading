import configparser
import json
from time import sleep
import xlsxwriter
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors import FloodWaitError, MultiError
from telethon.tl.types import (
    PeerChannel
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config-sample.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    # me = await client.get_me()

    user_input_channel = input("enter entity(telegram URL or entity id):")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    all_participants = []

    it = client.iter_participants(my_channel, aggressive=True)
    while True:
        try:
            participant = await it.__anext__()
            all_participants.append(participant)
            print(len(all_participants))
        except (FloodWaitError, MultiError):
            print('Wait...')
            sleep(35)  
        except StopAsyncIteration:
            break

    all_user_details = []
    all_user_details_toTxt = []
    all_user_details_toExcel = []
    for participant in all_participants:
        all_user_details.append(
            {"id": participant.id, "first_name": participant.first_name, "last_name": participant.last_name,
             "user": participant.username, "phone": participant.phone, "is_bot": participant.bot})

        all_user_details_toExcel.append([participant.id, participant.first_name, participant.last_name,
            participant.username, participant.phone, participant.bot])

    with open('user_data.json', 'w') as file:
        json.dump(all_user_details, file)

    workbook = xlsxwriter.Workbook('user_data.xlsx')
    worksheet = workbook.add_worksheet("Users")
    row = 0
    col = 0

    worksheet.write(row, col, 'id')
    worksheet.write(row, col + 1, 'first_name')
    worksheet.write(row, col + 2, 'last_name')
    worksheet.write(row, col + 3, 'username')
    worksheet.write(row, col + 4, 'phone')
    worksheet.write(row, col + 5, 'bot')
    row += 1

    for id, first_name, last_name, username, phone, bot in (all_user_details_toExcel):
        worksheet.write(row, col, id)
        worksheet.write(row, col + 1, first_name)
        worksheet.write(row, col + 2, last_name)
        worksheet.write(row, col + 3, username)
        worksheet.write(row, col + 4, phone)
        worksheet.write(row, col + 5, bot)
        row += 1
    workbook.close()
with client:
    client.loop.run_until_complete(main(phone))

# https://t.me/hillelmos