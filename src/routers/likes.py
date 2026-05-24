from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/likes", tags=["Likes"])

class LikesBase(BaseModel):
    pass

class LikesCreate(LikesBase):
    user_id : int
    shader_id : int

class LikesResponse(BaseModel):
    amount: int
    liked_by_u: bool


@cbv(router)
class Likes(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/", response_model=LikesResponse)
    def likes(self, shader_id : int = None, user_id : int = None):
        amount = None
        liked_by_u = None
        if shader_id is not None and shader_id in self.db.query(models.DBShader.ShaderId).all():
            amount = self.db.query().filter((shader_id == models.DBLikes.shaderId)).count()
            if user_id is not None and user_id in self.db.query(models.DBUsers.UserId).all():
                if self.db.query().filter((shader_id == models.DBLikes.shaderId) & (user_id == models.DBLikes.user_id)).first() is not None:
                    liked_by_u = True
                else:
                    liked_by_u = False
            else:
                raise HTTPException(400, "user_id hast to be not null and in user table")

        else:
            raise HTTPException(400, "shader_id has to be not null and in shader table")

        return {"amount": {amount}, "liked_by_u": {liked_by_u}}

    @router.post("/", response_model=LikesCreate)
    def new_like(self, item: LikesCreate):
        if item.shader_id not in self.db.query(models.DBShader.ShaderId).all():
            raise HTTPException(400, "shader_id must be in shader table")
        if item.user_id not in self.db.query(models.DBUsers.UserId).all():
            raise HTTPException(400, "user already liked shader")
        new = models.DBLikes(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    @router.delete("/", response_model=LikesCreate)
    def delete_like(self, item: LikesCreate):
        if item.shader_id not in self.db.query(models.DBShader.ShaderId).all():
            raise HTTPException(400, "shader_id must be in shader table")
        if item.user_id not in self.db.query(models.DBUsers.UserId).all():
            raise HTTPException(400, "user already liked shader")
        item = self.db.query(models.DBLikes).filter(models.DBLikes.shaderId == item.shader_id, models.DBLikes.user_id == item.user_id).first()
        self.db.delete(item)
        self.db.commit()
        return item
