from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/likes", tags=["Likes"])

class LikesBase(BaseModel):
    pass

class LikesCreate(LikesBase):
    user_id: int
    shader_id: int
    class Config:
        from_attributes = True

class LikesResponse(BaseModel):
    amount: int
    liked_by_u: bool


@cbv(router)
class Likes(BaseAPI):
    db : Session = Depends(get_db)
    api_key : str = Depends(verify_api_key)

    @router.get("/", response_model=LikesResponse)
    def likes(self, shader_id: int = Query(...), user_id: int = Query(None)):
        amount = None
        liked_by_u = False
        if  self.db.query(models.DBShader).filter(shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id has to be not null and in shader table")

        else:
            amount = self.db.query(models.DBLikes).filter(shader_id == models.DBLikes.shader_id).count()
            if self.db.query(models.DBUsers).filter(user_id == models.DBUsers.UserId).first() is None:
                raise HTTPException(400, "user_id must be in user table")
            else:
                if self.db.query(models.DBLikes).filter((shader_id == models.DBLikes.shader_id) & (user_id == models.DBLikes.user_id)).first() is not None:
                    liked_by_u = True

        return {"amount": amount, "liked_by_u": liked_by_u}

    @router.post("/", response_model=LikesCreate)
    def new_like(self, item: LikesCreate):
        if self.db.query(models.DBLikes).filter(item.shader_id == models.DBLikes.shader_id, item.user_id == models.DBLikes.user_id).first() is not None:
            self.delete_like(item)
        if self.db.query(models.DBShader).filter(item.shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")
        if self.db.query(models.DBUsers).filter(item.user_id == models.DBUsers.UserId).first() is None:
            raise HTTPException(400, "user_id must be in user table")
        new = models.DBLikes(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    @router.delete("/")
    def delete_like(self, item: LikesCreate):
        if self.db.query(models.DBShader).filter(item.shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")
        if self.db.query(models.DBUsers).filter(item.user_id == models.DBUsers.UserId).first() is None:
            raise HTTPException(400, "user_id must be in user table")
        item = self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == item.shader_id, models.DBLikes.user_id == item.user_id).first()
        self.db.delete(item)
        self.db.commit()
        return item
