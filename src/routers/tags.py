from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, Field, ConfigDict
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/tags", tags=["Tags"])

class TagsBase(BaseModel):
    pass

class TagsCreate(TagsBase):
    TagName: str = Field(max_length=31)

class TagsResponse(TagsCreate):
    TagId: int
    model_config = ConfigDict(from_attributes=True)

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

    @router.get("/{tag_id}", response_model=TagsResponse)
    def get_tag(self, tag_id: int):
        tag = self.db.query(models.DBTags).filter(models.DBTags.TagId == tag_id).first()
        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag

    @router.post("/", response_model=TagsResponse)
    def create_tag(self, item: TagsCreate):
        all_tags = self.db.query(models.DBTags).all()
        for tag in all_tags:
            if tag.TagName == item.TagName:
                raise HTTPException(status_code=409, detail="Tag already exists")
        new = models.DBTags(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    @router.delete("/{tag_id}", status_code=204)
    def delete_tag_by_id(self, tag_id: int):
        tag = self.db.query(models.DBTags).filter(models.DBTags.TagId == tag_id).first()
        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        self.db.delete(tag)
        self.db.commit()

    @router.delete("/{tag_name}", status_code=204)
    def delete_tag_by_id(self, tag_name: str):
        tag = self.db.query(models.DBTags).filter(models.DBTags.TagName == tag_name).first()
        if tag is None:
            raise HTTPException(status_code=404, detail="Tagname not found")
        self.db.delete(tag)
        self.db.commit()
