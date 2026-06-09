from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from models import DBTags, DBShader
from routers.base import BaseAPI

router = APIRouter(prefix="/tags", tags=["Tags"])

class TagsBase(BaseModel):
    pass

class TagsCreate(TagsBase):
    TagName: str = Field(max_length=31)

class TagsResponse(TagsCreate):
    TagId: int

class ShaderTagsResponse(BaseModel):
    tag_id:int
    shader_id:int
    user_id:int

@cbv(router)
class Tags(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/", response_model=list[TagsResponse])
    def get_tags(self):
        return self.db.query(models.DBTags).all()


    @router.post("/", response_model=TagsResponse)
    def create_tag(self, item:TagsCreate):
        new = models.DBTags(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new


