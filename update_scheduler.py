import schedule
import time
from data_scraper import GIKIDataScraper
from model_trainer import GIKIModelTrainer
import logging
from pathlib import Path

class UpdateScheduler:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.setup_logging()
        self.scraper = GIKIDataScraper()
        self.trainer = GIKIModelTrainer()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.data_dir / 'scheduler.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('Scheduler')
    
    def update_data_and_model(self):
        """Update dataset and retrain model"""
        try:
            self.logger.info("Starting data update...")
            if self.scraper.update_dataset():
                self.logger.info("Dataset updated successfully")
                
                self.logger.info("Starting model training...")
                if self.trainer.train():
                    self.logger.info("Model training completed successfully")
                else:
                    self.logger.error("Model training failed")
            else:
                self.logger.error("Dataset update failed")
        
        except Exception as e:
            self.logger.error(f"Error in update process: {str(e)}")
    
    def run(self):
        """Run the scheduler"""
        # Schedule updates
        schedule.every().day.at("00:00").do(self.update_data_and_model)  # Daily update at midnight
        schedule.every().day.at("12:00").do(self.update_data_and_model)  # Daily update at noon
        
        # Initial update
        self.update_data_and_model()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = UpdateScheduler()
    scheduler.run() 