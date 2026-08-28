from models import User, InvalidIDError

u = User("Test Patient", "12345678", "mypassword")
print("Correct password check:", u.check_password("mypassword"))
print("Wrong password check:", u.check_password("wrongpass"))

try:
    User("Test", "123", "pw")
    print("ERROR: bad ID was accepted — validation is broken")
except InvalidIDError as e:
    print("Validation correctly caught bad ID:", e)

