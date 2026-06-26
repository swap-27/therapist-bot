from auth import register_user, authenticate_user

register_user("swap27", "mypassword", "Swapnil")

user = authenticate_user("swap27", "mypassword")
print(user)

user = authenticate_user("swap27", "wrongpassword")
print(user)