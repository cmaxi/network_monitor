import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse
from settings import DATASTORE_APP_ADDRESS

app = FastAPI()


@app.route('/{_:path}')
async def https_redirect(request: Request):
    return RedirectResponse(request.url.replace(scheme='http'))

if __name__ == '__main__':
    uvicorn.run('https_redirect:app', port=8100, host='0.0.0.0')