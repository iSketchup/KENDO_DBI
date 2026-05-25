from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.engine import connection_memoize
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/comments", tags=["Comment"])

class CommentBase(BaseModel):
    CommentText : str = Field(max_length=511)

class CommentCreate(CommentBase):
    user_id : int
    shader_id : int

class CommentResponse(CommentCreate):
    CommentId : int

@cbv(router)
class Comments(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/{Shader_id}", response_model=list[CommentResponse])
    def comments(self, Shader_id : int):
        if self.db.query(models.DBShader).filter(Shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")
        return self.db.query(models.DBComments).where(models.DBComments.shader_id == Shader_id).all()

    @router.post("/", response_model=CommentResponse)
    def new_like(self, item: CommentCreate):
        if self.db.query(models.DBShader).filter(item.shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")
        if self.db.query(models.DBUsers).filter(item.user_id == models.DBUsers.UserId).first() is None:
            raise HTTPException(400, "user_id must be in user table")
        new = models.DBComments(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new


    @router.delete("/{comment_id}")
    def delete_comment(self, comment_id :int):
        if self.db.query(models.DBComments).filter(comment_id == models.DBComments.CommentId).first() is None:
            raise HTTPException(400, "comment_id does not exits")
        item = self.db.query(models.DBComments).filter(models.DBComments.CommentId == comment_id).first()
        self.db.delete(item)
        self.db.commit()
        return item
