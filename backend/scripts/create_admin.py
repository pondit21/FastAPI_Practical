from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.session import engine, init_db
from app.models import Role, User

email_adapter = TypeAdapter(EmailStr)


def main() -> None:
    init_db()

    raw_email = input("Admin ইমেইল: ").strip()
    try:
        email = str(email_adapter.validate_python(raw_email)).lower()
    except ValidationError:
        print("ইমেইল সঠিক নয়।")
        return

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if user:
            if user.role == Role.admin:
                print("এই ইউজার আগে থেকেই admin।")
                return
            answer = input("এই ইমেইলে অ্যাকাউন্ট আছে। admin বানাবেন? (y/n): ")
            if answer.strip().lower() != "y":
                print("বাতিল করা হলো।")
                return
            user.role = Role.admin
            session.add(user)
            session.commit()
            print(f"{email} এখন admin।")
            return

        password = getpass("পাসওয়ার্ড (কমপক্ষে ৮ অক্ষর): ")
        confirm = getpass("পাসওয়ার্ড আবার দিন: ")
        if len(password) < 8:
            print("পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।")
            return
        if password != confirm:
            print("দুটো পাসওয়ার্ড মেলেনি।")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role=Role.admin,
        )
        session.add(admin)
        session.commit()
        print(f"admin তৈরি হয়েছে: {email}")


if __name__ == "__main__":
    main()