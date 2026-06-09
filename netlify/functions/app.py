import sys
import os
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app

flask_app = create_app()


def handler(event, context):
    path    = event.get("path", "/")
    method  = event.get("httpMethod", "GET")
    headers = event.get("headers") or {}
    body    = event.get("body") or ""
    qs      = event.get("queryStringParameters") or {}

    if qs:
        path += "?" + "&".join(f"{k}={v}" for k, v in qs.items())

    body_bytes = body.encode("utf-8") if isinstance(body, str) else body

    environ = {
        "REQUEST_METHOD":   method,
        "PATH_INFO":        path,
        "QUERY_STRING":     "",
        "CONTENT_TYPE":     headers.get("content-type", ""),
        "CONTENT_LENGTH":   str(len(body_bytes)),
        "HTTP_HOST":        headers.get("host", "localhost"),
        "wsgi.input":       io.BytesIO(body_bytes),
        "wsgi.errors":      sys.stderr,
        "wsgi.url_scheme":  "https",
        "wsgi.multithread":  False,
        "wsgi.multiprocess": False,
        "wsgi.run_once":     False,
        "SERVER_NAME":      "localhost",
        "SERVER_PORT":      "443",
        "SERVER_PROTOCOL":  "HTTP/1.1",
    }

    for k, v in headers.items():
        key = "HTTP_" + k.upper().replace("-", "_")
        environ[key] = v

    response_data = {}

    def start_response(status, response_headers, exc_info=None):
        response_data["status"]  = status
        response_data["headers"] = dict(response_headers)

    result   = flask_app.wsgi_app(environ, start_response)
    body_out = b"".join(result)

    status_code = int(response_data.get("status", "200").split(" ")[0])

    return {
        "statusCode": status_code,
        "headers":    response_data.get("headers", {}),
        "body":       body_out.decode("utf-8", errors="replace"),
    }