from fastapi import APIRouter, HTTPException, responses
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field, ConfigDict
from fastapi_restful.cbv import cbv
from pydantic._internal import _serializers
from sqlalchemy import Select
from sqlalchemy.orm import Session

from database import get_db
import models
from models import DBShader
from routers import likes, comments, tags
from routers.base import BaseAPI
from routers.likes import Likes

router = APIRouter(prefix="/{user_id}/shaders", tags=["Shader"])


class ShaderCreate(BaseModel):
    ShaderCode: str

class ShaderResponse(ShaderCreate):
    ShaderId: int
    ShaderTags: list[tags.TagsResponse]
    model_config = ConfigDict(from_attributes=True)

class SingleShaderResponse(ShaderResponse):
    ShaderLikes: likes.LikesResponse
    ShaderComments: list[comments.CommentResponse]

@cbv(router)
class Shaders(BaseAPI):
    db : Session = Depends(get_db)
    @router.get("/", response_model=list[ShaderResponse])
    def get_all_shaders(self, user_id: int):
        all_shaders = self.db.query(models.DBShader).all()
        results = []
        for shader in all_shaders:
            liked_by_user = False
            like_amount = self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader.ShaderId).count()

            if self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader.ShaderId,models.DBLikes.user_id == user_id, ).first() is not None:
                liked_by_user = True
            shaderCode = self.db.query(models.DBShader).filter(DBShader.ShaderId == shader.ShaderId).first().ShaderCode

            results.append({
            "ShaderId": shader.ShaderId,
            "ShaderCode": shaderCode,
            "ShaderLikes": {"amount": like_amount,"liked_by_u": liked_by_user},})
        return results

    @router.get("/{shader_id}", response_model=ShaderResponse)
    def get_shader_by_id(self,user_id:int, shader_id: int):
        liked_by_user = False
        like_amount = self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader_id).count()

        if self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader_id,
                                                models.DBLikes.user_id == user_id, ).first() is not None:
            liked_by_user = True

        shader_comments = self.db.query(models.DBComments).filter(models.DBComments.shader_id == shader_id).all()
        shader_tags = self.db.query(models.DBTags).join(models.DBShaderTags,
                                                        models.DBShaderTags.tag_id == models.DBTags.TagId).filter(
            models.DBShaderTags.shader_id == shader_id).all()
        shaderCode = self.db.query(models.DBShader).filter(DBShader.ShaderId == shader_id).first().ShaderCode

        return {
            "ShaderId": shader_id,
            "ShaderCode": shaderCode,
            "ShaderLikes": {
                "amount": like_amount,
                "liked_by_u": liked_by_user,
            },
            "ShaderComments": shader_comments,
            "ShaderTags": shader_tags,
        }
    @router.put("/{shader_id}", response_model=ShaderCreate)
    def put_shader_by_id(self, shader_id: int, item: ShaderCreate):
        shader = self.db.query(models.DBShader).filter(models.DBShader.ShaderId == shader_id).first()

        shader.ShaderCode = item.ShaderCode
        self.db.commit()
        self.db.refresh(shader)
        return shader

    @router.get("/by_user={shader_user_id}", response_model=list[ShaderResponse])
    def get_shader_by_user(self, shader_user_id: int):
        return self.db.query(models.DBShader).filter(DBShader.user_id == shader_user_id).all()


router_per_user = APIRouter(
    prefix="/{user_id}/{shader_id}", tags=["Shader"])
@cbv(router_per_user)
class ShadersUser(BaseAPI):
    db : Session = Depends(get_db)


    @router_per_user.get("/{shader_user_id}", response_model=list[ShaderResponse])
    def get_shader_by_user(self, shader_user_id: int):
        return self.db.query(models.DBShader).filter(DBShader.user_id == shader_user_id).all()

    @router_per_user.put("/", response_model=ShaderCreate)
    def change_shader(self, new_code:str, shader_id):
        result = self.get_or_404(self.db, models.DBShader, shader_id)
        result.ShaderCode = new_code
        self.db.commit()
        self.db.refresh(result)
        return result

