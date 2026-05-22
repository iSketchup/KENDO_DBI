from sqlalchemy import Column, Integer, String, BOOLEAN, VARCHAR, ForeignKey
from database import Base


class DBUsers(Base):
    __tablename__ = "Users"
    UserId = Column(Integer, primary_key=True)
    UserName = Column(String, max_lengh=31 , unique=True ,index=True)
    passwd = Column(String)


class DBShader(Base):
    __tablename__ = "Shaders"
    ShaderId = Column(Integer, primary_key=True)
    ShaderCode = Column(String, index=True)


class DBComment(Base):
    __tablename__ = "Comment"
    CommentId = Column(Integer, primary_key=True)
    CommentText = Column(String, max_length=255)
    user_id = Column(Integer, ForeignKey("Users.UserId"))

class ShaderTags(Base):
    __tablename__ = "ShaderTags"
    shaderId = Column(Integer, ForeignKey("Shaders.ShaderId"))
    tagId = Column(Integer, ForeignKey("Tags.TagId"))

class Tags(Base):
    __tablename__ = "Tags"
    TagId = Column(Integer, primary_key=True)
    TagName = Column(String,max_legnth=31 ,unique=True, index=True)



