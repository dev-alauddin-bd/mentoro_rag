from fastapi import FastAPI

app= FastAPI()

# root endpoint
@app.get('/')
def root():
    return {
        "message": "Mentoro RAG is running!",
        "status": "success"
    }



