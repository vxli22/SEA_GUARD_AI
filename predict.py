import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Run SEA GUARD AI detection")
    parser.add_argument("--weights", default="models/best.pt")
    parser.add_argument("--source", required=True, help="Image, video, or camera source")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    model = YOLO(args.weights)
    results = model.predict(source=args.source, conf=args.conf, save=True)
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            print(f"{model.names[cls_id]}: {float(box.conf[0]):.2f}")

if __name__ == "__main__":
    main()
