import os
import RPi.GPIO as GPIO
import time

# Konfiguracja pinów GPIO
X_DIR = 27  # Kierunek dla osi X
X_STEP = 17  # Kroki dla osi X
Y_DIR = 23  # Kierunek dla osi Y
Y_STEP = 22  # Kroki dla osi Y
servo_pin = 25

# Konfiguracja silnika
STEP_DELAY = 0.0003  # Opóźnienie między krokami (sekundy)
STEPS_PER_MM = 100  # Liczba kroków na 1 mm

FRAME_WIDTH = 15
FRAME_HEIGHT = 30
LEADING = 5
FRAMES_IN_LINE = 16

# Inicjalizacja PWM i GPIO
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(X_DIR, GPIO.OUT)
    GPIO.setup(X_STEP, GPIO.OUT)
    GPIO.setup(Y_DIR, GPIO.OUT)
    GPIO.setup(Y_STEP, GPIO.OUT)
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)  # Częstotliwość PWM 50 Hz
    pwm.start(0)
    return pwm

def cleanup_gpio(pwm):
    pwm.stop()
    GPIO.cleanup()

def set_angle(pwm, angle):
    duty_cycle = 2 + (angle / 18)  # Przeliczanie kąta na wartość PWM
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

def pen_up(pwm):
    set_angle(pwm, 180)

def pen_down(pwm):
    set_angle(pwm, 0)

