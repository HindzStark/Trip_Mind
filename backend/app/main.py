from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlalchemy import text

from app.db.session import engine

from app.db.base import Base

                                                        

                                                                 

import app.models              

@asynccontextmanager

async def lifespan(app: FastAPI):

    

                     

    try:

        with engine.connect() as conn:

            conn.execute(text("SELECT 1"))

        print("Yay! Database is connected and happy!  Let's go! ")

    except Exception as e:

        print(f"Database connection failed: {e}")

        raise

                                            

                                                         

    Base.metadata.create_all(bind=engine)

    print("Database tables are all created and ready to rock! ")

    yield

                      

    engine.dispose()

from fastapi.middleware.cors import CORSMiddleware


app    =    FastAPI(

    title="TripMind",

    lifespan=lifespan,

)


app.add_middleware(  

    CORSMiddleware,

    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

                           

                                     

                                                                    

 

                                                                     

from app.routes.trip import router as trip_router

app.include_router(trip_router)

from app.routes.auth import router as auth_router

app.include_router(auth_router)

from app.routes.user import router as user_router

app.include_router(user_router)

@app.get("/")

def root():

    return {"message": "TripMind API Running"}
