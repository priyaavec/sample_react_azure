from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas
from .blob import upload_file, download_file, delete_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Azure CRUD Demo",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {"message": "CRUD API is running"}


@app.post("/items", response_model=schemas.ItemOut)
async def create_item(
    title: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):

    blob_name = None
    original_filename = None
    content_type = None

    if file:
        content = await file.read()

        blob_name = upload_file(
            content,
            file.filename,
            file.content_type
        )

        original_filename = file.filename
        content_type = file.content_type

    item = models.Item(
        title=title,
        description=description,
        blob_name=blob_name,
        original_filename=original_filename,
        content_type=content_type
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@app.get("/items", response_model=list[schemas.ItemOut])
def get_items(db: Session = Depends(get_db)):

    return db.query(models.Item).all()


@app.get("/items/{item_id}", response_model=schemas.ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.get(models.Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item


@app.put("/items/{item_id}", response_model=schemas.ItemOut)
async def update_item(
    item_id: int,
    title: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):

    item = db.get(models.Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    item.title = title
    item.description = description

    if file:

        if item.blob_name:
            delete_file(item.blob_name)

        content = await file.read()

        item.blob_name = upload_file(
            content,
            file.filename,
            file.content_type
        )

        item.original_filename = file.filename
        item.content_type = file.content_type

    db.commit()
    db.refresh(item)

    return item


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.get(models.Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    if item.blob_name:
        delete_file(item.blob_name)

    db.delete(item)
    db.commit()

    return {"message": "Item deleted"}


@app.get("/items/{item_id}/download")
def download(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.get(models.Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    if not item.blob_name:
        raise HTTPException(
            status_code=404,
            detail="No file attached"
        )

    data = download_file(item.blob_name)

    return StreamingResponse(
        BytesIO(data),
        media_type=item.content_type or "application/octet-stream",
        headers={
            "Content-Disposition":
            f'attachment; filename="{item.original_filename}"'
        }
    )
