from sqlalchemy import Column, Integer, String, BOOLEAN, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class DBUsers(Base):
    # Der Wert in String(...) bestimmt die maximale Länge von einem String
    __tablename__ = "Users"
    UserId = Column(Integer, primary_key=True)
    UserName = Column(String(31) , unique=True ,index=True)
    passwd = Column(String)
    shaders = relationship("DBShader", back_populates="user")


class DBShader(Base):
    __tablename__ = "Shaders"
    ShaderId = Column(Integer, primary_key=True)
    ShaderName = Column(String(63) , index=True)
    ShaderCode = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("Users.UserId"))
    user = relationship("DBUsers", back_populates="shaders")


class DBComments(Base):
    __tablename__ = "Comments"
    CommentId = Column(Integer, primary_key=True)
    CommentText = Column(String(255))
    user_id = Column(Integer, ForeignKey("Users.UserId"))
    shader_id = Column(Integer, ForeignKey("Shaders.ShaderId"))

class DBShaderTags(Base):
    __tablename__ = "ShaderTags"
    ShaderTagsID = Column(Integer, primary_key=True)
    shader_id = Column(Integer, ForeignKey("Shaders.ShaderId"))
    tag_id = Column(Integer, ForeignKey("Tags.TagId"))
    user_id = Column(Integer, ForeignKey("Users.UserId"))

class DBTags(Base):
    __tablename__ = "Tags"
    TagId = Column(Integer, primary_key=True)
    TagName = Column(String(31) ,unique=True, index=True)

class DBLikes(Base):
    __tablename__ = "Likes"
    LikeId = Column(Integer, primary_key=True)
    shader_id = Column(Integer, ForeignKey("Shaders.ShaderId"))
    user_id = Column(Integer, ForeignKey("Users.UserId"))


class DBTextures(Base):
    __tablename__ = "Textures"
    TextureId = Column(Integer, primary_key=True)
    TexturePath = Column(String)
    shader_id = Column(Integer, ForeignKey("Shaders.ShaderId"))

