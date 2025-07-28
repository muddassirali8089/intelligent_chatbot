import subprocess
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('Pipeline')

def run_command(command: str, logger: logging.Logger) -> bool:
    """Run a command and log its output"""
    try:
        logger.info(f"Running command: {command}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True
        )
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.info(output.strip())
        
        # Get the return code
        return_code = process.poll()
        
        if return_code == 0:
            logger.info(f"Command completed successfully")
            return True
        else:
            error = process.stderr.read()
            logger.error(f"Command failed with return code {return_code}")
            logger.error(f"Error output: {error}")
            return False
            
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    logger = logging.getLogger('Pipeline')
    
    try:
        import torch
        import transformers
        import pandas
        import nltk
        import wandb
        import streamlit
        logger.info("All required packages are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing required package: {str(e)}")
        return False

def main():
    logger = setup_logging()
    logger.info("Starting GIKI Chatbot pipeline")
    
    try:
        # Step 1: Check requirements
        logger.info("Checking requirements...")
        if not check_requirements():
            logger.error("Missing required packages. Please run: pip install -r requirements.txt")
            return
        
        # Step 2: Create necessary directories
        for dir_name in ['data', 'models', 'logs', 'dataset']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Step 3: Run data collection and processing
        logger.info("Starting data collection and processing...")
        if not run_command(f"{sys.executable} data_processor.py", logger):
            logger.error("Data processing failed")
            return
        
        # Step 4: Run model training
        logger.info("Starting model training...")
        if not run_command(f"{sys.executable} train.py", logger):
            logger.error("Model training failed")
            return
        
        # Step 5: Start the chatbot
        logger.info("Starting the chatbot...")
        run_command(f"streamlit run chatbot.py", logger)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 