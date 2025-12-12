import os
from pathlib import Path


GENERATED_ROOT = Path("generated_projects")
GENERATED_ROOT.mkdir(exist_ok=True)


def slugify(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in name.lower()).strip("-")
    return safe or "project"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def create_opencv_face_tracker(project_name: str, description: str | None = None):
    slug = slugify(project_name)
    base = GENERATED_ROOT / slug
    readme = f"""# {project_name}

{description or "OpenCV face detection and tracking from webcam."}

## Setup
```
pip install -r requirements.txt
python main.py
```
"""
    requirements = "opencv-python\n"

    main_py = """import cv2

def main():
    # Load Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("✅ Webcam opened. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Face Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
"""
    write_file(base / "README.md", readme)
    write_file(base / "requirements.txt", requirements)
    write_file(base / "main.py", main_py)
    return f"📦 Project created at {base}"


def scaffold_project(name: str, description: str | None = None, template: str | None = None):
    template = template or "opencv_face_tracker"
    if template == "opencv_face_tracker":
        return create_opencv_face_tracker(name, description)
    return "❌ Unknown template."
