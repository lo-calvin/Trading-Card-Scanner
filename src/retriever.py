# Setup
import torch.nn as nn
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import re


class Retriever:
    def __init__(self, embeddings_path) -> None:
        model = models.resnet18(pretrained=False)
        model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove the classification head
        model.eval()
        model.load_state_dict(torch.load("res/detection_weights/resnet18_embeddings.pth", map_location=torch.device('cpu')))
        self.model = model

        # define preprocessing transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.dataset = torch.load(embeddings_path)


    def get_card_id(self, image):
        # TODO if opencv2 image, convert to PIL
        input_tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            target_vector = self.model(input_tensor).flatten().unsqueeze(0)

        sim_dict = self.get_matches(target_vector, 5)
        return sim_dict
  

    def get_matches(self, target_vector, n=5):
        # initiate computation of cosine similarity
        cosine = nn.CosineSimilarity(dim=1)

        # iteratively store similarity of stored images to target image
        sim_dict = {}
        for k, v in self.dataset.items():
            sim = cosine(v.unsqueeze(0), target_vector)[0].item()
            sim_dict[k] = sim

        # sort based on decreasing similarity
        items = sim_dict.items()
        sim_dict = {k: v for k, v in sorted(items, key=lambda i: i[1], reverse=True)}

        # cut to defined top n similar images
        if n is not None:
            top_n_keys = [k for k, v in list(sim_dict.items())[:int(n)]]

            # Apply transformation (regular expression) to each key in the list
            transformed_keys = []
            for key in top_n_keys:
                match = re.search(r'\\([^\\]+)\.png', key)
                if match:
                    transformed_keys.append(match.group(1))  # Extracted part of the key
                else:
                    transformed_keys.append(key)  # If no match, keep the original key

            return transformed_keys

        return []  # If no matches found or `n` is None


