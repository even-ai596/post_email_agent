from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.post("/stream")
async def stream(request: Request):
    body = await request.body()
    return {
        "IP": request.client.host,
        "port": request.client.port,
        "headers": request.headers,
        "body": body,
        "method": request.method,
        "url": request.url,
        "cookies": request.cookies,
    }

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, World!"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("x:app", host="0.0.0.0", port=8000, reload=True)