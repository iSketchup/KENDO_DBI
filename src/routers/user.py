import bcrypt
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator, Field, ConfigDict
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.base import BaseAPI
from auth import verify_api_key

from passlib.context import CryptContext # Bibliothek für das Hashing


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



router = APIRouter(prefix="/user", tags=["User"])




class UserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    UserName: str = Field(..., min_length=1, max_length=31, alias="UserName") # Hier wird eine Alias für das JSON gesetzt
    passwd: str

    @field_validator("UserName")
    @classmethod
    def name_with_whitespace(cls, value:str):
        if not ' ' in value:
            return value
        else:
            raise ValueError("Name must not contain whitespaces")


# Response-Klasse für das Login
class LoginRequest(BaseModel):
    UserName: str
    passwd: str


class UserResponse(UserCreate):
    UserId: int
    is_admin: bool

    class ConfigDict:
        from_attributes = True



@cbv(router)
class UsersAPI(BaseAPI):
    db: Session = Depends(get_db)

    api_key: str = Depends(verify_api_key)


    @router.get("/{username}", response_model=UserResponse)
    def usernames(self, username : str):
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == username).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' nicht gefunden")

        return user

    @router.post("/login", response_model=UserResponse)
    def login(self, request: LoginRequest):

        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == request.UserName).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")



        ## ToDo: da auf der pos seite momentan nicht gehasht wird kan ndas  oben nie funktionieren

        # Prüfen, ob es sich überhaupt um einen gültigen Bcrypt-Hash in der DB handelt
        is_hashed = user.passwd.startswith(("$2a$", "$2b$", "$2y$")) and len(user.passwd) == 60

        if is_hashed:
            result = bcrypt.checkpw(request.passwd.encode("utf-8"), user.passwd.encode("utf-8"))
        else:

            result = (request.passwd == user.passwd)


            if result:
                salt = bcrypt.gensalt()
                user.passwd = bcrypt.hashpw(request.passwd.encode("utf-8"), salt).decode("utf-8")
                self.db.commit()

        if not result:
            raise HTTPException(status_code=401, detail="Login is invalid")

        return user


    @router.post("/", response_model=UserResponse)
    def new_user(self, item: UserCreate):
        # Hier wird nachgeschaut, ob ein User mit diesen Namen schon vorhanden ist.
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == item.UserName).first()


        if user:
            raise HTTPException(status_code=409, detail="Es ist nicht erlaubt User"
                                                        "mit gleichen Namen zu erstellen")


        is_already_hashed = item.passwd.startswith(("$2a$", "$2b$", "$2y$")) and len(item.passwd) == 60

        if not is_already_hashed:
            # Wenn es im Klartext kommt (z.B. aus Swagger), wird es hier im Backend gehasht
            salt = bcrypt.gensalt()
            hashed_bytes = bcrypt.hashpw(item.passwd.encode("utf-8"), salt)
            passwd = hashed_bytes.decode("utf-8")
        else:
            # Falls es schon gehasht vom C# Programm ankommt.s
            passwd = item.passwd



        newuser = models.DBUsers(UserName=item.UserName, passwd=passwd)
        self.db.add(newuser)
        self.db.commit()
        self.db.refresh(newuser)
        return newuser
        # Muss zurückgegeben werden, damit der Validationhandler es auch validieren kann.


    @router.put("/", response_model=UserResponse)
    def change_user(self, item: UserCreate, username: str):
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == username).first()
        # Boolsche Flag um zu prüfen ob man nur sein Passwort verändern möchte

        if not user:
            raise HTTPException(status_code=404, detail=f"Der User mit der ID: {username}"
                                                        f" wurde nicht gefunden")


        new_username = item.UserName if item.UserName else user.UserName
        new_passwd = item.passwd if item.passwd else user.passwd

        if user.UserName != new_username:
            existing = (self.db.query(models.DBUsers)
                        .filter(models.DBUsers.UserName == new_username).first())
            if existing:
                raise HTTPException(status_code=409, detail="Users with the same name"
                                                            " are not permitted")



        user.UserName = new_username
        user.passwd = new_passwd

        self.db.commit()
        self.db.refresh(user)
        return user


    @router.delete("/", status_code=204)
    def del_user(self, username: str):
        user = self.db.query(models.DBUsers).filter(models.DBUsers.UserName == username).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"Der User mit dem Namen: {username}"
                                                        f" wurde nicht gefunden")
        self.db.delete(user)
        self.db.commit()