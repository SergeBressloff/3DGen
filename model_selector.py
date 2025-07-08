from sentence_transformers import SentenceTransformer, util
import torch

class ModelSelector:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Map model files to descriptions
        self.model_descriptions = {
            "dino.glb": "3D model of a T-Rex dinosaur",
            "space.glb": "A sci-fi style spaceship model",
            "tree.glb": "A realistic 3D model of an oak tree",
            "lion.glb": "A 3D model of a lion",
        }

        self.descriptions = list(self.model_descriptions.values())
        self.embeddings = self.model.encode(self.descriptions, convert_to_tensor=True)

    def get_best_match(self, input_text, threshold=0.5):
        query_embedding = self.model.encode(input_text, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]
        best_score = torch.max(scores).item()
        best_idx = torch.argmax(scores).item()

        if best_score < threshold:
            return None, best_score

        best_key = list(self.model_descriptions.keys())[best_idx]
        return best_key, best_score
