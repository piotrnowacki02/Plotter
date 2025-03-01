from http.server import SimpleHTTPRequestHandler, HTTPServer
from converter import *  # Importowanie klasy PngToGcode
from plotter4 import *
import os
import json
import base64

HOST = "0.0.0.0"
PORT = 8080
FONTS_DIR = "./fonts"

class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/save-letter":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            font_name = data["fontName"]
            letter = data["letter"]
            image_data = data["image"]

            # Dekodowanie danych obrazu
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

            # Tworzenie folderu czcionki
            font_folder = os.path.join(FONTS_DIR, font_name)
            os.makedirs(font_folder, exist_ok=True)

            # Zapis pliku obrazu
            file_path = os.path.join(font_folder, f"{letter}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            input_image_path = file_path
            output_gcode_path = file_path[0:-4]

            png_to_gcode = PngToGcode()

            # Ustawianie parametrów
            png_to_gcode.input = input_image_path
            png_to_gcode.output = output_gcode_path
            png_to_gcode.gcode_height = 200  # Wysokość w mm
            png_to_gcode.gcode_width = 100   # Szerokość w mm
            png_to_gcode.pen_up = "M3"       # Przykładowa komenda podniesienia pióra
            png_to_gcode.pen_down = "M5"     # Przykładowa komenda opuszczenia pióra

            png_to_gcode.gen_all()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/plotter":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            text = data.get("text")
            #font_name = data.get("fontName")
#             font_name = FONTS_DIR+"/test"
            font_name = FONTS_DIR+"/"+data.get("fontName")

            #run(text, font_name)
            # Odpowiedz klientowi
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Tekst otrzymano.")
        elif self.path == "/list-fonts":
            fonts = [d for d in os.listdir(FONTS_DIR) if os.path.isdir(os.path.join(FONTS_DIR, d))]
            self.send_response(200)
            #print(fonts)
            self.end_headers()
            self.wfile.write(json.dumps(fonts).encode())
        else:
            self.send_response(404)
            self.end_headers()

# Tworzenie serwera
os.makedirs(FONTS_DIR, exist_ok=True)
server = HTTPServer((HOST, PORT), MyRequestHandler)
print(f"Serwer działa na http://{HOST}:{PORT}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Zatrzymanie serwera.")
finally:
    server.server_close()
    print("Serwer zamknięty.")