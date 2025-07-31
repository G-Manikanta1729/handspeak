import cv2
import mediapipe as mp
import pyautogui
import time
import webbrowser

# ----------------------- AUTO OPEN GAME IN BROWSER -----------------------
webbrowser.open("https://poki.com/en/g/subway-surfers")

# ----------------------- CAMERA & MEDIAPIPE SETUP -----------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)
mp_draw = mp.solutions.drawing_utils

# ----------------------- GESTURE LOGIC -----------------------
def is_finger_up(tip, mcp):
    return tip.y < mcp.y - 0.06

def is_finger_down(tip, mcp):
    return tip.y > mcp.y + 0.03

def detect_hand_gesture(landmarks):
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]
    ring_mcp = landmarks[13]
    pinky_mcp = landmarks[17]

    # -- LEFT: Index + Middle UP (others down)
    if (is_finger_up(index_tip, index_mcp) and
        is_finger_up(middle_tip, middle_mcp) and
        is_finger_down(ring_tip, ring_mcp) and
        is_finger_down(pinky_tip, pinky_mcp)):
        return "left"

    # -- RIGHT: Index + Pinky UP (others down)
    if (is_finger_up(index_tip, index_mcp) and
        is_finger_up(pinky_tip, pinky_mcp) and
        is_finger_down(middle_tip, middle_mcp) and
        is_finger_down(ring_tip, ring_mcp)):
        return "right"

    # -- JUMP: Only Index UP (all others down)
    if (is_finger_up(index_tip, index_mcp) and
        is_finger_down(middle_tip, middle_mcp) and
        is_finger_down(ring_tip, ring_mcp) and
        is_finger_down(pinky_tip, pinky_mcp)):
        return "jump"

    # -- SLIDE: All fingers down
    if (is_finger_down(index_tip, index_mcp) and
        is_finger_down(middle_tip, middle_mcp) and
        is_finger_down(ring_tip, ring_mcp) and
        is_finger_down(pinky_tip, pinky_mcp)):
        return "slide"

    return ""

# ----------------------- UI & CONTROL -----------------------
gesture_display = {
    "jump": ("JUMP", (0, 255, 0)),
    "slide": ("SLIDE", (255, 100, 0)),
    "left": ("LEFT", (0, 255, 255)),
    "right": ("RIGHT", (0, 0, 255))
}

prev_gesture = ""
last_time = time.time()
cooldown = 0.8  # seconds

def execute_gesture(gesture):
    if gesture == "jump":
        pyautogui.press("up")
    elif gesture == "slide":
        pyautogui.press("down")
    elif gesture == "left":
        pyautogui.press("left")
    elif gesture == "right":
        pyautogui.press("right")

# ----------------------- MAIN LOOP -----------------------
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    result = hands.process(rgb)
    gesture = ""
    color = (150, 150, 150)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            gesture = detect_hand_gesture(hand.landmark)
            if gesture in gesture_display:
                _, color = gesture_display[gesture]

    current_time = time.time()
    if gesture and gesture != prev_gesture and (current_time - last_time) > cooldown:
        execute_gesture(gesture)
        prev_gesture = gesture
        last_time = current_time
    elif not gesture:
        prev_gesture = ""

    # Display overlay
    status_text = f"Detected: {gesture_display[gesture][0]}" if gesture else "Awaiting Gesture..."
    cv2.rectangle(frame, (0, h - 40), (w, h), color, -1)
    cv2.putText(frame, status_text, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(frame, (0, 0), (w, h), color, 8)
    cv2.putText(frame, "Gestures: Jump | Slide | Left | Right", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Subway Surfers Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ----------------------- CLEANUP -----------------------
cap.release()
cv2.destroyAllWindows()
