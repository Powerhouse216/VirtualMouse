import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math 
import json
import random

#functions

def confronta_pose(punti_json, punti_webcam, tipo_mano="Right", soglia_tolleranza=0.4):
    if not punti_json:
        return False, 999.0
    diz_json = {p["id"]: p for p in punti_json}
    diz_webcam = {p["id"]: p for p in punti_webcam}
    
    errore_totale = 0.0

    for i in range(21):
        pt_j = diz_json[i]
        pt_w = diz_webcam[i]
        x_webcam = pt_w["x"]
        if tipo_mano == "Left":
            x_webcam = -x_webcam

        distanza = math.sqrt((pt_j["x"] - x_webcam)**2 + (pt_j["y"] - pt_w["y"])**2)
        errore_totale += distanza

    errore_medio = errore_totale / 21
    gesto_uguale = errore_medio < soglia_tolleranza
    
    return gesto_uguale, errore_medio

def WorldBearer(durata_frame=20):
    screenshot = pyautogui.screenshot()
    schermo_base = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    nome_finestra = "WorldBearing"
    cv2.namedWindow(nome_finestra, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(nome_finestra, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    (testo_w, testo_h), _ = cv2.getTextSize("Prepare for destruction", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    testo_x = (larghezzaSchermo - testo_w) / 2
    testo_y = (altezzaSchermo + testo_h) / 2
    cv2.putText(schermo_base, "Prepare for destruction", (int(testo_x), int(testo_y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    for f in range(durata_frame):
        overlay = schermo_base.copy()
        num_cubi = random.randint(3, 8) + (f // 2)
        
        for _ in range(num_cubi):
            w = random.randint(40, 150)
            x = random.randint(0, larghezzaSchermo - w)
            y = random.randint(0, altezzaSchermo - w)
            
            colore = (0, 0, random.randint(100, 160)) if random.random() < 0.6 else (10, 20, random.randint(200, 255))
            
            cv2.rectangle(overlay, (x, y), (x + w, y + w), colore, cv2.FILLED)
            cv2.rectangle(overlay, (x, y), (x + w, y + w), (0, 0, 0), 1)

        cv2.addWeighted(overlay, 0.6, schermo_base, 0.4, 0, schermo_base)
        cv2.imshow(nome_finestra, schermo_base)
        
        if cv2.waitKey(30) & 0xFF == ord('s'):
            break
            
    cv2.destroyWindow(nome_finestra)

def Remembrance(durata_frame=20):
    nomeF = "Freeze"
    cv2.namedWindow(nomeF, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(nomeF, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.waitKey(5)
    screen = pyautogui.screenshot()
    sb = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    b_base, g_base, r_base = cv2.split(sb)
    
    for f in range(durata_frame):
        fattore_b = f * 5
        fattore_r = int(f / 5)
        
        b = cv2.add(b_base, fattore_b)
        r = cv2.add(r_base, fattore_r)
        
        freezato = cv2.merge([b, g_base, r])
        cv2.imshow(nomeF, freezato)
        
        if cv2.waitKey(30) & 0xFF == ord('s'):
            break
            
    cv2.destroyWindow(nomeF)

#Variable

offsetFiltro = 100
isDragging = False
scrollingAttivo = False
cliccato = False
xVecchia, yVecchia = 0, 0
frenoMovimento = 0.8
nome_file = "posa_mano_pura.json"
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

larghezzaSchermo, altezzaSchermo = pyautogui.size()

mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils

#Json opening
try:
    with open(nome_file, "r") as file_json:
        punti_json = json.load(file_json)
except FileNotFoundError:
    print(f"Errore: Il file '{nome_file}' non esiste ancora. Devi prima eseguire lo script che lo crea!")
    exit()

#hands settings
hands = mpHands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
#0 defines the webcam
cap = cv2.VideoCapture(0)
print("Premi 'q' per uscire dal programma.")

#getting the frame and tracking the hand

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Impossibile ricevere il frame dalla webcam. In uscita...")
        break

    frame = cv2.flip(frame, 1)
    altezzaFrame, larghezzaFrame, canaliFrame = frame.shape

    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgbFrame)

    stato_corrente = "Idle"

    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDrawing.draw_landmarks(
                frame, 
                handLandmarks, 
                mpHands.HAND_CONNECTIONS,
                mpDrawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4), 
                mpDrawing.DrawingSpec(color=(0, 0, 255), thickness=2)                 
            )
#main check for the hand and the corellation with the signs
    if results.multi_hand_landmarks and results.multi_handedness:
        for handLandmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            tipo_mano = handedness.classification[0].label

            puntaPollice = handLandmarks.landmark[4]
            puntaIndice = handLandmarks.landmark[8]
            puntaMedio = handLandmarks.landmark[12]
            puntaAnnullare = handLandmarks.landmark[16]

            px, py = int(puntaPollice.x * larghezzaFrame), int(puntaPollice.y * altezzaFrame)
            cx, cy = int(puntaIndice.x * larghezzaFrame), int(puntaIndice.y * altezzaFrame)
            mx, my = int(puntaMedio.x * larghezzaFrame), int(puntaMedio.y * altezzaFrame)
            ax, ay = int(puntaAnnullare.x * larghezzaFrame), int(puntaAnnullare.y * altezzaFrame)

            xFinale = float(np.interp(cx, (offsetFiltro, larghezzaFrame - offsetFiltro), (0, larghezzaSchermo)))
            yFinale = float(np.interp(cy, (offsetFiltro, altezzaFrame - offsetFiltro), (0, altezzaSchermo)))
            
            xStabilizzato = (xVecchia * frenoMovimento) + (xFinale * (1 - frenoMovimento))
            yStabilizzato = (yVecchia * frenoMovimento) + (yFinale * (1 - frenoMovimento))
            
            targetX = int(xStabilizzato)
            targetY = int(yStabilizzato)

            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
            
            polso = handLandmarks.landmark[0]
            x_polso, y_polso, z_polso = polso.x, polso.y, polso.z
            
            base_medio = handLandmarks.landmark[9]
            lunghezza_palmo = math.sqrt((base_medio.x - x_polso)**2 + (base_medio.y - y_polso)**2)
            
            datiMano = []
            for id_punto, landmark in enumerate(handLandmarks.landmark):
                puntoPerLista = {
                    "id" : id_punto,
                    "x" : (landmark.x - x_polso) / lunghezza_palmo,
                    "y" : (landmark.y - y_polso) / lunghezza_palmo,
                    "z" : (landmark.z - z_polso) / lunghezza_palmo,
                }
                datiMano.append(puntoPerLista)
            
            gs, erroreMedio = confronta_pose(punti_json, datiMano, tipo_mano=tipo_mano, soglia_tolleranza=0.4)
            if gs:
                if tipo_mano == "Right":
                    WorldBearer(durata_frame=20)
                elif tipo_mano == "Left":
                    Remembrance(durata_frame=20)

            distanzaClick = math.hypot(px - mx, py - my)
            if distanzaClick < 30:
                if not cliccato:
                    pyautogui.click()
                    cliccato = True  
                stato_corrente = "Click"
            else:
                cliccato = False

            differenzaY = my - cy
            if differenzaY > 40: 
                scrollingAttivo = True 
                pyautogui.scroll(-10) 
                stato_corrente = "Scroll Down"
            elif differenzaY < -40:  
                pyautogui.scroll(10)  
                scrollingAttivo = True 
                stato_corrente = "Scroll Up"
            else:
                scrollingAttivo = False

            distanzaDrag = math.hypot(ax - px, ay - py) 
            
            if distanzaDrag < 35: 
                if not isDragging:
                    pyautogui.mouseDown(button='left') 
                    isDragging = True
                stato_corrente = "DRAG"
                pyautogui.moveTo(targetX, targetY)
            else:
                if isDragging:
                    pyautogui.mouseUp(button='left') 
                    isDragging = False
                
                if not scrollingAttivo and not cliccato:
                    pyautogui.moveTo(targetX, targetY)

            xVecchia, yVecchia = xStabilizzato, yStabilizzato

            cv2.putText(frame, stato_corrente, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("finestra pazza", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if isDragging:
    pyautogui.mouseUp(button='left')

#releasing all
cap.release()
cv2.destroyAllWindows()