from sqlalchemy import Column, Integer, String, BOOLEAN, VARCHAR, ForeignKey
from database import Base


class DBUsers(Base):
    # Der Wert in String(...) bestimmt die maximale Länge von einem String
    __tablename__ = "Users"
    UserId = Column(Integer, primary_key=True)
    UserName = Column(String(31) , unique=True ,index=True)
    passwd = Column(String)


class DBShader(Base):
    __tablename__ = "Shaders"
    ShaderId = Column(Integer, primary_key=True)
    ShaderCode = Column(String, index=True)


class DBComments(Base):
    __tablename__ = "Comments"
    CommentId = Column(Integer, primary_key=True)
    CommentText = Column(String(255))
    user_id = Column(Integer, ForeignKey("Users.UserId"))
    shader_id = Column(Integer, ForeignKey("Shaders.ShaderId"))

class ShaderTags(Base):
    __tablename__ = "ShaderTags"
    ShaderTagsID = Column(Integer, primary_key=True)
    shaderId = Column(Integer, ForeignKey("Shaders.ShaderId"))
    tagId = Column(Integer, ForeignKey("Tags.TagId"))

class Tags(Base):
    __tablename__ = "Tags"
    TagId = Column(Integer, primary_key=True)
    TagName = Column(String(31) ,unique=True, index=True)

class DBLikes(Base):
    __tablename__ = "Likes"
    LikeId = Column(Integer, primary_key=True)
    shaderId = Column(Integer, ForeignKey("Shaders.ShaderId"))
    user_id = Column(Integer, ForeignKey("Users.UserId"))
