from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2
import time

app = FastAPI()

# Global variable to hold the video capture object
cap = None

def get_video_capture():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap

def generate_frames():
    cap = get_video_capture()
    while True:
        success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpeg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(1/60)  # Around 30 FPS

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/video-stream")
async def video_stream_endpoint():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/video-frame")
async def video_frame_endpoint():
    cap = get_video_capture()
    success, frame = cap.read()
    if not success:
        return Response(content="Could not capture frame", status_code=500)
    ret, buffer = cv2.imencode('.jpg', frame)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

@app.on_event("shutdown")
def shutdown_event():
    global cap
    if cap is not None:
        cap.release()
