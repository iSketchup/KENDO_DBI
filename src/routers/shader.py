from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from pydantic import BaseModel,  ConfigDict
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from database import get_db
import models
from models import DBShader, DBTextures, DBUsers
from routers import likes, comments, tags
from routers.base import BaseAPI

router = APIRouter(prefix="/{user_id}/shaders", tags=["Shader"])


class TextureResponse(BaseModel):
    id: int
    Texture64: str

class ShaderBlank(BaseModel):
    ShaderName: str

class ShaderCreate(ShaderBlank):
    user_id: int
    ShaderCode: str


class ShaderUpdate(ShaderCreate):
    ShaderTextures: list[TextureResponse]



class ShaderResponse(ShaderCreate):
    ShaderId: int
    ShaderAuthor : str
    ShaderTags: list[str]
    ShaderLikes: likes.LikesResponse
    ShaderTextures: list[TextureResponse]

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

        user = self.db.query(DBUsers).filter(DBUsers.UserId == shader.user_id).first()
        shader_Author = "guest"
        if user is not None:
            shader_Author = user.UserName


        result = {
            "ShaderName": shader.ShaderName,
            "ShaderCode": shader.ShaderCode,
            "user_id": shader.user_id,
            "ShaderId": shader.ShaderId,
            "ShaderAuthor": shader_Author,
            "ShaderTags": self._get_shader_tags(shader.ShaderId),
            "ShaderLikes": self._get_shader_likes(shader.ShaderId, user_id),
            "ShaderTextures": textures,
        }

        if include_comments:
            comments_query = (
                self.db.query(models.DBComments, models.DBUsers)
                .join(models.DBUsers, models.DBUsers.UserId == models.DBComments.user_id)
                .filter(models.DBComments.shader_id == shader.ShaderId)
                .all()
            )

            result["ShaderComments"] = [{
                    "CommentText": comment.CommentText,
                    "CommentAuthor": author.UserName,
                } for comment, author in comments_query]


        return result

    def create_Shadertag_model(self, tag_id: int, user_id:int, shader_id:int):
        shader = (
            self.db.query(models.DBShader)
            .filter(models.DBShader.ShaderId == shader_id)
            .first()
        )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        if shader.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only Author of the Shader can Change the Shadertags")

        tag = (
            self.db.query(models.DBTags)
            .filter(models.DBTags.TagId == tag_id)
            .first()
        )

        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")


        new = models.DBShaderTags(
            tag_id=tag_id,
            user_id=user_id,
            shader_id=shader_id,
        )
        return  new

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

    @router.get("/filter/", response_model=list[ShaderResponse])
    def get_by_filters(self, user_id:int, shader_user_name: Optional[str] = Query(None), shader_name: Optional[str] = Query(None),tags: Optional[list[str]] = Query(None)):
        result = self.db.query(models.DBShader)

        if shader_user_name is not None:
            shader_user = self.db.query(DBUsers).filter(models.DBUsers.UserName == shader_user_name).first()
            if shader_user is None:
                raise HTTPException(status_code=404, detail="Username not found")
            result = result.filter(DBShader.user_id == shader_user.UserId)
        if shader_name is not None:
            result = result.filter(models.DBShader.ShaderName.ilike(f"%{shader_name}%"))
        if tags is not None:
            pass
            #result = (
            #result.join(models.DBShaderTags, models.DBShaderTags.shader_id == models.DBShader.ShaderId)
            #.join(models.DBTags, models.DBTags.TagId == models.DBShaderTags.tag_id)
            #.filter(models.DBTags.TagName.in_(tags))
            #.distinct())

        return [self._serialize_shader(shader, shader.user_id) for shader in result]

    @router.post("/new", response_model=SingleShaderResponse)
    def create_blank_shader(self, user_id: int, input: ShaderBlank):

        base_shader = """#version 330 core\n\nout vec4 outputColor;\n\nin vec2 TexCoord;\n\nuniform float uTime;\n\nvec3 hsvToRgb(vec3 c)\n{\n    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0);\n    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);\n}\n\nvoid main()\n{\n    vec2 uv = TexCoord;\n\n    float diagonal = (uv.x + uv.y) * 0.5;\n\n    float hue = fract(diagonal + uTime * 0.15);\n\n    vec3 color = hsvToRgb(vec3(hue, 1.0, 1.0));\n\n    outputColor = vec4(color, 1.0);\n}
        """

        new = models.DBShader(
            user_id=user_id,
            ShaderCode=base_shader,
            ShaderName=input.ShaderName,
        )


        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)

        return self._serialize_shader(new, user_id, True)

    @router.post("/shadertag/{shader_id}/{tag_id}", response_model=tags.ShaderTagsResponse)
    def create_shadertag(self, tag_id: int, user_id: int, shader_id: int):

        new = self.create_Shadertag_model(tag_id,user_id,shader_id)
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

        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)

        return new

    @router.delete("/shadertag/{shader_id}/{tag_name}", response_model=tags.ShaderTagsResponse)
    def delete_shadertag(self, tag_name: str, user_id: int, shader_id: int):
        shader = (
            self.db.query(models.DBShader)
            .filter(models.DBShader.ShaderId == shader_id)
            .first()
        )

        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        if shader.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only Author of the Shader can Change the Shadertags",
            )

        tag = (
            self.db.query(models.DBTags)
            .filter(models.DBTags.TagName == tag_name)
            .first()
        )

        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")

        shader_tag = (
            self.db.query(models.DBShaderTags)
            .filter(
                models.DBShaderTags.shader_id == shader_id,
                models.DBShaderTags.tag_id == tag.TagId,
                models.DBShaderTags.user_id == user_id,
            )
            .first()
        )

        if shader_tag is None:
            raise HTTPException(status_code=404, detail="Shader does not have this tag")

        response = {
            "tag_id": shader_tag.tag_id,
            "shader_id": shader_tag.shader_id,
            "user_id": shader_tag.user_id,
        }

        self.db.delete(shader_tag)
        self.db.commit()

        return response


    @router.get("/shadertag/{shader_id}", response_model=list[str])
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

    @router.delete("/{shader_id}/shadertexture/{TextureId}", status_code=204)
    def delete_shadertextures(self, TextureId: int,):
        self.db.query(DBTextures).filter(DBTextures.id == TextureId).delete()
        self.db.commit()

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
