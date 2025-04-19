import logging
from typing import Any, Type
from app.models.user import User
from app.db import get_supabase

class BaseService:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def log(self, message: str, level: str = "info"):
        getattr(self.logger, level.lower(), self.logger.info)(message)

    def handle_error(self, error: Exception, context: str = ""):
        self.logger.error(f"Error in {self.__class__.__name__} {context}: {error}")
        raise error

class UserService(BaseService):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)
        self.supabase = get_supabase()

    def get_user_by_id(self, user_id: str) -> Any:
        try:
            res = self.supabase.table("users").select("*").eq("id", user_id).single().execute()
            if getattr(res, "error", None):
                raise Exception(res.error.message)
            return res.data
        except Exception as e:
            self.handle_error(e, context=f"get_user_by_id({user_id})")

    def create_user(self, user_data: dict) -> Any:
        try:
            res = self.supabase.table("users").insert(user_data).execute()
            if getattr(res, "error", None):
                raise Exception(res.error.message)
            return res.data[0]
        except Exception as e:
            self.handle_error(e, context="create_user")
