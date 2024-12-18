import logging
import asyncio
from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from env import ADMINS
from dispatcher import dp, bot
from aiogram.utils.exceptions import BotBlocked
from form import *  # Import form handlers
logging.basicConfig(level=logging.INFO)


CHANNELS = {
    'kanal_otiladi_gooooo': "Obuna-1",
    'kanal_sotiladi_goo': "Obuna-2"
}
ids = {}
user_data_file = "users.json"
def load_user_data():
    try:
        with open(user_data_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

user_data = load_user_data()
def save_user_data(data):
    with open(user_data_file, "w") as file:
        json.dump(data, file, indent=4)


def create_inline_keyboard():
    inline_keyboard = InlineKeyboardMarkup(row_width=1)  # One button per row
    button = InlineKeyboardButton(text="Bizning instagram📲", url="https://www.instagram.com/kinolar_olam1_24?igsh=eHJtZzg5enJsOXp4")
    inline_keyboard.add(button)
    return inline_keyboard





async def add_user_to_data(user_id, username, full_name):
    # Check if user is in left_users and remove them
    if str(user_id) in left_users_data:
        left_users_data.pop(str(user_id))
        save_left_user_data(left_users_data)  # Correctly save updated `left_users_data`
        logging.info(f"User {full_name} ({username}) returned to the bot.")
        await notify_admins(f"User {full_name or 'Unknown'} (@{username or 'No username'}) botga qaytdi🔙")
    # Add the user to active users if not already present
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "username": username,
            "full_name": full_name,
            "subscribed": True
        }
        save_user_data(user_data)  # Save updated active users
        await notify_admins(f"User {full_name or 'Unknown'} (@{username or 'No username'}) botga yangi qo'shildi➕")

# def remove_user_from_data(user_id):
#     if str(user_id) in user_data:
#         del user_data[str(user_id)]
#         save_user_data(user_data)
@dp.message_handler(Text(equals="Obunachilar👥", ignore_case=True))
async def send_to_all_users(message: types.Message):
    if message.from_user.id in ADMINS:
        active_users=len(user_data)
        left_user=len(left_users_data)
        inline_keyboard = InlineKeyboardMarkup(row_width=1)  # One button per row
        button1 = InlineKeyboardButton(text="Bloklaganlar🚫📃",callback_data="blocks")
        button2=InlineKeyboardButton(text="Aktiv userlar🕐",callback_data="actives")
        inline_keyboard.add(button1,button2)
        await message.reply(
            f"👥 *Obunachilar Statisikasi:*\n\n"
            f"📌 *Aktiv Userlar:* {active_users}\n"
            f"❌ *Blok qilgan yoki botni tark etganlar:* {left_user}",
            parse_mode="Markdown",reply_markup=inline_keyboard
        )
    else:
        pass

@dp.callback_query_handler(lambda c: c.data == "blocks")
async def show_blocks(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in ADMINS:
        text = "Hoziroq instagram sahifamizga obuna bo'ling va ajoyib kinolarni tomosha qiling😎"
        inline_keyboard = create_inline_keyboard()
        for user_id in user_data.keys():
            await safe_send_message(user_id, text, inline_keyboard)

        if not left_users_data:
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Blok qilgan foydalanuvchilar ro'yxati bo'sh📃",
                parse_mode="html"
            )
            return

            # Create the list of blocked users
        blocked_users_text = "\n".join(
            [
                f"👤 <a href='tg://user?id={user_id}'>{data['full_name']}</a> "
                f"(@{data['username'] or 'username yo‘q'})"
                for user_id, data in left_users_data.items()
            ]
        )

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"📃 Botni bloklagan foydalanuvchilar:\n\n{blocked_users_text}",
            parse_mode="html"
        )
    else:
        pass

@dp.callback_query_handler(lambda c: c.data == "actives")
async def show_actives(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in ADMINS:

        if not user_data:
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Aktiv userlar yo'q❌",
                parse_mode="html"
            )
            return

            # Create the list of blocked users
        active_users_text = "\n".join(
            [
                f"👤 <a href='tg://user?id={user_id}'>{data['full_name']}</a> "
                f"(@{data['username'] or 'username yo‘q'})"
                for user_id, data in user_data.items()
            ]
        )

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"📃 Aktiv foydalanuvchilar:\n\n{active_users_text}",
            parse_mode="html"
        )
    else:
        pass
