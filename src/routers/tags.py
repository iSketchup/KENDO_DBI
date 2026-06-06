from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/tags", tags=["Tags"])

class TagsBase(BaseModel):
    pass

class TagesCreate(TagsBase):
    TagName: str = Field(max_length=31)
    class Config:
        from_attributes = True

class TagesResponse(TagesCreate):
    tag_id: int


@cbv(router)
class Likes(BaseAPI):
    db : Session = Depends(get_db)
    @router.get("/", response_model=list(TagesResponse))
    def get_tags(self, shader_id : int):
        return self.get_or_404(self.db, models.DBShaderTags, shader_id)

    @router.post("/", response_model=TagesCreate)
    def create_tag(self, item : TagesCreate):
        new = models.DBComments(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new


