from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
import tempfile, shutil, os, git, json

app = FastAPI()

@app.get("/ping")
def ping():
    return JSONResponse(content={"message": "pong"})
