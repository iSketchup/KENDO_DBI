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
    ShaderName: str
    user_id:int



class ShaderResponse(ShaderCreate):
    ShaderId: int
    ShaderTags: list[tags.TagsResponse]
    ShaderLikes: likes.LikesResponse
    model_config = ConfigDict(from_attributes=True)

class SingleShaderResponse(ShaderResponse):
    ShaderComments: list[comments.CommentResponse]

@cbv(router)
class Shaders(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/{shader_id}", response_model=SingleShaderResponse)
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
        shader = self.db.query(models.DBShader).filter(DBShader.ShaderId == shader_id).first()

        return {
            "ShaderId": shader_id,
            "ShaderCode": shader.ShaderCode,
            "ShaderName": shader.ShaderName,
            "user_id": shader.user_id,
            "ShaderLikes": {
                "amount": like_amount,
                "liked_by_u": liked_by_user,
            },
            "ShaderComments": shader_comments,
            "ShaderTags": shader_tags,
        }

    @router.get("/", response_model=list[ShaderResponse])
    def get_all_shaders(self, user_id: int):
        all_shaders = self.db.query(models.DBShader).all()
        results = []
        for shader in all_shaders:
            liked_by_user = False
            like_amount = self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader.ShaderId).count()

            if self.db.query(models.DBLikes).filter(models.DBLikes.shader_id == shader.ShaderId,models.DBLikes.user_id == user_id, ).first() is not None:
                liked_by_user = True

            shader_tags = self.db.query(models.DBTags).join(models.DBShaderTags,
                                                            models.DBShaderTags.tag_id == models.DBTags.TagId).filter(
                models.DBShaderTags.shader_id == shader.ShaderId).all()

            results.append({
            "ShaderName": shader.ShaderCode,
            "ShaderCode": shader.ShaderName,
            "user_id": user_id,
            "ShaderId": shader.ShaderId,
            "ShaderTags": shader_tags,
            "ShaderLikes": {"amount": like_amount,"liked_by_u": liked_by_user},})
        return results


    @router.put("/{shader_id}", response_model=ShaderCreate)
    def put_shader_by_id(self, shader_id: int, user_id:int, shaderCode: str, shaderName: str,):
        # TODO: Only Creator of the Shader should be able to put
        shader = self.db.query(models.DBShader).filter(models.DBShader.ShaderId == shader_id).first()
        shader.ShaderCode = shaderCode
        shader.ShaderName = shaderName
        self.db.commit()
        self.db.refresh(shader)
        return shader

    @router.get("/by_user={shader_user_id}", response_model=list[ShaderResponse])
    def get_shader_by_user(self, shader_user_id: int):
        return self.db.query(models.DBShader).filter(DBShader.user_id == shader_user_id).all()

    @router.post("/", response_model=ShaderCreate)
    def create_shader(self, user_id:int, shader_code:str, shader_name:str):
        new = models.DBShader(user_id = user_id, ShaderCode = shader_code, ShaderName=shader_name)
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    @router.post("/shadertag", response_model=tags.ShaderTagsResponse)
    def create_shadertag(self, tag_id:int, user_id:int, shader_id:int):
        new = models.DBShaderTags(tag_id = tag_id , user_id = user_id, shader_id = shader_id)
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new

    @router.get("/shadertag")
    def get_tags_by_id(self, shader_id: int, ):
        return self.db.query(models.DBTags).join(models.DBShader).filter(DBShader.ShaderId == shader_id).all()

