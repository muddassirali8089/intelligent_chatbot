import logging
from pathlib import Path
from data_processor import GIKIDataProcessor
from advanced_model import GIKIAdvancedModel
import torch
import wandb
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('Training')

def main():
    logger = setup_logging()
    logger.info("Starting training process")
    
    try:
        # Step 1: Initialize data processor and collect data
        logger.info("Initializing data processor")
        processor = GIKIDataProcessor()
        
        # Step 2: Create dataset
        logger.info("Creating dataset")
        success = processor.create_dataset()
        if not success:
            logger.error("Failed to create dataset")
            return
        
        # Step 3: Load the processed data
        logger.info("Loading processed data")
        train_df, test_df = processor.load_dataset()
        if train_df is None or test_df is None:
            logger.error("Failed to load dataset")
            return
        
        logger.info(f"Dataset loaded - Training size: {len(train_df)}, Test size: {len(test_df)}")
        
        # Step 4: Initialize the model
        logger.info("Initializing model")
        model = GIKIAdvancedModel(model_name="bert-large-uncased-whole-word-masking-finetuned-squad")
        
        # Step 5: Configure training parameters
        training_config = {
            'epochs': 10,
            'batch_size': 8,
            'learning_rate': 2e-5,
            'max_length': 512,
            'model_name': model.model_name,
            'device': str(model.device)
        }
        
        # Log training configuration
        logger.info(f"Training configuration: {training_config}")
        
        # Step 6: Train the model
        logger.info("Starting model training")
        success = model.train(
            train_df=train_df,
            test_df=test_df,
            epochs=training_config['epochs'],
            batch_size=training_config['batch_size'],
            learning_rate=training_config['learning_rate']
        )
        
        if success:
            logger.info("Training completed successfully")
            
            # Step 7: Save training metadata
            metadata = {
                'training_completed': datetime.now().isoformat(),
                'dataset_size': len(train_df) + len(test_df),
                'config': training_config
            }
            
            metadata_file = Path("models") / "training_metadata.json"
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("Training metadata saved")
            
            # Step 8: Test the model with sample questions
            logger.info("Testing model with sample questions")
            test_questions = [
                "What is GIKI?",
                "When was GIKI established?",
                "What programs does GIKI offer?",
                "Where is GIKI located?",
                "How can I get admission in GIKI?"
            ]
            
            context = """GIKI (Ghulam Ishaq Khan Institute of Engineering Sciences and Technology) 
            is one of Pakistan's premier engineering universities. Established in 1993, it is located 
            in Topi, Khyber Pakhtunkhwa. The institute offers various engineering programs including 
            Computer Engineering, Electrical Engineering, Mechanical Engineering, and more. GIKI is known 
            for its high academic standards and research quality."""
            
            logger.info("Sample model responses:")
            for question in test_questions:
                answer, confidence = model.get_answer(question, context)
                logger.info(f"Q: {question}")
                logger.info(f"A: {answer} (confidence: {confidence:.2f})")
                logger.info("-" * 50)
        
        else:
            logger.error("Training failed")
    
    except Exception as e:
        logger.error(f"Error during training process: {str(e)}")
        raise
    
    finally:
        # Clean up wandb
        if wandb.run is not None:
            wandb.finish()

if __name__ == "__main__":
    main() 