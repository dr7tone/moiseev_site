from urllib import response

from fastapi import FastAPI, Form, HTTPException, Depends, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os
from dotenv import load_dotenv
load_dotenv()
secret_key = os.environ.get("secret_key")
admin_login = os.environ.get("admin_login")
admin_password = os.environ.get("admin_password")
engine = create_async_engine('sqlite+aiosqlite:///feedback.db')


from authx import AuthX, AuthXConfig

config = AuthXConfig()
config.JWT_SECRET_KEY = secret_key
config.JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)



app = FastAPI(title="Мой первый API", version="1.0", docs_url=None, 
    redoc_url=None,
    openapi_url=None )
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class feedbackModel(Base):
    __tablename__ = 'feedback'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    phone: Mapped[str]
    message: Mapped[str]

class reviewModel(Base):
    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    message: Mapped[str]
    rating: Mapped[str]


# @app.post("/setup_db")
# async def setup_db():
#     try:
#         async with engine.begin() as connection:
#             await connection.run_sync(Base.metadata.drop_all)
#             await connection.run_sync(Base.metadata.create_all)
#         return {"all good": "true"}
#     except:
#         return {"all no good"}
    


app.mount("/book", StaticFiles(directory="book"), name="book")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def general_window():
    return FileResponse("index.html")

@app.post("/submit-feedback/")
async def submit_feedback(
    session: SessionDep,
    name: Annotated[str, Form()],
    message: Annotated[str, Form()],
    rating: Annotated[Optional[int], Form()] = None 
):
    if rating is None:
        rating = 0 
    new_item = reviewModel(
        name = name,
        message = message,
        rating = rating
    )
    session.add(new_item)
    await session.commit()
    print(f"Новый отзыв от {name}: {message} (оценка: {rating})")
    return {"status": "success", "message": "Спасибо за отзыв!"}

@app.post("/feedback/")
async def feedback(
    session: SessionDep,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    message: Annotated[Optional[str], Form()] = None ):


    new_item = feedbackModel(
        name = name,
        phone = phone,
        message = message
    )
    session.add(new_item)
    await session.commit()
    print(f"Новый фитбэк {name}: {message} (его телефон: {phone})")
    return {"status": "success", "message": "Спасибо!"}





from datetime import date
from typing import Annotated, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fastui.forms import fastui_form
from fastui import FastUI, AnyComponent,  prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field



class User(BaseModel):
    id: int
    name: str
    dob: date = Field(title='Date of Birth')


class admins(BaseModel):
    login: str
    password: str

class check_admin(BaseModel):
    login: str = Field(title="login")
    password: str = Field(title="password")

True_admin = admins(login=str(admin_login), password=str(admin_password))



@app.post("/api/admin/send")
async def admin_check(response: Response, request: Request, session: SessionDep, form: Annotated[check_admin, fastui_form(check_admin)]) -> list[AnyComponent]:
    print(f'{form=}')
    if form.login == True_admin.login and form.password == True_admin.password:
        token = security.create_access_token(uid="1")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return [
        c.FireEvent(
            event=GoToEvent(url=f'/admin/panel?token={token}')
        )
        ]
    raise HTTPException(status_code=401)


class FeedbackDisplay(BaseModel):
    name: str
    phone: str
    message: str

class reviewDisplay(BaseModel):
    name: str
    message: str
    rating: str

@app.get("/api/admin/panel", dependencies=[Depends(security.access_token_required)], response_model=FastUI, response_model_exclude_none=True)
async def admin_panel(session: SessionDep) -> list[AnyComponent]:
    query = select(feedbackModel)
    result = await session.execute(query)
    l = result.scalars().all()
    table_data = [
        FeedbackDisplay(
            name=fb.name,
            phone=str(fb.phone),
            message=str(fb.message)
        ) for fb in l
    ]
    query2 = select(reviewModel)
    result2 = await session.execute(query2)
    l2 = result2.scalars().all()
    table_data2 = [
        reviewDisplay(
            name=fb2.name,
            message=fb2.message, 
            rating=fb2.rating,
        ) for fb2 in l2
    ]
    if table_data:
        return [
            c.Page(
                components=[
                    c.Heading(text='feedback', level=2),
                    c.Table(
                        data=table_data,
                        columns=[
                            DisplayLookup(field='name'),
                            DisplayLookup(field='message'),
                            DisplayLookup(field='phone'),
                        ],
                    ),
                    c.Table(
                        data=table_data2,
                        columns=[
                            DisplayLookup(field='name'),
                            DisplayLookup(field='message'),
                            DisplayLookup(field='rating'),
                        ],
                    ),
                ]
            ),
        ]
    else:
        return [
            c.Page(
                components=[
                    c.Heading(text='feedback', level=2),
                ]
            ),
        ]


@app.get("/api/admin", response_model=FastUI, response_model_exclude_none=True)
def admin():
    return [
        c.Page( 
            components=[
                c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
                c.Heading(text='admin', level=2), 
                c.ModelForm(
                    model = check_admin,
                    submit_url= "/api/admin/send"
                )
            ]
        ),
    ]
@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='admin_panel'))





if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', reload=True)