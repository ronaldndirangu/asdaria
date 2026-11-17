from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"


def site_headers():
    # Reads the "/*" rule from site/_headers so the preview sends the same headers as the host.
    headers, applies = [], False
    for line in (SITE / "_headers").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line[0].isspace():
            applies = line.strip() == "/*"
        elif applies and ":" in line:
            key, value = line.split(":", 1)
            headers.append((key.strip(), value.strip()))
    return headers


class PreviewServer(ThreadingHTTPServer):
    # Browsers open many connections at once; with the default backlog of 5, Windows refuses the excess.
    request_queue_size = 128


class PreviewHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
    }
    headers_to_send = site_headers()

    def end_headers(self):
        for key, value in self.headers_to_send:
            self.send_header(key, value)
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # Hosts answer missing addresses with 404.html, so the preview does too.
        page = SITE / "404.html"
        if code != 404 or not page.exists():
            return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404, message)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main():
    handler = partial(PreviewHandler, directory=str(SITE))
    with PreviewServer(("127.0.0.1", 4173), handler) as server:
        print("Preview: http://127.0.0.1:4173", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nPreview stopped.")


if __name__ == "__main__":
    main()
