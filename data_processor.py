import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class GIKIDataProcessor:
    def __init__(self):
        self.data_dir = Path("dataset")
        self.data_dir.mkdir(exist_ok=True)
        self.setup_logging()
        self.setup_nltk()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.data_dir / 'data_processor.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DataProcessor')
    
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            self.logger.error(f"Error setting up NLTK: {str(e)}")
    
    def collect_web_data(self):
        """Collect data from various web sources"""
        sources = {
            'giki_main': 'https://giki.edu.pk/',
            'wikipedia': 'https://en.wikipedia.org/wiki/Ghulam_Ishaq_Khan_Institute_of_Engineering_Sciences_and_Technology',
            'news': 'https://giki.edu.pk/news/',
            'research': 'https://giki.edu.pk/research/',
            'admissions': 'https://giki.edu.pk/admissions/'
        }
        
        collected_data = []
        
        for source_name, url in sources.items():
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract paragraphs
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Filter out short snippets
                        collected_data.append({
                            'text': text,
                            'source': source_name,
                            'url': url,
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Extract headers
                headers = soup.find_all(['h1', 'h2', 'h3'])
                for h in headers:
                    text = h.get_text().strip()
                    if len(text) > 20:  # Filter out short headers
                        collected_data.append({
                            'text': text,
                            'source': source_name,
                            'url': url,
                            'timestamp': datetime.now().isoformat()
                        })
            
            except Exception as e:
                self.logger.error(f"Error collecting data from {source_name}: {str(e)}")
        
        return collected_data
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text data"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def generate_training_pairs(self, texts: List[Dict]) -> List[Dict]:
        """Generate question-answer pairs from texts"""
        training_pairs = []
        
        # Question patterns
        patterns = [
            ("what", "Describe"),
            ("how", "Explain how"),
            ("when", "When"),
            ("where", "Where"),
            ("why", "Why"),
            ("who", "Who"),
            ("which", "Which")
        ]
        
        for text_dict in texts:
            text = text_dict['text']
            sentences = nltk.sent_tokenize(text)
            
            for sentence in sentences:
                # Generate different types of questions
                for q_word, pattern in patterns:
                    if len(sentence.split()) > 5:  # Only use meaningful sentences
                        training_pairs.append({
                            'question': f"{pattern} {sentence.strip('.')}?",
                            'answer': sentence,
                            'source': text_dict['source'],
                            'url': text_dict['url']
                        })
        
        return training_pairs
    
    def create_dataset(self):
        """Create and save the training dataset"""
        try:
            # Collect web data
            self.logger.info("Collecting web data...")
            web_data = self.collect_web_data()
            
            # Generate training pairs
            self.logger.info("Generating training pairs...")
            training_pairs = self.generate_training_pairs(web_data)
            
            # Create DataFrame
            df = pd.DataFrame(training_pairs)
            
            # Preprocess text
            self.logger.info("Preprocessing text...")
            df['processed_question'] = df['question'].apply(self.preprocess_text)
            df['processed_answer'] = df['answer'].apply(self.preprocess_text)
            
            # Split into train and test sets
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
            
            # Save datasets
            train_df.to_csv(self.data_dir / 'train_dataset.csv', index=False)
            test_df.to_csv(self.data_dir / 'test_dataset.csv', index=False)
            
            # Save raw data
            with open(self.data_dir / 'raw_data.json', 'w') as f:
                json.dump(web_data, f, indent=2)
            
            self.logger.info(f"Dataset created successfully. Training size: {len(train_df)}, Test size: {len(test_df)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating dataset: {str(e)}")
            return False
    
    def load_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load the training and test datasets"""
        try:
            train_df = pd.read_csv(self.data_dir / 'train_dataset.csv')
            test_df = pd.read_csv(self.data_dir / 'test_dataset.csv')
            return train_df, test_df
        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
            return None, None

if __name__ == "__main__":
    processor = GIKIDataProcessor()
    processor.create_dataset() 