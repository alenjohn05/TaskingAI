from common.models import Admin
from common.error import raise_http_error, ErrorCode
import bcrypt
from .refresh_token import refresh_admin_token
from .redis import set_redis_admin


def _verify_password(password: str, salt: str, password_hash: str):
    password_hash_bytes = password_hash.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    re_hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt_bytes)
    if password_hash_bytes == re_hashed_password:
        return True
    else:
        return False


async def login_admin(conn, admin: Admin, password: str):
    # 1. check password
    if _verify_password(password, admin.salt, admin.password_hash):
        admin = await refresh_admin_token(conn, admin)
    else:
        raise_http_error(ErrorCode.INCORRECT_PASSWORD, message="Password is incorrect.")

    # 2. write to redis and return
    await set_redis_admin(admin)

    return admin
