from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/Shader", tags=["Shader"])

class ShaderCreate(BaseModel):
    ShaderCode: str

class ShaderResponse(ShaderCreate):
    ShaderId: int





@cbv(router)
class ShadersAPI(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/{idx}", response_model=list[ShaderResponse])
    def get_shader(self, idx: int):
        return self.db.query(models.DBShader).filter(models.DBShader.ShaderId == idx).all()

