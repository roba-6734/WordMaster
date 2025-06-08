from fastapi import FastAPI


app = FastAPI()


@app.get('/')
def index():
    return {"HomePage":"Welcome to my webapp"}


@app.post('/api/auth/register')
def register_user():
    pass

@app.post('/api/auth/login')
def login():
    pass

@app.get('/api/auth/user')
def get_user_info():
    pass

@app.post('/api/auth/logout')
def logout():
    pass
