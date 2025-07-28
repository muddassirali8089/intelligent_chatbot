import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List
import logging
from pathlib import Path

class GIKIDataScraper:
    def __init__(self):
        self.base_url = "https://giki.edu.pk/"
        self.news_url = "https://giki.edu.pk/news/"
        self.events_url = "https://giki.edu.pk/events/"
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.data_dir / 'scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GIKIScraper')
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def scrape_news(self) -> List[Dict]:
        """Scrape latest news from GIKI website"""
        try:
            soup = self.fetch_page(self.news_url)
            if not soup:
                return []
            
            news_items = []
            news_elements = soup.find_all('article', class_='post')
            
            for element in news_elements:
                news_items.append({
                    'title': element.find('h2').text.strip(),
                    'date': element.find('time').get('datetime'),
                    'content': element.find('div', class_='entry-content').text.strip(),
                    'link': element.find('a')['href']
                })
            
            return news_items
        except Exception as e:
            self.logger.error(f"Error scraping news: {str(e)}")
            return []
    
    def scrape_events(self) -> List[Dict]:
        """Scrape upcoming events from GIKI website"""
        try:
            soup = self.fetch_page(self.events_url)
            if not soup:
                return []
            
            events = []
            event_elements = soup.find_all('div', class_='event-item')
            
            for element in event_elements:
                events.append({
                    'title': element.find('h3').text.strip(),
                    'date': element.find('time').get('datetime'),
                    'location': element.find('span', class_='location').text.strip(),
                    'description': element.find('div', class_='description').text.strip()
                })
            
            return events
        except Exception as e:
            self.logger.error(f"Error scraping events: {str(e)}")
            return []
    
    def scrape_faculty_data(self) -> Dict:
        """Scrape faculty information from department pages"""
        departments = {
            'FME': 'faculty-of-mechanical-engineering',
            'FEE': 'faculty-of-electrical-engineering',
            'FCSE': 'faculty-of-computer-science-engineering',
            'FMC': 'faculty-of-materials-chemical-engineering',
            'FES': 'faculty-of-engineering-sciences'
        }
        
        faculty_data = {}
        
        for dept_code, dept_url in departments.items():
            try:
                soup = self.fetch_page(f"{self.base_url}/academics/{dept_url}")
                if not soup:
                    continue
                
                faculty_members = []
                faculty_elements = soup.find_all('div', class_='faculty-member')
                
                for element in faculty_elements:
                    faculty_members.append({
                        'name': element.find('h3').text.strip(),
                        'designation': element.find('span', class_='designation').text.strip(),
                        'specialization': element.find('span', class_='specialization').text.strip(),
                        'email': element.find('a', class_='email').get('href').replace('mailto:', '')
                    })
                
                faculty_data[dept_code] = faculty_members
            
            except Exception as e:
                self.logger.error(f"Error scraping faculty data for {dept_code}: {str(e)}")
        
        return faculty_data
    
    def scrape_research_publications(self) -> List[Dict]:
        """Scrape recent research publications"""
        try:
            soup = self.fetch_page(f"{self.base_url}/research/publications")
            if not soup:
                return []
            
            publications = []
            pub_elements = soup.find_all('div', class_='publication')
            
            for element in pub_elements:
                publications.append({
                    'title': element.find('h4').text.strip(),
                    'authors': element.find('p', class_='authors').text.strip(),
                    'journal': element.find('em').text.strip(),
                    'year': element.find('span', class_='year').text.strip()
                })
            
            return publications
        except Exception as e:
            self.logger.error(f"Error scraping publications: {str(e)}")
            return []
    
    def update_dataset(self):
        """Update the main dataset with fresh data"""
        try:
            # Load existing dataset
            dataset_path = self.data_dir / 'giki_dataset.json'
            if dataset_path.exists():
                with open(dataset_path, 'r') as f:
                    dataset = json.load(f)
            else:
                dataset = {}
            
            # Update with fresh data
            dataset['last_updated'] = datetime.now().isoformat()
            dataset['news'] = self.scrape_news()
            dataset['events'] = self.scrape_events()
            dataset['faculty'] = self.scrape_faculty_data()
            dataset['publications'] = self.scrape_research_publications()
            
            # Save updated dataset
            with open(dataset_path, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            self.logger.info("Dataset successfully updated")
            return True
        except Exception as e:
            self.logger.error(f"Error updating dataset: {str(e)}")
            return False

if __name__ == "__main__":
    scraper = GIKIDataScraper()
    scraper.update_dataset() 