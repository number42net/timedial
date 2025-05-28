import getpass
import subprocess

import bcrypt

from timedial.accounts import account

login_user = subprocess.check_output(["whoami"]).decode().strip()
user = account.read(login_user)

change = False
for name, field in account.UserModel.model_fields.items():
    extra = field.json_schema_extra
    if isinstance(extra, dict) and not extra.get("menu_visible", True):
        continue

    title = field.title if field.title else name
    description = (field.description if field.description else "",)
    value = getattr(user, name)
    if isinstance(value, list):
        value = ",".join(value)

    if name == "password_hash":
        while True:
            pass1 = getpass.getpass(f"{title} [Blank to skip change]: ")
            if not pass1:
                break
            pass2 = getpass.getpass(f"{title} [Repeat]: ")

            if not pass1 == pass2:
                print("Passwords do not match")
                continue

            hashed = bcrypt.hashpw(pass1.encode("utf-8"), bcrypt.gensalt())
            user.password_hash = hashed.decode("utf-8")
            change = True
            break
    else:
        update: str | list[str] = input(f"{title} [{value}]: ").strip()
        if update:
            change = True
            if isinstance(getattr(user, name), list) and isinstance(update, str):
                update = [i.strip() for i in update.split(",")]
            setattr(user, name, update)

if change:
    user.write()
    print("Information updated!")
else:
    print("Nothing changed")

print("\nPress enter to continue...")
input()
