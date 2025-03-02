
# Plotter

Projekt ten polega na stworzeniu robota zdolnego do pisania na kartce papieru w sposób przypominający pismo odręczne. Styl pisma użytkownika jest rejestrowany za pomocą aplikacji przeglądarkowej, gdzie użytkownik wpisuje litery, które są zapisywane jako obrazy w formacie .png. Obrazy te są następnie przekształcane na pliki .gcode, które zawierają instrukcje dla robota dotyczące ruchów w osiach X i Y oraz sterowania długopisem.

Robot wykorzystuje mechanizm poruszający się w dwóch osiach za pomocą silników krokowych, a serwomechanizm odpowiada za podnoszenie i opuszczanie długopisu. Dzięki algorytmowi synchronizującemu ruchy w osiach X i Y robot zapewnia płynność i dokładność ruchu.




## Technologie

Projekt został zaimplementowany w języku Python i działa na platformie Raspberry Pi. Do jego realizacji wykorzystano następujące biblioteki i technologie:

Python:
 - os – do nawigacji po katalogach i plikach
 - http.server – do obsługi żądań HTTP
 - json i base64 – do przetwarzania danych użytkownika
 - cv2 (OpenCV) – do konwersji obrazów na pliki .gcode
 - numpy – do obróbki danych graficznych
 - RPi.GPIO – do sterowania silnikami krokowymi i serwomechanizmem
 - time – do synchronizacji ruchów robota

Frontend (Klient):
 - HTML, JavaScript – do obsługi interfejsu użytkownika w przeglądarce


## Uruchomienie

#### Uruchomienie serwera:
 - Na Raspberry Pi należy uruchomić serwer wpisując w terminalu:

```bash
  ./server.py
```

#### Połączenie z klientem:
 - Na komputerze w tej samej sieci otwórz przeglądarkę i wejdź na adres:
```bash
  http://<IP_RASPBERRY_PI>:8080
```
 - Tutaj użytkownik może wprowadzić własny styl pisma lub skorzystać z wcześniej zapisanych czcionek.

#### Wysyłanie tekstu do robota:
 - Po wybraniu czcionki i wprowadzeniu tekstu można wysłać go do plottera, który zapisze tekst na kartce.





## Zrzuty ekranu
<p align="center">
  <img src="https://github.com/user-attachments/assets/3d0894ce-529b-4fa5-ad6d-6719639b0fa7" width="40%">
  <img src="https://github.com/user-attachments/assets/76a31dff-0641-4722-a0f1-d7ebc5676809" width="37.58%">
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/0a65e97c-15e5-497d-aa4a-20039e769dbb" width="77%">
</p>


https://github.com/user-attachments/assets/4fece059-0e7a-4e05-93c3-4711c3c8b245

