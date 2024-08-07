from fastapi import status, HTTPException
from app.models import User
from app.repositories import UserRepository
from app.repositories.workspace import WorkspaceRepository
from app.schemas.responses.users import UserInfo, OrganizationBase, SpaceBase
from core.controller import BaseController
from core.database.transactional import Propagation, Transactional
from core.exceptions.base import NotFoundException


class UserController(BaseController[User]):
    def __init__(
        self, user_repository: UserRepository, space_repository: WorkspaceRepository
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.space_repository = space_repository

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def create_default_user(self) -> User:
        users = await self.get_all(limit=1, join_={"memberships"})
        if not users:
            await self.user_repository.create_and_init_dummy_user()

    async def get_by_email(self, email: str) -> User:
        return await self.user_repository.get_by_email(email)

    async def me(self) -> UserInfo:
        users = await self.get_all(limit=1)
        if not users:
            raise NotFoundException(
                "No user found. Please restart the server and try again"
            )

        user = users[0]

        organizations = [
            OrganizationBase(
                id=membership.organization.id, name=membership.organization.name
            )
            for membership in user.memberships
        ]

        space = await self.space_repository.get_by(
            "organization_id", organizations[0].id
        )
        space = space[0]

        space_base = SpaceBase(id=space.id, name=space.name, slug=space.slug)

        return UserInfo(
            email=user.email,
            first_name=user.first_name,
            id=user.id,
            organizations=organizations,
            space=space_base,
            features=user.features
        )
    
    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def update_features(self, user_id, features):
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                "No user found. Please restart the server and try again"
            )        

        user.features = features
        return user.features

    async def check_log_feature(self, user_id: str):
        user_in_db = await self.user_repository.get_by_id(user_id)
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        logs_feature = next(
            (route for route in user_in_db.features["routes"] if route["name"] == "Logs"),
            None
        )
        
        if not logs_feature or not logs_feature["enabled"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Logs feature is disabled for this user."
            )

        return True