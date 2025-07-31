from http.client import HTTPException
from fastapi import FastAPI, Depends, Query
from starlette import status
from starlette.requests import Request
from models import Post


app = FastAPI()

db = []
log_user = []

def log_client(request: Request):
    log_user.append(request.headers)

app = FastAPI(dependencies=[Depends(log_client)])

@app.get('/log_user')
async def print_log_user():
    return {'user': log_user}

async def pagination_path_func(page: int):
    if page < 0:
        raise HTTPException(status_code=404,
                            detail='Page does not exist')
    if page == 0:
        raise HTTPException(status_code=400,
                            detail='Invalid page value')


async def get_post_or_404(id: int):
    try:
        return db[id]
    except IndexError:
        raise
    HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def pagination_func(limit: int = Query(10, ge=0), page: int = 1):
    return {'limit': limit, 'page': page}


async def sub_dependency(request: Request) -> str:
    return request.method


async def main_dependency(
        sub_dependency_value: str = Depends(sub_dependency)) -> str:
    return sub_dependency_value


@app.get('/test/')
async def test_endpoint(test: str = Depends(main_dependency)):
    return test


@app.get('/message/{id}')
async def get_message(post: Post = Depends(get_post_or_404)):
    return post


@app.post('/message', status_code=status.HTTP_201_CREATED)
async def create_message(post: Post) -> str:
    post.id = len(db)
    db.append(post)
    return f'Message created!'


@app.get('/messages', dependencies= [Depends(pagination_path_func)])
async def all_messages(
        pagination: dict = Depends(pagination_func)):
    return {'message': pagination}

@app.get('/comments')
async def all_comments(
        pagination: list = Depends(pagination_func)):
    return {'comments': pagination}

