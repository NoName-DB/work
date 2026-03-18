from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.security import get_password_hash, verify_password
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def __init__(self, model: type[User]):
        self.model = model

    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(self.model).where(self.model.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
        if obj_in.full_name is not None:
            db_obj.full_name = obj_in.full_name
        if obj_in.is_active is not None:
            db_obj.is_active = obj_in.is_active
        if obj_in.is_superuser is not None:
            db_obj.is_superuser = obj_in.is_superuser

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(User)
