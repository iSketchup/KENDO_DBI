from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(
    prefix="/shaders", tags=["Shader"])


class ShaderCreate(BaseModel):
    ShaderCode: str

class ShaderResponse(ShaderCreate):
    ShaderId: int
    ShaderLikes: int

def populate_shaderlikes(self, shaders):
    for shader in shaders:
        shader.ShaderLikes = self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader.ShaderId).count()
    return shaders
@cbv(router)
class ShaderTags(BaseAPI):
    db : Session = Depends(get_db)
    @router.get("/", response_model=list[ShaderResponse])
    def get_all_shaders(self):
        shaders = self.db.query(models.DBShader).all()
        return populate_shaderlikes(self, shaders)

    @router.get("/{shader_id}", response_model=ShaderResponse)
    def get_shader_by_id(self, shader_id: int):
        return self.db.query(models.DBShader).filter(models.DBShader.ShaderId == shader_id).first()



router_per_user = APIRouter(
    prefix="/users/{user_id}/shaders", tags=["Shader"])
@cbv(router_per_user)
class ShadersAPI(BaseAPI):
    db : Session = Depends(get_db)


    @router_per_user.get("/", response_model=list[ShaderResponse])
    def get_shader_by_user(self, user_id: int):
        shaders = self.db.query(models.DBShader).filter(models.DBShader.user_id == user_id).all()
        return populate_shaderlikes(self, shaders)

    @router_per_user.post("/", response_model=ShaderCreate)
    def new_shader(self, item: ShaderCreate, user_id: int):
        new = models.DBShader(**item.model_dump(), user_id=user_id)
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new