import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import logging
from datetime import datetime

class GIKIModelTrainer:
    def __init__(self):
        self.data_dir = Path("data")
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        self.setup_logging()
        self.load_model()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.data_dir / 'model.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GIKIModel')
    
    def load_model(self):
        """Load or download the sentence transformer model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise
    
    def prepare_training_data(self) -> List[Dict]:
        """Prepare training data from the dataset"""
        try:
            # Load dataset
            with open(self.data_dir / 'giki_dataset.json', 'r') as f:
                dataset = json.load(f)
            
            training_data = []
            
            # Generate QA pairs for departments
            for dept_code, dept_info in dataset.get('departments', {}).items():
                training_data.extend([
                    {
                        'question': f"What is {dept_code}?",
                        'answer': f"The {dept_info['name']} ({dept_code}) was established in {dept_info['established']}."
                    },
                    {
                        'question': f"What programs are offered in {dept_code}?",
                        'answer': f"The {dept_code} offers: {', '.join(dept_info['programs'])}"
                    },
                    {
                        'question': f"What research is done in {dept_code}?",
                        'answer': f"Research areas in {dept_code} include: {', '.join(dept_info['research_areas'])}"
                    }
                ])
            
            # Generate QA pairs for events
            for event in dataset.get('events', []):
                training_data.append({
                    'question': f"Tell me about {event['title']}",
                    'answer': f"{event['title']} is scheduled for {event['date']} at {event['location']}. {event['description']}"
                })
            
            # Generate QA pairs for faculty
            for dept, faculty in dataset.get('faculty', {}).items():
                for member in faculty:
                    training_data.append({
                        'question': f"Who is {member['name']}?",
                        'answer': f"{member['name']} is a {member['designation']} in {dept}, specializing in {member['specialization']}."
                    })
            
            # Generate QA pairs for publications
            for pub in dataset.get('publications', []):
                training_data.append({
                    'question': f"Tell me about the research on {pub['title']}",
                    'answer': f"Research paper titled '{pub['title']}' was published in {pub['journal']} ({pub['year']}) by {pub['authors']}."
                })
            
            return training_data
        
        except Exception as e:
            self.logger.error(f"Error preparing training data: {str(e)}")
            return []
    
    def encode_qa_pairs(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Encode questions and answers using the model"""
        try:
            questions = [item['question'] for item in training_data]
            answers = [item['answer'] for item in training_data]
            
            # Encode questions and answers
            question_embeddings = self.model.encode(questions, convert_to_tensor=True)
            answer_embeddings = self.model.encode(answers, convert_to_tensor=True)
            
            return question_embeddings, answer_embeddings, answers
        
        except Exception as e:
            self.logger.error(f"Error encoding QA pairs: {str(e)}")
            raise
    
    def save_embeddings(self, question_embeddings: torch.Tensor, answer_embeddings: torch.Tensor, answers: List[str]):
        """Save the encoded embeddings and answers"""
        try:
            # Convert tensors to numpy arrays for saving
            q_emb = question_embeddings.cpu().numpy()
            a_emb = answer_embeddings.cpu().numpy()
            
            # Save embeddings and answers
            np.save(self.model_dir / 'question_embeddings.npy', q_emb)
            np.save(self.model_dir / 'answer_embeddings.npy', a_emb)
            
            with open(self.model_dir / 'answers.json', 'w') as f:
                json.dump(answers, f)
            
            # Save metadata
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'model_name': self.model.get_sentence_embedding_dimension(),
                'num_qa_pairs': len(answers)
            }
            
            with open(self.model_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f)
            
            self.logger.info("Embeddings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving embeddings: {str(e)}")
            raise
    
    def find_best_answer(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Find the best matching answers for a query"""
        try:
            # Load saved embeddings and answers
            q_emb = np.load(self.model_dir / 'question_embeddings.npy')
            with open(self.model_dir / 'answers.json', 'r') as f:
                answers = json.load(f)
            
            # Encode the query
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = cosine_similarity(
                query_embedding.cpu().numpy().reshape(1, -1),
                q_emb
            )[0]
            
            # Get top-k matches
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            return [(answers[i], float(similarities[i])) for i in top_indices]
            
        except Exception as e:
            self.logger.error(f"Error finding answer: {str(e)}")
            return []
    
    def train(self):
        """Train/update the model with latest data"""
        try:
            # Prepare training data
            training_data = self.prepare_training_data()
            if not training_data:
                raise ValueError("No training data available")
            
            # Encode QA pairs
            q_embeddings, a_embeddings, answers = self.encode_qa_pairs(training_data)
            
            # Save embeddings and answers
            self.save_embeddings(q_embeddings, a_embeddings, answers)
            
            self.logger.info("Training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during training: {str(e)}")
            return False

if __name__ == "__main__":
    trainer = GIKIModelTrainer()
    trainer.train() 