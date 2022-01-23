""" mongo database """

from motor.motor_asyncio import AsyncIOMotorClient as Bot
from config import MONGO_DB_URI as tmo


MONGODB_CLI = Bot(tmo)
db = MONGODB_CLI.program
