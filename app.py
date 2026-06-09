"""
netlify/functions/app.py
─────────────────────────
Wraps the Flask app as a Netlify serverless function using
the serverless-wsgi adapter pattern.

This is the entry point Netlify calls for every request.
"""
import sys
import os

# Add project root to path so we can import our Flask app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app

flask_app = create_app()


def handler(event, context):
    """
    Netlify Functions entry point.
    Adapts AWS Lambda-style event/context to WSGI.
    """
    from werkzeug.test import Client
    from werkzeug.wrappers import Response

    # Build WSGI environ from Netlify event
    path    = event.get("path", "/")
    method  = event.get("httpMethod", "GET")
    headers = event.get("headers", {}) or {}
    body    = event.get("body", "") or ""
    qs      = event.get("queryStringParameters", {}) or {}

    if qs:
        path += "?" + "&".join(f"{k}={v}" for k, v in qs.items())

    environ = {
        "REQUEST_METHOD":  method,
        "PATH_INFO":       path,
        "CONTENT_TYPE":    headers.get("content-type", ""),
        "CONTENT_LENGTH":  str(len(body.encode("utf-8"))),
        "HTTP_HOST":       headers.get("host", "localhost"),
        "wsgi.input":      __import__("io").BytesIO(body.encode("utf-8")),
        "wsgi.errors":     sys.stderr,
        "wsgi.url_scheme": "https",
        "SERVER_NAME":     "localhost",
        "SERVER_PORT":     "443",
    }

    for k, v in headers.items():
        key = "HTTP_" + k.upper().replace("-", "_")
        environ[key] = v

    response_started = {}

    def start_response(status, response_headers, exc_info=None):
        response_started["status"] = status
        response_started["headers"] = dict(response_headers)

    result = flask_app(environ, start_response)
    body_out = b"".join(result)

    status_code = int(response_started["status"].split(" ")[0])

    return {
        "statusCode": status_code,
        "headers":    response_started.get("headers", {}),
        "body":       body_out.decode("utf-8", errors="replace"),
    }