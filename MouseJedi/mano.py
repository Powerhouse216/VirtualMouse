import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math 


#Variable

offsetFiltro = 100
isDragging = False
scrollingAttivo = False
cliccato = False
xVecchia, yVecchia = 0, 0
frenoMovimento = 0.8
jaring = 30
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

larghezzaSchermo, altezzaSchermo = pyautogui.size()

mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils


#hands settings
hands = mpHands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
#defines the webcam
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
    else:
        if isDragging:
            isDragging = False
            pyautogui.mouseUp(button="left")
        cv2.imshow("finestra pazza",frame)
        if cv2.waitKey(1) & 0xFF=='q':
            break
        continue
#main check for the hand and the corellation with the signs
    if results.multi_hand_landmarks and results.multi_handedness:
        for handLandmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            tipo_mano = handedness.classification[0].label

            puntaPollice = handLandmarks.landmark[4]
            puntaIndice = handLandmarks.landmark[8]
            puntaMedio = handLandmarks.landmark[12]
            puntaAnnullare = handLandmarks.landmark[16]
            puntaMignolo = handLandmarks.landmark[20]

            px, py = int(puntaPollice.x * larghezzaFrame), int(puntaPollice.y * altezzaFrame)
            cx, cy = int(puntaIndice.x * larghezzaFrame), int(puntaIndice.y * altezzaFrame)
            mx, my = int(puntaMedio.x * larghezzaFrame), int(puntaMedio.y * altezzaFrame)
            ax, ay = int(puntaAnnullare.x * larghezzaFrame), int(puntaAnnullare.y * altezzaFrame)
            mix, miy = int(puntaMignolo.x * larghezzaFrame), int(puntaMignolo.y * altezzaFrame)
            xFinale = float(np.interp(cx, (offsetFiltro, larghezzaFrame - offsetFiltro), (0, larghezzaSchermo)))
            yFinale = float(np.interp(cy, (offsetFiltro, altezzaFrame - offsetFiltro), (0, altezzaSchermo)))
            
            xStabilizzato = (xVecchia * frenoMovimento) + (xFinale * (1 - frenoMovimento))
            yStabilizzato = (yVecchia * frenoMovimento) + (yFinale * (1 - frenoMovimento))
            
            curX, curY = pyautogui.position()
            targetX, targetY = int(xStabilizzato), int(yStabilizzato)
            delt = math.hypot(curX - targetX, curY - targetY)

            # 1. Gestione  Drag & Click 
            distanzaDrag = math.hypot(mix - px, miy - py) 
            distanzaClick = math.hypot(px - mx, py - my) 

            if distanzaDrag < 35:
                if not isDragging:
                    pyautogui.mouseDown(button='left')
                    isDragging = True
                stato_corrente = "DRAG"
            else:
                if isDragging:
                    pyautogui.mouseUp(button='left')
                    isDragging = False
                
                # Gestione Click
                if distanzaClick < 30:
                    if not cliccato:
                        pyautogui.click()
                        cliccato = True
                    stato_corrente = "Click"
                else:
                    cliccato = False

            # 2. Gestione Scroll
            differenzaY = ay - cy
            if abs(differenzaY) > 40: 
                scrollingAttivo = True
                pyautogui.scroll(10 if differenzaY < -40 else -10)
                stato_corrente = "Scroll"
            else:
                scrollingAttivo = False

        
            # Movimento
            if not scrollingAttivo and delt > jaring:
                pyautogui.moveTo(targetX, targetY)

            # Aggiornamento stato per il frame successivo
            xVecchia, yVecchia = xStabilizzato, yStabilizzato
            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
            
            polso = handLandmarks.landmark[0]
            x_polso, y_polso, z_polso = polso.x, polso.y, polso.z
            
            base_medio = handLandmarks.landmark[9]
            lunghezza_palmo = math.sqrt((base_medio.x - x_polso)**2 + (base_medio.y - y_polso)**2)



            cv2.putText(frame, stato_corrente, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("finestra pazza", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if isDragging:
    pyautogui.mouseUp(button='left')

#releasing all
cap.release()
cv2.destroyAllWindows()