async def periodic_subscription_check():
    while True:
        for user_id in list(user_data.keys()):  # Use a copy of keys to avoid modification issues
            user_id = int(user_id)
            still_subscribed = all(
                [await is_subscribed(user_id, channel) for channel in CHANNELS.keys()]
            )

            if not still_subscribed:
                user_data[str(user_id)]["subscribed"] = False
                save_user_data(user_data)
                await delete_user_movies(user_id)
                logging.info(f"User {user_id} is unsubscribed. Deleted their movies.")
            else:
                user_data[str(user_id)]["subscribed"] = True
                save_user_data(user_data)
        await asyncio.sleep(5)


async def is_subscribed(user_id: int, channel_username: str) -> bool:
    try:
        member = await bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Add user to JSON file
    await add_user_to_data(user_id, username, full_name)
    await check_sub(message)

async def delete_user_movies(user_id: int):
    if user_id in ids:
        for msg_id in ids[user_id]:
            try:
                await bot.delete_message(chat_id=user_id, message_id=msg_id)
                logging.info(f"Deleted movie message with ID {msg_id} for user {user_id}")
            except Exception as e:
                logging.warning(f"Failed to delete message {msg_id} for user {user_id}: {e}")
        del ids[user_id]
        unsubscribed_channels = []

        for channel, button_text in CHANNELS.items():
            if not await is_subscribed(user_id, channel):
                unsubscribed_channels.append(
                    InlineKeyboardButton(text=button_text, url=f"https://t.me/{channel}")
                )

        if unsubscribed_channels:
            unsubscribed_channels.append(
                InlineKeyboardButton(text="Tekshirish✅", callback_data="check_button")
            )

            keyboard = InlineKeyboardMarkup(row_width=1).add(*unsubscribed_channels)

            await bot.send_message(chat_id=user_id,
                                   text="Iltimos kanallarni tark etmang❗Qaytadan foydalanish uchun kerakli kanallarga obuna bo'ling:",
                                   reply_markup=keyboard
                                   )
