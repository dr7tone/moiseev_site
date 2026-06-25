from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/book", StaticFiles(directory="book"), name="book")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def general_window():
    return FileResponse("index.html")







if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', reload=True)