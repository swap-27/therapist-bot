import bcrypt
from database import db

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")

def verify_password(
        password: str,
        password_hash: str
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

def register_user(
        username: str,
        password: str,
        display_name: str
):
    password_hash = hash_password(password)

    return db.create_user(
        username=username,
        password_hash=password_hash,
        display_name=display_name
    )



def authenticate_user(
        username: str,
        password: str
):
    user = db.get_user(username)

    if user is None:
        return None

    if verify_password(password, user["password_hash"]):
        return user
    
    return None