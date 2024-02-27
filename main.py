import uvicorn
from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.dependencies.db import get_db
from src.routes import images, users, comment, auth


app = FastAPI()

app.include_router(users.router)
app.include_router(images.router)
app.include_router(comment.router)
app.include_router(auth.router)



@app.post("/halthchecker")
async def halthchecker(db: Session=Depends(get_db)):
    """
    The halthchecker function is used to check if the database connection is working.
    It will return a message with the status code 200 if everything works fine, otherwise it 
    will return an HTTPException 500.
    
    :param db: Session: Inject the database session into the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        result = db.execute(text('SELECT 1')).fetchone()

        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        
    except Exception as err:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
    return {"message": "Wellcome to ImageShare"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)