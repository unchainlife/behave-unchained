import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uuid
import uvicorn
import threading
import time
from behave import fixture, use_fixture
import re

def before_feature(context, feature):
    if "skip" in feature.tags:
        feature.skip("Marked with @skip")
    context.functions = {
        "UUID": uuid.uuid4
    }

def before_scenario(context, scenario):
    if "skip" in scenario.tags:
        scenario.skip("Marked with @skip")
    context.values = {}
    context.results = {}

def convert_comma_separated_key_value_into_dict(args):
    return { k: v for (k, v) in [x.split("=") for x in args.split(",")] } if args else {}

def before_tag(context, tag):
    http_server_match = re.match(r"^http_server(\(([^\)]*)\))?$", tag)
    if http_server_match:
        args = convert_comma_separated_key_value_into_dict(http_server_match.group(2))
        host = args.get("host", "127.0.0.1")
        port = int(args.get("port", 8000))
        use_fixture(http_server, context, host, port)

@fixture
def http_server(context, host, port):
    """
    Starts a FastAPI server around the fixture
    """
    app = FastAPI()

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    async def http_response(path_name: str, request: Request, response: Response):
        body = await request.body()
        correlation_id = request.headers.get("x-correlation-id", "")
        request_id = request.headers.get("x-request-id", "")
        content = {
            "message": "Echo",
            "request": {
                "method": request.method,
                "path": request.url.path,
                "headers": { k: v for (k, v) in request.headers.items() },
                "query_params": { k: v for (k, v) in request.query_params.items() },
                "body": body.decode("utf-8"),
            }
        }
        headers = { k: v for (k, v) in request.headers.items() if k.startswith("x-")}
        return JSONResponse(
            content=content,
            status_code=200,
            headers=headers,
        )

    def run_server(stop_event:threading.Event):
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)

        loop = asyncio.new_event_loop()
        task = loop.create_task(server.serve())
        while not stop_event.is_set():
            loop.run_until_complete(asyncio.sleep(0.1))
        task.cancel()
        loop.run_until_complete(server.shutdown())

    stop_event = threading.Event()
    thread = threading.Thread(target=run_server, args=(stop_event,))
    thread.start()
    time.sleep(1)
    yield
    stop_event.set()
    thread.join(timeout=5)

print (__name__)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)