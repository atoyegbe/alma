import motor.motor_asyncio

from app.models import User
from fastapi.encoders import jsonable_encoder

MONGO_DETAILS = "mongodb://localhost:27017/alma"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.alma

users = database.get_collection("users")
friends = database.get_collection('friends')


async def create_user(user: User) -> None:
    _json_user = jsonable_encoder(user)
    await users.insert_one(_json_user)
    print('done saving user')


async def get_user(user_id: str) -> dict:
    res = await users.find_one({'user_id': user_id})
    return res

# TODO: Remeber to write test
#  TODO : update user data
#  TODO : return all users
