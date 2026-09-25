import datetime
import http.client
import http.server
import json
import os

BACKEND_HOST = os.environ.get("BACKEND_HOST", "bunker")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8080"))
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8080"))

CHAT_PATHS = {"/v1/chat/completions", "/chat/completions"}


def build_datetime_note():
    now = datetime.datetime.now(datetime.timezone.utc)
    return (
        f"Current date and time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}. "
        "You have no internet access and no tools available; never attempt a "
        "tool call for date/time or anything else, just use this information "
        "directly."
    )


def inject_datetime(body: bytes) -> bytes:
    try:
        payload = json.loads(body)
    except ValueError:
        return body

    messages = payload.get("messages")
    if not isinstance(messages, list):
        return body

    note = build_datetime_note()
    if messages and messages[0].get("role") == "system":
        messages[0]["content"] = f"{messages[0].get('content', '')}\n\n{note}"
    else:
        messages.insert(0, {"role": "system", "content": note})

    payload["messages"] = messages
    return json.dumps(payload).encode("utf-8")


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _proxy(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        if self.command == "POST" and self.path in CHAT_PATHS and body:
            body = inject_datetime(body)

        headers = {
            k: v
            for k, v in self.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        headers["Content-Length"] = str(len(body))
        headers["Connection"] = "close"

        conn = http.client.HTTPConnection(BACKEND_HOST, BACKEND_PORT)
        try:
            conn.request(self.command, self.path, body=body, headers=headers)
            resp = conn.getresponse()

            self.send_response(resp.status, resp.reason)
            for k, v in resp.getheaders():
                if k.lower() in ("transfer-encoding", "connection"):
                    continue
                self.send_header(k, v)
            self.send_header("Connection", "close")
            self.end_headers()

            while True:
                chunk = resp.read1(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
        finally:
            conn.close()

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), ProxyHandler)
    server.serve_forever()
