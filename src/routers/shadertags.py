from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/{shader_id}/shadertags", tags=["Shadertags"])

class ShadertagsBase(BaseModel):
    pass

class ShadertagsCreate(ShadertagsBase):
    tag_id: int
    shader_id: int
    class Config:
        from_attributes = True

class ShadertagsResponse(ShadertagsCreate):
    ShaderTagsID : int

@cbv(router)
class Shadertags(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/", response_model=list(ShadertagsResponse))
    def get_Shadertags(self, shader_id : int):
        return self.get_or_404(self.db, models.DBShaderTags, shader_id)

    @router.post("/", response_model=ShadertagsCreate)
    def create_Shadertag(self, item : ShadertagsCreate):
        new = models.DBComments(**item.model_dump())
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new


