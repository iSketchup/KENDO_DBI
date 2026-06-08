from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse

from database import engine
import models
from routers import user, shader, likes, comments, tags

# Erstellt alle Tabellen im Datenbank Schema (falls noch nicht vorhanden)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="myApp", description="myApp", version="1.0.0")

app.include_router(user.router)
app.include_router(shader.router)
app.include_router(shader.router_per_user)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(tags.router)
# Custome valdidation Error handler

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error.get("loc")[-1]
        error_msg = error.get("msg")
        errors.append({"field": field, "msg": error_msg})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
        "status": "validation_error ",
        "errors": errors
    })

@app.get("/")
def root():
    return {"Message": "Hello World\n Besuche /docs für die API"}


if __name__ == "__main__":
    import uvicorn
    import os
    from sslmake import create_ssl

    # Hier prüfen wir, ob die beiden Dateien auf der Festplatte existieren
    ssl_vorhanden = os.path.exists("key.pem") and os.path.exists("cert.pem")


    # TODO: Zertifikat erzeugen, falls keines vorhanden ist via os
    if not ssl_vorhanden:
        create_ssl() # Das SSL erzeugen.
        ssl_vorhanden = os.path.exists("key.pem") and os.path.exists("cert.pem")

    if ssl_vorhanden:
        print("SSL-Zertifikate gefunden. Es wird in den HTTPS-Modus gestartet...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            ssl_keyfile="key.pem",
            ssl_certfile="cert.pem"
        )