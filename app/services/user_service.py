from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from sqlalchemy import or_
from app.services.auth_service import GenerateAuthCode
from app.core.security import pwd_context
from sqlalchemy.exc import IntegrityError
from abc import ABC, abstractmethod


class Validations(ABC):
    @abstractmethod
    def create_user(self, db: Session, user_input: UserCreate) -> dict:
        pass


class CreateUser(Validations):
    async def create_user(self, db: Session, user_input: UserCreate) -> dict:
        """Main method to create a new user."""
        user = self._check_account(db, user_input.email, user_input.username)
        if user["status"] == "error":
            return user
        
        auth_code = GenerateAuthCode()
        result = await auth_code.generate_code(db)
        if result["status"] == "error":
            return result
        
        code = result["message"]
        if isinstance(code, str):
            code = int(code)

        return self._add_user(db, user_input, code)

    def _check_account(self, db: Session, email: str, username: str) -> dict:
        """Check if user email or username already exists."""
        try:
            existing_user = (
                db.query(User)
                .filter(or_(User.email == email, User.username == username))
                .first()
            )

            if not existing_user:
                return {"status": "success", "message": "No account found"}
            else:
                return {
                    "status": "error",
                    "message": f"Account already exists for email '{email}' or username '{username}'"
                }

        except Exception as exc:
            print(f"Error during account check: {exc}")
            return {"status": "error", "message": "Database query failed"}

    def _add_user(self, db: Session, user: UserCreate, code: int) -> dict:
        """Add a new user to the database."""
        hashed_password = pwd_context.hash(user.password)

        try:
            db_user = User(
                name=user.full_name,
                username=user.username.lower(),  
                email=user.email.lower(),
                is_active=False,
                code=code,  
                hashed_password=hashed_password
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return {"status": "success", "message": "User created successfully", "data": db_user}

        except IntegrityError:
            db.rollback()
            return {"status": "error", "message": "Email or username already exists"}

        except Exception as exc:
            db.rollback()
            print(f"Error during user creation: {exc}")
            return {"status": "error", "message": "Failed to create user"}