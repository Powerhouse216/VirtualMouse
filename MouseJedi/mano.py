import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math 

# Impostazioni di calibrazione e filtri
offsetFiltro = 100
isDragging = False
scrollingAttivo = False
cliccato = False
xVecchia, yVecchia = 0, 0
frenoMovimento = 0.8

# Evita il blocco di sicurezza se il cursore tocca i bordi dello schermo
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Ottiene le dimensioni reali dello schermo
larghezzaSchermo, altezzaSchermo = pyautogui.size()

# Inizializzazione dei moduli di MediaPipe per il tracciamento della mano
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils

# Configurazione del modello (ottimizzato per 1 sola mano nel flusso video)
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Avvia l'acquisizione della webcam predefinita
cap = cv2.VideoCapture(0)

print("Premi 'q' per uscire dal programma.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Impossibile ricevere il frame dalla webcam. In uscita...")
        break

    # Specchia l'immagine orizzontalmente per un effetto specchio naturale
    frame = cv2.flip(frame, 1)
    altezzaFrame, larghezzaFrame, canaliFrame = frame.shape

    # Conversione colore da BGR (OpenCV) a RGB (MediaPipe)
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgbFrame)

    # BLOCCO 1: Disegno dello scheletro della mano sul frame
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDrawing.draw_landmarks(
                frame, 
                handLandmarks, 
                mpHands.HAND_CONNECTIONS,
                mpDrawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4), # Punti verdi
                mpDrawing.DrawingSpec(color=(0, 0, 255), thickness=2)                 # Linee rosse
            )

    # BLOCCO 2: Calcolo delle gesture e interazione con il sistema
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            # Estrazione dei Landmark chiave (Punte delle dita)
            puntaPollice = handLandmarks.landmark[4]
            puntaIndice = handLandmarks.landmark[8]
            puntaMedio = handLandmarks.landmark[12]
            puntaAnnullare = handLandmarks.landmark[16]

            # Conversione delle coordinate normalizzate (0.0 - 1.0) in pixel sul frame
            px, py = int(puntaPollice.x * larghezzaFrame), int(puntaPollice.y * altezzaFrame)
            cx, cy = int(puntaIndice.x * larghezzaFrame), int(puntaIndice.y * altezzaFrame)
            mx, my = int(puntaMedio.x * larghezzaFrame), int(puntaMedio.y * altezzaFrame)
            ax, ay = int(puntaAnnullare.x * larghezzaFrame), int(puntaAnnullare.y * altezzaFrame)

            # Mappatura dello spazio di movimento e stabilizzazione del cursore (Filtro)
            xFinale = float(np.interp(cx, (offsetFiltro, larghezzaFrame - offsetFiltro), (0, larghezzaSchermo)))
            yFinale = float(np.interp(cy, (offsetFiltro, altezzaFrame - offsetFiltro), (0, altezzaSchermo)))
            
            xStabilizzato = (xVecchia * frenoMovimento) + (xFinale * (1 - frenoMovimento))
            yStabilizzato = (yVecchia * frenoMovimento) + (yFinale * (1 - frenoMovimento))
            
            targetX = int(xStabilizzato)
            targetY = int(yStabilizzato)

            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

            # --- GESTURE 1: CLICK SINISTRO (Distanza Pollice - Medio) ---
            distanzaClick = math.hypot(px - mx, py - my)
            if distanzaClick < 30:
                if not cliccato:
                    pyautogui.click()
                    cliccato = True  
                    cv2.putText(frame, "Click", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cliccato = False

            # --- GESTURE 2: SCROLLING (Differenza Asse Y tra Medio e Indice) ---
            differenzaY = my - cy
            if differenzaY > 40: 
                scrollingAttivo = True 
                pyautogui.scroll(-10) # Ruota la rotellina in giù
                cv2.putText(frame, "Down", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif differenzaY < -40:  
                pyautogui.scroll(10)  # Ruota la rotellina in su
                scrollingAttivo = True 
                cv2.putText(frame, "Up", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                scrollingAttivo = False

            # --- GESTURE 3: TRASCINAMENTO FINESTRE O MOVIMENTO (Esclusione logica) ---
            distanzaDrag = math.hypot(ax - px, ay - py) # Distanza Annullare - Pollice
            
            if distanzaDrag < 35: 
                if not isDragging:
                    pyautogui.mouseDown(button='left') # Aggancia l'elemento/finestra
                    isDragging = True
                cv2.putText(frame, "DRAG", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                pyautogui.moveTo(targetX, targetY)
            else:
                if isDragging:
                    pyautogui.mouseUp(button='left') # Rilascia l'elemento/finestra
                    isDragging = False
                
                # Muove il puntatore solo se non sono in corso scroll o click statici
                if not scrollingAttivo and not cliccato:
                    pyautogui.moveTo(targetX, targetY)

            # Aggiornamento storico posizioni per il frame successivo
            xVecchia, yVecchia = xStabilizzato, yStabilizzato

    # Rendering grafico della finestra video (Fuori dai loop di scansione)
    cv2.imshow("finestra pazza", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Chiusura pulita delle risorse e reset periferiche hardware
if isDragging:
    pyautogui.mouseUp(button='left')

cap.release()
cv2.destroyAllWindows()