const newFontBtn = document.getElementById("newFontBtn");
const plotterModeBtn = document.getElementById("plotterModeBtn");
const startFontCreation = document.getElementById("startFontCreation");
const backToMain = document.getElementById("backToMain");

const mainScreen = document.getElementById("mainScreen");
const newFontScreen = document.getElementById("newFontScreen");
const canvasScreen = document.getElementById("canvasScreen");
const completionScreen = document.getElementById("completionScreen");
const plotterPanel = document.getElementById("plotterPanel");

const fontNameInput = document.getElementById("fontName");
const letterPrompt = document.getElementById("letterPrompt");
const clear = document.getElementById("clear");
const save = document.getElementById("save");

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = 250;
canvas.height = 500;

let isPainting = false;
let currentFontName = "";
let currentLetterIndex = 0;
const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

// Funkcje rysowania na canvasie
const startDrawing = (e) => {
    const rect = canvas.getBoundingClientRect();
    if (e.button === 0) { // Sprawdź, czy to lewy przycisk myszy
        isPainting = true;
        ctx.lineWidth = 5;
        ctx.lineCap = "round";
        ctx.strokeStyle = "#cad3f4";
        ctx.beginPath(); // Zaczynamy nową ścieżkę
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top); // Ustaw początkowy punkt
    }
};

// Funkcja rysująca linię
const draw = (e) => {
    if (!isPainting) return;
    const rect = canvas.getBoundingClientRect();
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top); // Rysuj linię do nowego punktu
    ctx.stroke();
};

// Funkcja kończąca rysowanie
const stopDrawing = () => {
    if (isPainting) {
        isPainting = false;
        ctx.closePath(); // Zakończ ścieżkę
    }
};

// Funkcja czyszcząca płótno
clear.addEventListener("click", () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Wyczyszczenie całego płótna
    ctx.beginPath(); // Resetowanie ścieżki rysowania
});


// Zapisanie litery
save.addEventListener("click", () => {
    const image = canvas.toDataURL("image/png");
    const letter = alphabet[currentLetterIndex];

    fetch("/save-letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fontName: currentFontName, letter, image }),
    }).then((response) => {
        if (response.ok) {
            currentLetterIndex++;
            if (currentLetterIndex < alphabet.length) {
                letterPrompt.innerText = `Narysuj literę ${alphabet[currentLetterIndex]}`;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            } else {
                showCompletionScreen();
            }
        } else {
            alert("Błąd przy zapisywaniu litery.");
        }
    });
});

// Obsługa klawiszy
document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && currentMode === "fontCreation") {
        save.click();
    }
});

//fontNameInput.addEventListener("keydown", (e) => {
    //if (e.key === "Enter") {
        //startFontCreation.click();
    //}
//});

// Przełączanie ekranów
const showScreen = (screen) => {
    [mainScreen, newFontScreen, canvasScreen, completionScreen, plotterPanel].forEach(
        (div) => (div.style.display = "none")
    );
    screen.style.display = "block";
    if(screen === canvasScreen){
        currentMode = "fontCreation";
    }
    else if(screen === plotterPanel){
        currentMode = "plotter";
    }
    else{
        currentMode = "";
    }
};

const showCompletionScreen = () => {
    showScreen(completionScreen);
};

// Obsługa przycisków nawigacyjnych
newFontBtn.addEventListener("click", () => showScreen(newFontScreen));
//plotterModeBtn.addEventListener("click", () => showScreen(plotterPanel));
startFontCreation.addEventListener("click", () => {
    currentFontName = fontNameInput.value.trim();
    if (currentFontName) {
        currentLetterIndex = 0;
        letterPrompt.innerText = `Narysuj literę ${alphabet[currentLetterIndex]}`;
        showScreen(canvasScreen);
    } else {
        alert("Podaj nazwę czcionki!");
    }
});


backToMain.addEventListener("click", () => showScreen(mainScreen));

// Obsługa rysowania
canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDrawing);
canvas.addEventListener("mouseleave", stopDrawing);


const plotterText = document.getElementById("plotterText");
const sendToPlotter = document.getElementById("sendToPlotter");

// Obsługa przycisku wysyłającego tekst do serwera
sendToPlotter.addEventListener("click", () => {
    const text = plotterText.value.trim();
    const fontName = fontSelector.value;

    if (!fontName){
        alert("wybierz czcionke");
        return;
}
    if (/^[A-Z\s]+$/.test(text)) { // Sprawdzanie tylko liter i spacji
        fetch("/plotter", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, fontName })
        }).then(response => {
            if (response.ok) {
                console.log("Tekst wysłany do plottera:", text);
                plotterText.value = ""; // Wyczyść pole tekstowe
                fontSelector.value = "";
            }
        });
    } else {
        alert("Wpisz tylko duze litery i spacje.");
    }
});
const fontSelector = document.getElementById("fontSelector");

plotterModeBtn.addEventListener("click", () => {
    fetch("/list-fonts", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        })
    .then(response => response.json())
    .then(fonts => {
        console.log("Otrzymane czcionki:", fonts); // Debug
        fontSelector.innerHTML = '<option value="" disabled selected>Wybierz czcionkę</option>';
        fonts.forEach(font => {
            console.log("Dodawanie opcji:", font); // Debug
            const option = document.createElement("option");
            option.value = font;
            option.textContent = font;
            fontSelector.appendChild(option);
        });
    })
    .catch(err => console.error("Błąd przy pobieraniu czcionek:", err));

    showScreen(plotterPanel);
});