import cv2
import asyncio
from detector import Detector
from retriever import Retriever
from PIL import Image
import numpy as np
from pokemontcgsdk import Card
from pokemontcgsdk import RestClient
import cv2
import numpy as np
from PIL import Image

RestClient.configure('c0a13e31-4371-413c-8f1f-264697acc48e')  # my API key

class Model:
    def __init__(self):
        self.det = Detector("res\\detection_weights\\yolo11n_seg_best_10epochs.onnx")
        self.ret = Retriever("res\\classification_embeddings\\Resnet18_embeddings.pt")

    def get_bbox_corner(self, bbox, img):
        x, y, w, h = bbox
        x_min = int(x - w / 2)
        y_min = int(y - h / 2)
        x_max = int(x + w / 2)
        y_max = int(y + h / 2)

        height, width, _ = img.shape
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(width, x_max)
        y_max = min(height, y_max)

        return x_min, y_min, x_max, y_max


    def get_segmented_card(self, mask, bbox, img):
        resized_mask = cv2.resize(
            mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)

        # get masked pixels
        cutout = resized_mask[..., None]*img

        # Get bounding box coordinates (x, y, width, height, conf, label)
        x_min, y_min, x_max, y_max = self.get_bbox_corner(bbox, img)

        # Crop to bounding box
        cropped_cutout = cutout[y_min:y_max, x_min:x_max]

        # Convert to PIL image
        cropped_cutout = Image.fromarray((cropped_cutout * 255).astype(np.uint8))

        return cropped_cutout


    def process_card(self, mask, bbox, track_id):
        x_min, y_min, x_max, y_max = self.get_bbox_corner(bbox, self.img)

        # Convert to PIL image
        cropped_cutout = self.get_segmented_card(mask, bbox, self.img)

        # Get card id
        matches = self.ret.get_card_id(cropped_cutout)
        card_id = matches[0]
        try:
            card = Card.find(card_id)
        except:
            print("Card not found")
            return

        # Store the result
        self.results[track_id] = card

        # Draw bounding box and label on the original image
        
        label = f"ID: {track_id} - {card.name}"
        if self.img.shape[1] > 1500:
            cv2.putText(self.img, label, (x_min, int(bbox[1]) + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 10)
            cv2.putText(self.img, label, (x_min, int(bbox[1]) + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.rectangle(self.img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 8)
        else:
            cv2.rectangle(self.img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)
            cv2.putText(self.img, label, (x_min, int(bbox[1]) + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 8)
            cv2.putText(self.img, label, (x_min, int(bbox[1]) + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)



    def process_all_cards(self):
        self.results = {}

        # Loop over masks and create asynchronous tasks for each card
        for i in range(len(self.masks)):
            self.process_card(self.masks[i], self.bboxs[i], self.track_ids[i])


    # Main function to run the model, track and process the image
    def process_image(self, file):
        img = cv2.imread(file)
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.det.model.track(file)
        try:
            result = results[0]
            self.masks = (result.masks.data.numpy() * 255).astype("uint8")
            self.bboxs = result.boxes.xywh.data.numpy()
            self.track_ids = results[0].boxes.id.int().cpu().tolist()
        except:
            print("No cards detected")
            self.results = {}
            return
        
        self.process_all_cards()

# sample usage:


# from model import Model

# # Run the main function
# model = Model()

# model.process_image("res\\test2.jpg")

# # contains a dict of tracked number and the card objects
# model.results

# # contains the marked up img
# plt.imshow(model.img)
# plt.show()

