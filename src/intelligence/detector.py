import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class MobileNetDetector:
    """Lightweight detector for Gurneev's Smart Glasses (V1 Vision)."""

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]

    def __init__(self, prototxt="models/deploy.prototxt", model="models/mobilenet_iter_73000.caffemodel"):
        if not os.path.exists(prototxt) or not os.path.exists(model):
            logger.error("Vision models not found. Please download them first.")
            self.net = None
            return
        
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        logger.info("MobileNet-SSD loaded.")

    def detect(self, frame: np.ndarray, min_confidence: float = 0.4):
        """Run detection and return a list of hazards."""
        if self.net is None:
            return []

        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        
        self.net.setInput(blob)
        detections = self.net.forward()
        
        hazards = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > min_confidence:
                idx = int(detections[0, 0, i, 1])
                obj_class = self.CLASSES[idx]
                
                # Bounding box
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Estimate distance based on box height (relative to frame height)
                # This is a very rough simulation for V1.
                obj_height = endY - startY
                distance = round(max(3.0 - (obj_height / h) * 3, 0.5), 1)
                
                hazards.append({
                    'class': obj_class,
                    'confidence': float(confidence),
                    'distance': distance,
                    'box': (startX, startY, endX, endY)
                })

        return hazards
