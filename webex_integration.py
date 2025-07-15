import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from PySide6.QtCore import Signal, QObject, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout
import os
from http.server import SimpleHTTPRequestHandler

# Webex OAuth2 credentials
CLIENT_ID = "C2b7139e803362d903b975c245afe0e6edec2848b7653f4428e3d9a1e9195236a"
CLIENT_SECRET = "84d74ca17fb23e3c93a011d77b5932c247036ad129e92a0987b9616fb7cd7a9e"
REDIRECT_URI = "http://localhost:8000/viewer_assets/webex.html"
AUTH_URL = (
    f"https://webexapis.com/v1/authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope=spark%3Aall%20spark%3Akms"
)
TOKEN_URL = "https://webexapis.com/v1/access_token"

class OAuthCodeReceiver(QObject):
    code_received = Signal(str)

    def __init__(self):
        super().__init__()
        self._server = None
        self._thread = None

    def start(self):
        def handler_factory():
            parent = self
            class OAuthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    parsed = urllib.parse.urlparse(self.path)
                    if parsed.path == "/viewer_assets/webex.html":
                        params = urllib.parse.parse_qs(parsed.query)
                        code = params.get("code", [None])[0]
                        if code:
                            # Notify via Qt signal
                            parent.code_received.emit(code)
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(b"<html><body><h2>Webex login successful. You may close this window.</h2></body></html>")
                        else:
                            self.send_response(400)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()
                def log_message(self, format, *args):
                    return  # Suppress logging
            return OAuthHandler

        self._server = HTTPServer(('localhost', 8000), handler_factory())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

class AssetHTTPServer:
    """Serves the viewer_assets directory on localhost:8000."""
    def __init__(self, directory):
        self.directory = directory
        self._server = None
        self._thread = None

    def start(self):
        if self._server:
            return  # Already running
        handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=self.directory, **kwargs)
        self._server = HTTPServer(('localhost', 8001), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

class WebexLoginWidget(QWidget):
    access_token_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.webview = QWebEngineView()
        layout = QVBoxLayout(self)
        layout.addWidget(self.webview)
        self.setLayout(layout)

        # Start HTTP server for viewer_assets
        assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'viewer_assets'))
        self.asset_server = AssetHTTPServer(directory=assets_path)
        self.asset_server.start()

        self.oauth_receiver = OAuthCodeReceiver()
        self.oauth_receiver.code_received.connect(self.on_code_received)
        self.oauth_receiver.start()

        self.webview.load(QUrl(AUTH_URL))

    def on_code_received(self, code):
        # Exchange code for access token
        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        try:
            resp = requests.post(TOKEN_URL, data=data)
            resp.raise_for_status()
            token = resp.json().get('access_token')
            if token:
                self.access_token_received.emit(token)
            else:
                print("Failed to get access token:", resp.text)
        except Exception as e:
            print("Error exchanging code for token:", e)
        finally:
            self.oauth_receiver.stop()

    def load_meeting(self, meeting_url):
        """Load a Webex meeting URL in the QWebEngineView."""
        self.webview.load(QUrl(meeting_url))

# Example usage (for testing)
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = WebexLoginWidget()
    widget.access_token_received.connect(lambda token: print("Access token:", token))
    widget.show()
    sys.exit(app.exec()) 