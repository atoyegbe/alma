from typing import Dict, Any, Optional


from app.models import User
from app.database import create_user, get_user


async def save_user_info(data: Dict[str, Any]):
    new_user = User()
    new_user.user_id = data['id']
    new_user.name = data['display_name']
    new_user.country = data['country']

    print('saving user')
    await create_user(new_user)


async def get_user_info(user_id: str) -> Optional[User]:
    _user = await get_user(user_id)
    if not _user:
        return None
    user = User(**_user)
    return user



# TODO : save users top artist
# TODO : save users top track
#  TODO : update user data
#  TODO : return all users
