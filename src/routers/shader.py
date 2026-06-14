from fastapi import APIRouter, HTTPException, responses
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field, ConfigDict
from fastapi_restful.cbv import cbv
from pydantic._internal import _serializers
from sqlalchemy import Select
from sqlalchemy.orm import Session

from database import get_db
import models
from models import DBShader, DBTextures
from routers import likes, comments, tags
from routers.base import BaseAPI
from routers.likes import Likes

router = APIRouter(prefix="/{user_id}/shaders", tags=["Shader"])


class TextureResponse(BaseModel):
    id: int
    Texture64: str


class ShaderCreate(BaseModel):
    ShaderCode: str
    ShaderName: str
    user_id: int


class ShaderUpdate(ShaderCreate):
    ShaderTextures: list[TextureResponse]



class ShaderResponse(ShaderCreate):
    ShaderId: int
    ShaderTags: list[str]
    ShaderLikes: likes.LikesResponse
    ShadersTextures: list[TextureResponse]

    model_config = ConfigDict(from_attributes=True)


class SingleShaderResponse(ShaderResponse):
    ShaderComments: list[comments.CommentResponse]


@cbv(router)
class Shaders(BaseAPI):
    db: Session = Depends(get_db)

    def _get_shader_tags(self, shader_id: int) -> list[str]:
        tag_rows = (
            self.db.query(models.DBTags)
            .join(
                models.DBShaderTags,
                models.DBShaderTags.tag_id == models.DBTags.TagId,
            )
            .filter(models.DBShaderTags.shader_id == shader_id)
            .all()
        )
        return [tag.TagName for tag in tag_rows]

    def _get_shader_likes(self, shader_id: int, user_id: int) -> dict:
        like_amount = (
            self.db.query(models.DBLikes)
            .filter(models.DBLikes.shader_id == shader_id)
            .count()
        )

        liked_by_user = (
            self.db.query(models.DBLikes)
            .filter(
                models.DBLikes.shader_id == shader_id,
                models.DBLikes.user_id == user_id,
            )
            .first()
            is not None
        )

        return {
            "amount": like_amount,
            "liked_by_u": liked_by_user,
        }



    def _serialize_shader(self, shader: DBShader, user_id: int, include_comments: bool = False) -> dict:
        textures = (
            self.db.query(models.DBTextures)
            .filter(models.DBTextures.shader_id == shader.ShaderId)
            .all()
        )

        result = {
            "ShaderName": shader.ShaderName,
            "ShaderCode": shader.ShaderCode,
            "user_id": shader.user_id,
            "ShaderId": shader.ShaderId,
            "ShaderTags": self._get_shader_tags(shader.ShaderId),
            "ShaderLikes": self._get_shader_likes(shader.ShaderId, user_id),
            "ShadersTextures": textures,
        }

        if include_comments:
            result["ShaderComments"] = (
                self.db.query(models.DBComments)
                .filter(models.DBComments.shader_id == shader.ShaderId)
                .all()
            )

        return result

    @router.get("/{shader_id}", response_model=SingleShaderResponse)
    def get_shader_by_id(self, user_id: int, shader_id: int):
        shader = (
            self.db.query(DBShader)
            .filter(DBShader.ShaderId == shader_id)
            .first()
        )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        return self._serialize_shader(shader, user_id, include_comments=True)

    @router.get("/", response_model=list[ShaderResponse])
    def get_all_shaders(self, user_id: int):
        all_shaders = self.db.query(models.DBShader).all()
        return [self._serialize_shader(shader, user_id) for shader in all_shaders]

    @router.put("/{shader_id}", response_model=ShaderCreate)
    def put_shader_by_id(self, shader_id: int, user_id: int, item : ShaderUpdate):


        shader = (
            self.db.query(models.DBShader)
            .filter(models.DBShader.ShaderId == shader_id)
            .first()
        )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        if shader.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only the shader creator can edit this shader")

        shader.ShaderCode = item.ShaderCode
        shader.ShaderName = item.ShaderName

        self.db.query(models.DBTextures).filter(models.DBTextures.shader_id == shader_id).delete()


        for i in item.ShaderTextures:
            self.create_shadertextures(shader_id, i.Texture64)



        self.db.commit()
        self.db.refresh(shader)

        return shader

    @router.get("/by_user/{shader_user_id}", response_model=list[ShaderResponse])
    def get_shader_by_user(self, user_id: int, shader_user_id: int):
        all_shaders = (
            self.db.query(models.DBShader)
            .filter(DBShader.user_id == shader_user_id)
            .all()
        )

        return [self._serialize_shader(shader, user_id) for shader in all_shaders]

    @router.post("/", response_model=ShaderCreate)
    def create_shader(self, user_id: int, shader_code: str, shader_name: str):
        new = models.DBShader(
            user_id=user_id,
            ShaderCode=shader_code,
            ShaderName=shader_name,
        )

        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)

        return new

    @router.post("/shadertag", response_model=tags.ShaderTagsResponse)
    def create_shadertag(self, tag_id: int, user_id: int, shader_id: int):
        shader = (
            self.db.query(models.DBShader)
            .filter(models.DBShader.ShaderId == shader_id)
            .first()
        )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        tag = (
            self.db.query(models.DBTags)
            .filter(models.DBTags.TagId == tag_id)
            .first()
        )

        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")

        existing = (
            self.db.query(models.DBShaderTags)
            .filter(
                models.DBShaderTags.shader_id == shader_id,
                models.DBShaderTags.tag_id == tag_id,
            )
            .first()
        )

        if existing is not None:
            raise HTTPException(status_code=400, detail="Shader already has this tag")

        new = models.DBShaderTags(
            tag_id=tag_id,
            user_id=user_id,
            shader_id=shader_id,
        )

        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)

        return new

    @router.get("/shadertag", response_model=list[str])
    def get_tags_by_id(self, shader_id: int):
        return self._get_shader_tags(shader_id)

    @router.post("/{shader_id}/shadertexture")
    def create_shadertextures(self,shader_id:int, Encoded:str,):
        new = models.DBTextures( shader_id = shader_id, Texture64=Encoded)
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)

        return new

    @router.put("/{shader_id}/shadertexture/{TextureId}")
    def put_shadertextures(self, shader_id: int, TextureId: int,Encoded: str, ):
        Tex = self.get_or_404(self.db, DBTextures, TextureId)

        Tex.Texture64 = Encoded

        self.db.commit()
        self.db.refresh(Tex)
        return Tex

    @router.get("/{shader_id}/shadertexture")
    def get_textures_by_id(self, shader_id: int, ):
        shader = (
                self.db.query(models.DBShader)
                  .filter(DBShader.ShaderId == shader_id).first()
            )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        return (
            self.db.query(models.DBTextures)
            .filter(models.DBTextures.shader_id == shader_id)
            .all()
        )
