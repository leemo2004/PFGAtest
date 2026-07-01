import cv2
import numpy as np
import time
cap = cv2.VideoCapture('coin.mp4')


while True:
    ret, frame = cap.read()
    start_time = time.time()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.resize(frame, (0,0), fx=0.4, fy=0.4 )
    gray = cv2.resize(gray, (0,0), fx=0.4, fy=0.4 ) 
    gray = cv2.GaussianBlur(gray, (17,17), 2)
    circles = cv2.HoughCircles(
        gray, 
        cv2.HOUGH_GRADIENT, 
        dp=1,          
        minDist=50,    
        param1=70,    
        param2=27,     
        minRadius=7,  
        maxRadius=30
    )
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2] 
            # 畫出硬幣的外圈（綠色線條，粗度 2）
            cv2.rectangle(frame, (i[0]-i[2], i[1]-i[2]), (i[0]+i[2], i[1]+i[2]), (0, 0, 255), 2)
            # 畫出硬幣的圓心（紅色實心點，半徑 3）
            cv2.circle(frame, (i[0], i[1]), 3, (0, 255, 0), -1)  
            coordinate_text = f"({x}, {y})"
            text_position = (x - r, y - r - 5)
            cv2.putText(
                frame, 
                coordinate_text, 
                text_position,             # 自動計算出的文字放置位置
                cv2.FONT_HERSHEY_SIMPLEX,  # 字體
                0.4,                       # 字體大小（配合縮小後的畫面，0.4 剛剛好）
                (255, 255, 255),           # 文字顏色（白色）
                1                          # 線條粗細
            )
    end_time = time.time()
    processing_time = end_time - start_time
    if ret: 
        time_text = f"Time: {processing_time * 1000:.2f} ms"

    # 如果時間小於等於 100 毫秒 (0.1秒)，顯示綠色（安全）；超過則顯示紅色（超標）
        text_color = (0, 255, 0) if processing_time <= 0.1 else (0, 0, 255)
    
        cv2.putText(
            frame, 
            time_text, 
            (10, 30),                  # 文字左下角的座標 (X, Y)
            cv2.FONT_HERSHEY_SIMPLEX,  # 字體
            0.7,                       # 字體大小倍率
            text_color,                # 顏色
            2                        
        )

        cv2.imshow('frame', frame)
        cv2.imshow("Gray", gray)
    else:
      break
    if cv2.waitKey(16) == ord('q'):
      break