from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field, ConfigDict
from fastapi_restful.cbv import cbv
from sqlalchemy.engine import connection_memoize
from sqlalchemy.orm import Session
from database import get_db
import models
from models import DBComments, DBShader, DBUsers
from routers.base import BaseAPI

router = APIRouter(prefix="/{user_id}/{shader_id}/comments", tags=["Comment"])

class CommentBase(BaseModel):
    CommentText : str = Field(max_length=511)

class CommentCreate(CommentBase):
    user_id : int
    shader_id : int
    model_config = ConfigDict(from_attributes=True)

class CommentResponse(CommentBase):
    CommentAuthor : str
    model_config = ConfigDict(from_attributes=True)
@cbv(router)
class Comments(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/", response_model=list[CommentResponse])
    def comments(self, shader_id : int):
        if self.db.query(models.DBShader).filter(shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")

        serialized_response = []
        all_comments = self.db.query(models.DBComments).filter(DBComments.shader_id == shader_id).all()
        for single_comment in all_comments:
            comment_Author = self.db.query(models.DBUsers.UserName).where(DBUsers.UserId == single_comment.user_id).first()[0]
            serialized_response.append({"CommentAuthor": comment_Author, "CommentText":single_comment.CommentText})
        return serialized_response

    @router.post("/")
    def new_comment(self, user_id : int, shader_id : int, item : CommentBase):
        if self.db.query(models.DBShader).filter(shader_id == models.DBShader.ShaderId).first() is None:
            raise HTTPException(400, "shader_id must be in shader table")
        if self.db.query(models.DBUsers).filter(user_id == models.DBUsers.UserId).first() is None:
            raise HTTPException(400, "user_id must be in user table")
        new = models.DBComments(user_id=user_id, shader_id=shader_id, CommentText=item.CommentText)
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
