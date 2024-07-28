from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
from telethon.tl.types import User
from sqlalchemy import create_engine, Column, BigInteger, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy.exc import DataError, IntegrityError
from settings import api_id, api_hash, phone

DATABASE_URL = "postgresql://admin:admin@172.19.224.1/test_proj_db_2"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()



class Message(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    date = Column(String, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)



Base.metadata.create_all(engine)




client = TelegramClient('session_name', api_id, api_hash)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    await client.start(phone)

    dialogs = await client.get_dialogs()


    threshold_time = datetime.now() - timedelta(minutes=180+9)
    threshold_time = pytz.utc.localize(threshold_time)


    for dialog in dialogs:
        if isinstance(dialog.entity, User):

            async for message in client.iter_messages(dialog.id):
                if message.date >= threshold_time:

                    print(
                        f"Chat ID: {dialog.id}, Sender ID: {message.sender_id}, Message: {message.text}, Date: {message.date}")


                    msg_data = {
                        'sender_id': message.sender_id,
                        'message': message.text or '',
                        'date': message.date.isoformat(),
                        'username': dialog.entity.username or 'N/A',
                        'first_name': dialog.entity.first_name or 'N/A',
                        'last_name': dialog.entity.last_name or 'N/A',
                        'phone': dialog.entity.phone or 'N/A'
                    }


                    new_message = Message(**msg_data)

                    try:

                        session.add(new_message)
                        session.commit()
                    except DataError as e:

                        logger.error(f"DataError: {e} - Пропускаємо повідомлення")
                        session.rollback()
                    except IntegrityError as e:

                        logger.error(f"IntegrityError: {e} - Пропускаємо повідомлення")
                        session.rollback()


with client:
    client.loop.run_until_complete(main())
