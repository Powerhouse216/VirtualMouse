import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math 
offset = 100
cliccato = False
xVecchia, yVecchia = 0,0
freno = 0.8
#evita il crush se la mano tocca i bordi
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
#da le dimensioni dello schermo
larghezza_schermo, altezza_schermo = pyautogui.size()

# Inizializza i moduli di MediaPipe per il tracciamento delle mani
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configura il modello di tracciamento
# - static_image_mode=False: ottimizzato per il flusso video continuo
# - max_num_hands=1: rileva 1 mano solo
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
)

# Avvia la cattura della webcam (0 è solitamente la webcam predefinita del PC)
cap = cv2.VideoCapture(0)

print("Premi 'q' per uscire dal programma.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Impossibile ricevere il frame dalla webcam. In uscita...")
        break
    #ottiene i valori del frame
    # Specchia l'immagine orizzontalmente per un effetto "specchio" più naturale
    frame = cv2.flip(frame, 1)

    # MediaPipe lavora con lo spazio colore RGB, mentre OpenCV usa BGR.
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Elabora il frame e trova le mani
    results = hands.process(rgb_frame)

    # Se vengono rilevate delle mani, disegna i punti di snodo
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Disegna le connessioni e i punti (landmarks) sulla mano
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4), # Colore punti (Verde)
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)                 # Colore linee (Rosso)
            )
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            h,w,c = frame.shape
            puntaIndice = hand_landmarks.landmark[8]
            puntaPollice = hand_landmarks.landmark[4]
            puntaMedio = hand_landmarks.landmark[12]
            px,py = int(puntaPollice.x*w), int(puntaPollice.y*h)
            cx,cy = int(puntaIndice.x*w), int(puntaIndice.y * h)
            mx,my = int(puntaMedio.x*w), int(puntaMedio.y * h)
            distanza = math.hypot(px-mx,py-my)
            #calcolo movimento
            xfin = float(np.interp(cx, (offset, w-offset), (0, larghezza_schermo)))
            yfin = float(np.interp(cy, (offset,h-offset), (0,altezza_schermo)))
            xStab = (xVecchia * freno) + (xfin * (1 - freno))
            yStab = (yVecchia * freno) + (yfin * (1 - freno))
            # Mostra il frame risultante in una finestra
            pyautogui.moveTo(int(xStab),int(yStab))
            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
            if distanza < 30:  # Soglia in pixel (fai dei test)
                if not cliccato:
                    pyautogui.click()
                    cliccato = True  
            else:
                cliccato = False
            # Sottrai la Y del medio da quella dell'indice per vedere chi sta più in alto
            differenza_y = my - cy

            if differenza_y > 40:  
                pyautogui.scroll(-10) # Scroll Down
            elif differenza_y < -40:  
                    pyautogui.scroll(10)  # Scroll Up
            cv2.imshow("finestra pazza",frame)
            xVecchia, yVecchia = xStab,yStab
    # Interrompi il ciclo se viene premuto q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia la webcam e chiude tutte le finestre di OpenCV
cap.release()
cv2.destroyAllWindows()