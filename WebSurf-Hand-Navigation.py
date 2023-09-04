import cv2
import mediapipe as mp
import time
from pynput.keyboard import Controller, Key

# Web kamerasını başlatın
cap = cv2.VideoCapture(0)

# MediaPipe ile el takibi yapmak için gerekli nesneleri oluşturun
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Pynput klavye denetleyicisini oluşturun
keyboard = Controller()

# Zamanı takip etmek için değişkenler
pTime = 0
cTime = 0

# El pozisyonunu ve klavye durumunu takip etmek için değişkenler
x = 0
y = 0
izin = True
key_pressed = False
prev_region = None
down_pressed = False
up_pressed = False

# Ana döngüyü başlatın
while True:
    # Webcam'den bir çerçeve alın
    success, img = cap.read()

    # Çerçeveyi yatay olarak çevirin (ayna görüntü)
    img = cv2.flip(img, 1)

    # MediaPipe için RGB formatına dönüştürün
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # El izleme sonuçlarını alın
    results = hands.process(imgRGB)

    # Eğer el izleme sonuçları varsa
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                # İlgili işaret noktası belirlendiğinde (örneğin, işaret parmağı)
                if id == 8:
                    cv2.circle(img, (cx, cy), 20, (0, 0, 0), cv2.FILLED)
                    x = cx
                    y = cy

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # FPS hesaplamaları
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # FPS'i çerçevenin üst sol köşesine yazdırın
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 5)

    # El pozisyonuna göre klavye eylemlerini gerçekleştirin
    if x < (1 / 3) * img.shape[1]:  # Sol bölge
        if prev_region != 'left':
            keyboard.press(Key.right)
            if prev_region == 'right':
                keyboard.release(Key.left)
            prev_region = 'left'
            key_pressed = True
        print("Solda")
    elif x > (2 / 3) * img.shape[1]:  # Sağ bölge
        if prev_region != 'right':
            keyboard.press(Key.left)
            if prev_region == 'left':
                keyboard.release(Key.right)
            prev_region = 'right'
            key_pressed = True
        print("Sağda")
    else:
        if key_pressed:
            keyboard.release(Key.right)
            keyboard.release(Key.left)
            key_pressed = False
        if prev_region is None and x != 0 and y != 0:
            if y > (2 / 3) * img.shape[0]:  # Parmak aşağıda
                if not down_pressed:
                    keyboard.press(Key.down)
                    down_pressed = True
                    up_pressed = False
                    print("Parmaklar aşağıda")
            elif y < (1 / 3) * img.shape[0]:  # Parmaklar yukarıda
                if not up_pressed:
                    keyboard.press(Key.up)
                    up_pressed = True
                    down_pressed = False
                    time.sleep(0.2)  # Tuşa basılı tutma süresi
                    keyboard.release(Key.up)
                    print("Parmaklar yukarıda")
            else:
                if down_pressed:
                    keyboard.release(Key.down)
                    down_pressed = False
                if up_pressed:
                    keyboard.release(Key.up)
                    up_pressed = False
        prev_region = None

    # El pozisyonunu sıfırlayın
    x = 0
    y = 0

    # Bölgeleri görselleştirme
    sol_bolge = (int((1 / 3) * img.shape[1]), 0)
    sag_bolge = (int((2 / 3) * img.shape[1]), 0)
    cv2.line(img, sol_bolge, (sol_bolge[0], img.shape[0]), (0, 255, 0), 3)  # Sol bölge çizgisi
    cv2.line(img, sag_bolge, (sag_bolge[0], img.shape[0]), (0, 255, 0), 3)  # Sağ bölge çizgisi

    # Çerçeveyi göster
    cv2.imshow("Sonuç", img)

    # 'q' tuşuna basıldığında döngüyü kırın
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamerayı serbest bırakın ve pencereyi kapatın
cap.release()
cv2.destroyAllWindows()
