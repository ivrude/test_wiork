import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from aiogram.utils import executor
from settings import DATABASE_URL, API_TOKEN





engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()





class Message(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)



logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Показати останні 10 записів", callback_data="show_last_10"))


    await message.answer("Привіт! Натисніть кнопку, щоб побачити останні 10 записів.", reply_markup=keyboard)



@dp.callback_query_handler(text='show_last_10')
async def process_callback_show_last_10(callback_query: types.CallbackQuery):
    new_session = Session()
    try:
        new_session.expire_all()
        messages = new_session.query(Message).order_by(Message.id.desc()).limit(10).all()

        response = ""
        for msg in messages:
            response += (f"ID: {msg.id}\nFirst: {msg.first_name}\nLast: {msg.last_name}\nUsername: {msg.username}\n"
                         f"Phone Number: {msg.phone}\nMessage: {msg.message}\nDate Time: {msg.date}\nUser_id: {msg.sender_id}\n\n")


        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("Показати останні 10 записів", callback_data="show_last_10"))

        if response:
            await bot.send_message(callback_query.from_user.id, response)
        else:
            await bot.send_message(callback_query.from_user.id, "Немає записів.")

        await bot.send_message(callback_query.from_user.id, "Натисніть кнопку, щоб переглянути останні 10 записів.",
                               reply_markup=keyboard)
        await bot.answer_callback_query(callback_query.id)
    finally:
        new_session.close()

async def on_startup(dispatcher: Dispatcher):

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
