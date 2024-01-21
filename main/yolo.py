# 터미널 실행
# yolo predict model=best.pt source=0(웹캠) show=True box=True

from ultralytics import YOLO

# Load a pretrained YOLOv8n model
class yolo:
    def __init__(self,):
        self.model = YOLO('best.pt')

    def inference(self, source):
        # Run inference on the source
        results = self.model.predict(source, save=False, imgsz=416, save_txt=False, conf=0.5 )

        return results[0]

        

#for i in results.box:
#    print(i[0])
#print(results)