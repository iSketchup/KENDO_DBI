from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.base import BaseAPI

router = APIRouter(prefix="/user", tags=["User"])

class UserCreate(BaseModel):
    UserName: str = Field(..., min_length=1, max_length=31)
    passwd: str = Field(...,min_length=8)

    @field_validator("UserName")
    @classmethod
    def name_with_whitespace(cls, value:str):
        if not ' ' in value:
            return value
        else:
            raise ValueError("Name must not contain whitespaces")


class UserResponse(UserCreate):
    UserId: int

    class ConfigDict:
        from_attributes = True



@cbv(router)
class UsersAPI(BaseAPI):
    db : Session = Depends(get_db)

    @router.get("/", response_model=list[UserResponse])
    def users(self):
        return self.db.query(models.DBUsers).all()


    @router.post("/", response_model=UserResponse)
    def new_user(self, item: UserCreate):
        # Hier wird nachgeschaut, ob ein User mit diesen Namen schon vorhanden ist.
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == item.UserName).first()


        if user:
            raise HTTPException(status_code=409, detail="Es ist nicht erlaubt User"
                                                        "mit gleichen Namen zu erstellen") #

        newuser = models.DBUsers(UserName=item.UserName, passwd=item.passwd)
        self.db.add(newuser)
        self.db.commit()
        self.db.refresh(newuser)
        return newuser
        # Muss zurückgegeben werden, damit der Validationhandler es auch validieren kann.


    @router.put("/", response_model=UserResponse)
    def change_user(self, item: UserCreate, item_id: int):
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserId == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Der User mit der ID: {item_id}"
                                                        f" wurde nicht gefunden")

        user.UserName = item.UserName
        user.passwd = item.passwd

        self.db.commit()
        self.db.refresh(user)
        return user


    @router.delete("/", status_code=204)
    def del_user(self, item_id: int):
        item = self.db.query(models.DBUsers).filter(models.DBUsers.UserId == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Der User mit der ID: {item_id}"
                                                        f" wurde nicht gefunden")
        self.db.delete(item)
        self.db.commit()