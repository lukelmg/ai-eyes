import os
import time
import base64
import cv2
import requests


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL = os.getenv("MODEL", "qwen2.5vl:3b")  # set to a pulled vision model (e.g., llama3.2-vision, qwen2.5-vl, llava)
CAM_INDEX = int(os.getenv("CAM_INDEX", "0"))


def encode_frame_to_base64_jpeg(frame):
    success, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    if not success:
        return None
    return base64.b64encode(buf.tobytes()).decode()


def generate_with_image(model, prompt, image_b64, context):
    # Prefer chat API for vision models
    chat_url = f"{OLLAMA_HOST}/api/chat"
    chat_payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "stream": False,
    }
    if context:
        chat_payload["context"] = context

    r = requests.post(chat_url, json=chat_payload, timeout=120)
    if r.status_code == 404:
        # Fallback to legacy generate API
        gen_url = f"{OLLAMA_HOST}/api/generate"
        gen_payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }
        if context:
            gen_payload["context"] = context
        r = requests.post(gen_url, json=gen_payload, timeout=120)

    if not r.ok:
        try:
            print(f"Server said: {r.text}")
        except Exception:
            pass
        r.raise_for_status()

    data = r.json()
    # Chat response shape: { message: { content }, context }
    if "message" in data:
        return data["message"].get("content", ""), data.get("context")
    # Generate response shape: { response, context }
    return data.get("response", ""), data.get("context")


def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAM_INDEX}")

    context = None
    try:
        while True:
            ok, frame = cap.read()

            img_b64 = encode_frame_to_base64_jpeg(frame)

            prompt = (
                "Give directions to click on the firefox icon."
            )

            try:
                text, context = generate_with_image(MODEL, prompt, img_b64, context)
                print(text, flush=True)
            except Exception as e:
                print(f"Ollama error: {e}")
    finally:
        cap.release()


if __name__ == "__main__":
    main()


