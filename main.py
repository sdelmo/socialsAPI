from fastapi import FastAPI

# Create instance

app = FastAPI()

# A path operation

@app.get("/")
async def root():
    return {"message": "Hello World"}