async def check_sub(message: types.Message):
    user_id = message.from_user.id
    unsubscribed_channels = []

    for channel, button_text in CHANNELS.items():
        if not await is_subscribed(user_id, channel):
            unsubscribed_channels.append(
                InlineKeyboardButton(text=button_text, url=f"https://t.me/{channel}")
            )

    if unsubscribed_channels:
        unsubscribed_channels.append(
            InlineKeyboardButton(text="Tekshirish✅", callback_data="check_button")
        )

        keyboard = InlineKeyboardMarkup(row_width=1).add(*unsubscribed_channels)

        await message.reply(
            f"Salom {message.from_user.full_name}!\n"
            "Botni ishlatish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
    else:
        if user_id in ADMINS:
            button1 = KeyboardButton("Kino qo'shish🎬")
            button2 = KeyboardButton("Obunachilar👥")

            # Arrange buttons in a keyboard layout (row width of 2)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(button1, button2)
            await bot.send_message(chat_id=user_id,text=f"Salom admin {message.from_user.full_name}", reply_markup=keyboard)
        # Ask for the 4-digit movie code after subscription
        await message.reply(f"Marhamat {message.from_user.full_name} kerakli kino kodini yuboring🔢")

@dp.callback_query_handler(lambda c: c.data == "check_button")
async def handle_check_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id  # Correctly get the user's ID
    unsubscribed_channels = []

    # Check subscription for each required channel
    for channel, button_text in CHANNELS.items():
        if not await is_subscribed(user_id, channel):
            unsubscribed_channels.append(
                InlineKeyboardButton(text=button_text, url=f"https://t.me/{channel}")
            )

    if unsubscribed_channels:
        # Add the "Check Again" button
        unsubscribed_channels.append(
            InlineKeyboardButton(text="Tekshirish✅", callback_data="check_button")
        )

        # Create the keyboard with unsubscribed channel buttons
        keyboard = InlineKeyboardMarkup(row_width=1).add(*unsubscribed_channels)

        # Inform the user to subscribe
        await callback_query.message.reply(
            f"Iltmos {callback_query.from_user.full_name}!\n"
            "Botni ishlatish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
    else:
        # If the user is subscribed, ask for the 4-digit movie code
        if user_id in ADMINS:
            button1 = KeyboardButton("Kino qo'shish🎬")
            button2 = KeyboardButton("Obunachilar👥")

            # Arrange buttons in a keyboard layout (row width of 2)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(button1, button2)
            await bot.send_message(chat_id=user_id,text=f"Marhamat admin {callback_query.from_user.full_name}", reply_markup=keyboard)
        await callback_query.message.reply(
            f"Marhamat {callback_query.from_user.full_name} kerakli kino kodini yuboring🔢"
        )

    # Acknowledge the callback
    await bot.answer_callback_query(callback_query.id)






@dp.message_handler(lambda message: types.ContentType.TEXT)
async def get_movie(message: types.Message):
    user_id = message.from_user.id
    unsubscribed_channels = []

    for channel, button_text in CHANNELS.items():
        if not await is_subscribed(user_id, channel):
            unsubscribed_channels.append(
                InlineKeyboardButton(text=button_text, url=f"https://t.me/{channel}")
            )

    if unsubscribed_channels:
        unsubscribed_channels.append(
            InlineKeyboardButton(text="Tekshirish✅", callback_data="check_button")
        )

        keyboard = InlineKeyboardMarkup(row_width=1).add(*unsubscribed_channels)

        await message.reply(
            f"Iltimos {message.from_user.full_name}!\n"
            "Botni ishlatish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
    else:

        with open("movie_details.json", "r") as file:
            data = json.load(file)

            # Check if the movie code exists
            if message.text in data:
                code = data[message.text]['movie_id']
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Afsuski kod noto'g'ri yoki kino topilmadi☹️")
                return

            # Copy the movie to the user
            copied_message = await bot.copy_message(chat_id=message.from_user.id, from_chat_id='-1002257758230', message_id=code)

            # Add to the `ids` dictionary
            if message.from_user.id not in ids:
                ids[message.from_user.id] = []  # Create a list for this user if not already present

            ids[message.from_user.id].append(copied_message.message_id)  # Add the copied message ID to the list


            print(f"User {message.from_user.id} sent movie message ID {copied_message.message_id}")


LEFT_USERS_FILE = 'left_users.json'
def load_left_user_data():
    try:
        with open(LEFT_USERS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save left user data to the JSON file
def save_left_user_data(left_users_data):
    with open(LEFT_USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(left_users_data, file, indent=4, ensure_ascii=False)
left_users_data = load_left_user_data()


async def handle_bot_block(user_id: int):
    user_info = user_data.pop(user_id, None)
    if user_info:
        left_users_data[user_id] = {
            'username': user_info['username'],
            'full_name': user_info['full_name']
        }
        logging.info(f"User {user_info['full_name']} ({user_info['username']}) blocked the bot.")

        # Save the left user data to the JSON file
        save_left_user_data(left_users_data)

        # Optionally, save the updated active user data
        save_user_data(user_data)
async def safe_send_message(user_id: int, text: str, reply_markup: types.InlineKeyboardMarkup):
    try:
        await bot.send_message(user_id, text, reply_markup=reply_markup)
    except BotBlocked:
        await handle_bot_block(user_id)
        logging.info(f"BotBlocked: User {user_id} blocked the bot.")
        if user_id in left_users_data:
            await notify_admins(f"User:{left_users_data[user_id]['full_name']}\nUsername: @{left_users_data[user_id]['username']} botni blokladi🚫")
async def notify_admins(message: str):
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")


# @dp.errors_handler()
# async def handle_blocked_or_left(update, exception):
#     if isinstance(exception, Exception):
#         if update.message:
#             user_id = update.message.from_user.id
#             remove_user_from_data(user_id)
#             logging.info(f"Removed user {user_id} from data due to bot block or leave.")
#     return True


if __name__ == '__main__':
    # Start the periodic subscription check in the background
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_subscription_check())

    # Start the bot
    executor.start_polling(dp, skip_updates=True)

