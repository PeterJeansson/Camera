# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal, Photo, Base, engine
from schemas import PhotoResponse, PhotoMetadata
import io
import mimetypes
from typing import List
from datetime import datetime  # Ensure datetime is imported

app = FastAPI()

# Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST endpoint to upload a photo
@app.post("/upload", response_model=PhotoResponse)
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")
    
    # Read the file content
    content = await file.read()
    
    # Get current UTC time
    utc_now = datetime.utcnow()
    
    # Create a new Photo instance
    photo = Photo(
        filename=file.filename,
        content=content,
        upload_time=utc_now  # Explicitly set upload_time
    )
    
    # Add and commit to the database
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    return photo  # Pydantic model will handle serialization

# GET endpoint to retrieve all photos metadata
@app.get("/photos", response_model=List[PhotoMetadata])
def get_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos  # Pydantic model will handle serialization

# GET endpoint to retrieve a specific photo by ID
@app.get("/photos/{photo_id}")
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    
    # Determine the MIME type based on the filename
    mime_type, _ = mimetypes.guess_type(photo.filename)
    if not mime_type:
        mime_type = "application/octet-stream"
    
    return StreamingResponse(io.BytesIO(photo.content), media_type=mime_type)

# Serve static files (e.g., HTML, CSS, JS)
from fastapi.staticfiles import StaticFiles
import os

# Ensure the 'static' directory exists
if not os.path.isdir("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
