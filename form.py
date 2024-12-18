import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from dispatcher import dp, bot
from env import ADMINS

# Define States
class MovieForm(StatesGroup):
    movie_code = State()
    movie_id = State()


# Handler for "Kino qo'shish🎬" button
@dp.message_handler(Text(equals="Kino qo'shish🎬", ignore_case=True))
async def start_movie_addition(message: types.Message):
    if message.from_user.id in ADMINS:
        await MovieForm.movie_code.set()
        await message.reply(
            "Iltimos kino kodini kiriting🔢:",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Bekor qilish❌"))
        )
    else:
        pass



@dp.message_handler(Text(equals="Bekor qilish❌", ignore_case=True), state="*")
async def stop_process(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.finish()
        await message.reply(
            "Qo'shish to'xtatildi! Agarda yana kino qo'shishni xohlasangiz 'Kino qo'shish' tugmasini bosing👇",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Kino qo'shish🎬"),types.KeyboardButton("Obunachilar👥"))
        )
    else:
        pass


# Handle the movie code input
@dp.message_handler(state=MovieForm.movie_code)
async def process_movie_code(message: types.Message, state: FSMContext):
    movie_code = message.text
    with open("movie_details.json", "r") as file:
        existing_data = json.load(file)
    if str(movie_code) in existing_data:
        await message.reply(
            "Bu kod band. Iltimos boshqa kod kiriting🚮:",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Bekor qilish❌"))
        )
        return
    await state.update_data(movie_code=movie_code)
    await MovieForm.next()
    await message.reply(
        "Yaxshi endi kinoning kanaldagi linkini kiriting🔗:",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Bekor qilish❌"))
    )


# Handle the movie ID input

@dp.message_handler(state=MovieForm.movie_id)
async def process_movie_id(message: types.Message, state: FSMContext):
    movie_id = message.text.split("/")[-1].strip()
    await state.update_data(movie_id=movie_id)

    # Retrieve all data from the state
    data = await state.get_data()

    # Load the existing data from the JSON file
    try:
        with open("movie_details.json", "r") as file:
            existing_data = json.load(file)  # Load existing movie data
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, start with an empty dictionary
        existing_data = {}

    # Add or update the movie data with the movie_id as the key
    existing_data[data['movie_code']] = data  # Store the movie data with its ID as the key

    # Save the updated data back to the JSON file
    with open("movie_details.json", "w") as file:
        json.dump(existing_data, file, indent=4)

    await message.reply("Kino ma'lumotlari muvaffaqiyatli saqlandi☺️", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Kino qo'shish🎬"),types.KeyboardButton("Obunachilar👥")))

    # Finish the conversation
    await state.finish()