"""
Funkcja sterująca silnikami krokowymi w osiach X i Y.

Parametry:
x_steps (int): Liczba kroków do wykonania w osi X (wartości dodatnie dla ruchu w prawo, ujemne dla lewo).
y_steps (int): Liczba kroków do wykonania w osi Y (wartości dodatnie dla ruchu w górę, ujemne dla dół).
"""
def move_motors(x_steps, y_steps):

    GPIO.output(X_DIR, GPIO.HIGH if x_steps > 0 else GPIO.LOW) # jeżeli x_steps > 0 to idziemy w prawo, w przeciwnym wypadku w lewo
    GPIO.output(Y_DIR, GPIO.HIGH if y_steps > 0 else GPIO.LOW) # jeżeli y_steps > 0 to idziemy w górę, w przeciwnym wypadku w dół

    x_steps = abs(x_steps) # wartość bezwzględna z liczby kroków w każdym kierunku
    y_steps = abs(y_steps)

    max_steps = max(x_steps, y_steps) # maksymalna liczba kroków w obu osiach
    x_counter = 0 # licznik kroków w osi X
    y_counter = 0 # licznik kroków w osi Y

    for _ in range(max_steps):
        # Wykonanie kroku w osi X
        if x_counter < x_steps:
            GPIO.output(X_STEP, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(X_STEP, GPIO.LOW)
            time.sleep(STEP_DELAY)
            x_counter += 1

        # Wykonanie kroku w osi Y
        if y_counter < y_steps:
            GPIO.output(Y_STEP, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(Y_STEP, GPIO.LOW)
            time.sleep(STEP_DELAY)
            y_counter += 1


"""
Funkcja przetwarzająca plik G-code i wykonująca ruch robota na podstawie zawartych w nim komend.

Parametry:
filename (str): Ścieżka do pliku G-code.
FRAME_X_START (float): Aktualna pozycja początkowa w osi X.
FRAME_Y_START (float): Aktualna pozycja początkowa w osi Y.
pwm (PWM): Obiekt PWM do sterowania serwomechanizmem.
"""
def process_gcode(filename, FRAME_X_START, FRAME_Y_START, pwm):
    current_x = FRAME_X_START # Aktualna pozycja robota w osi X
    current_y = FRAME_Y_START # Aktualna pozycja robota w osi Y

    try:
        with open(filename, 'r') as file:
            for line in file:
                command = line.split(';')[0].strip()  # Ignorowanie komentarzy
                if command.startswith('M3'):  # Podniesienie pióra
                    pen_up(pwm)
                elif command.startswith('M5'):  # Opuszczenie pióra
                    pen_down(pwm)
                elif command.startswith('G0') or command.startswith('G1'):  # Ruch w X i Y
                    x_pos = command.find('X') # Wyszukiwanie współrzędnych X i Y
                    y_pos = command.find('Y')
                    
                    # Współrzędne docelowe
                    x_target = float(command[x_pos + 1:].split()[0]) if x_pos != -1 else current_x 
                    y_target = float(command[y_pos + 1:].split()[0]) if y_pos != -1 else current_y 

                    # Przeliczanie współrzędnych na kroki
                    x_target = FRAME_X_START + (FRAME_WIDTH * x_target / 100)
                    y_target = FRAME_Y_START + (FRAME_HEIGHT * y_target / 200)

                    x_steps = int((x_target - current_x) * STEPS_PER_MM)
                    y_steps = int((y_target - current_y) * STEPS_PER_MM)

                    # Wykonanie ruchu
                    move_motors(x_steps, y_steps)

                    # Aktualizacja pozycji robota
                    current_x = x_target
                    current_y = y_target
    finally:
        # Przejście do narożnika następnej ramki po zakończeniu pracy
        x_target = FRAME_X_START + FRAME_WIDTH
        y_target = FRAME_Y_START
        x_steps = int((x_target - current_x) * STEPS_PER_MM)
        y_steps = int((y_target - current_y) * STEPS_PER_MM)
        move_motors(x_steps, y_steps)
        current_x = x_target
        current_y = y_target
        # zwrócenie aktualnej pozycji robota
        return current_x, current_y


"""
Funkcja główna odpowiedzialna za sterowanie robotem na podstawie przesłanego tekstu.

Parametry:
napis (str): Tekst do zapisania przez robota.
fonts_path (str): Ścieżka do folderu zawierającego pliki G-code z literami.

"""
def run(napis, fonts_path):
    pwm = setup_gpio() # Inicjalizacja GPIO i PWM
    FRAME_X_START = 0 # Pozycja początkowa w osi X
    FRAME_Y_START = 0 # Pozycja początkowa w osi Y

    try:
        number_of_frames_in_line = 0 # Bieżąca liczba napisanych liter(i spacji) w linii
        for slowo in napis.split(): # Podział tekstu na słowa
            # jeżeli liczba liter w linii po dopisaniu obecnego słowa > 16 to przechodzimy do następnej linii
            if(number_of_frames_in_line + len(slowo) > FRAMES_IN_LINE): 
                x_steps = int((0 - FRAME_X_START) * STEPS_PER_MM)
                y_steps = int((FRAME_HEIGHT+LEADING) * STEPS_PER_MM)
                move_motors(x_steps, y_steps)
                FRAME_X_START = 0
                FRAME_Y_START = FRAME_Y_START + FRAME_HEIGHT + LEADING
                number_of_frames_in_line = 0
            
            for litera in slowo: # Iteracja po literach w słowie
                # Ścieżka do pliku G-code dla danej litery
                file_path = os.path.join(fonts_path, f"{litera}.gcode")
                if os.path.exists(file_path):  # Sprawdzenie, czy plik istnieje
                    FRAME_X_START, FRAME_Y_START = process_gcode(file_path, FRAME_X_START, FRAME_Y_START, pwm)
                else:
                    print(f"Plik {file_path} nie istnieje!")
            # Dodanie liczby liter w słowie do liczby liter w linii
            number_of_frames_in_line += len(slowo)
            # jeżeli znajdujemy się na końcu linii to nie dopisujemy spacji
            if number_of_frames_in_line >= FRAMES_IN_LINE:
                continue      
            # Obsługa spacji jako przesunięcia w prawo
            x_target = FRAME_X_START + FRAME_WIDTH
            y_target = FRAME_Y_START 
            x_steps = int((x_target - FRAME_X_START) * STEPS_PER_MM)
            y_steps = int((y_target - FRAME_Y_START) * STEPS_PER_MM)
            move_motors(x_steps, y_steps)
            FRAME_X_START = x_target
            FRAME_Y_START = y_target
            # Dodanie spacji do liczby liter w linii
            number_of_frames_in_line += 1

        # Powrót do punktu początkowego po zakończeniu pracy
        x_steps = int((0 - FRAME_X_START) * STEPS_PER_MM)
        y_steps = int((0 - FRAME_Y_START) * STEPS_PER_MM)
        move_motors(x_steps, y_steps)
    finally:
        cleanup_gpio(pwm)


# Wywołanie funkcji run w innym programie:
if __name__ == "__main__":
    napis = "ASPSA"
    fonts_path = "./fonts/test"
    run(napis, fonts_path)