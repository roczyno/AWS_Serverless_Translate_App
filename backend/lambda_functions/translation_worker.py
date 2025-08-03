import json
import boto3
import logging
import os
from datetime import datetime
from typing import Dict, Any, List


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
translate_client = boto3.client('translate')


TRANSLATION_JOBS_TABLE = os.environ['TRANSLATION_JOBS_TABLE']
INPUT_BUCKET = os.environ['INPUT_BUCKET']
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing translation requests.
    Invoked directly by API handler.
    """
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
       
        logger.info("Processing direct lambda invocation")
        process_translation_request_direct(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Translation request processed successfully'})
        }
    except Exception as e:
        logger.error(f"Error processing translation request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to process translation request'})
        }

def process_translation_request_direct(event: Dict[str, Any]) -> None:
    """Process a single translation request from direct lambda invocation."""
    try:
        job_id = event['job_id']
        content = event['content']
        source_language = event['source_language']
        target_language = event['target_language']
        file_name = event['file_name']
        user_id = event['user_id']
        
        logger.info(f"Processing translation for job: {job_id}")
        logger.info(f"Source language: {source_language}")
        logger.info(f"Target language: {target_language}")
        logger.info(f"Content length: {len(content)}")
        logger.info(f"File name: {file_name}")
        logger.info(f"User ID: {user_id}")
        
     
        logger.info(f"Environment variables:")
        logger.info(f"  TRANSLATION_JOBS_TABLE: {TRANSLATION_JOBS_TABLE}")
        logger.info(f"  INPUT_BUCKET: {INPUT_BUCKET}")
        logger.info(f"  OUTPUT_BUCKET: {OUTPUT_BUCKET}")
        
      
        logger.info("Updating job status to processing...")
        update_job_status(job_id, 'processing')
        logger.info("Job status updated to processing successfully")
        
        
        if file_name.lower().endswith('.pdf'):
          
            import base64
            try:
                pdf_bytes = base64.b64decode(content)
               
                logger.warning("PDF translation not yet implemented - using placeholder")
                translated_content = f"[PDF Translation Placeholder] Original content length: {len(pdf_bytes)} bytes"
            except Exception as pdf_error:
                logger.error(f"Error processing PDF: {pdf_error}")
                translated_content = f"[PDF Processing Error] {str(pdf_error)}"
        else:
            
            logger.info("Starting text translation...")
            translated_content = translate_text(content, source_language, target_language)
            logger.info("Text translation completed")
        
     
        logger.info("Saving translated content to S3...")
        output_key = f"output/{user_id}/{job_id}/{file_name}"
        save_translated_content(output_key, translated_content)
        logger.info("Translated content saved to S3 successfully")
        
       
        logger.info("Updating job completion...")
        update_job_completion(job_id, translated_content, output_key)
        logger.info("Job completion updated successfully")
        
        logger.info(f"Translation completed for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Error processing translation request: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
       
        try:
            job_id = event['job_id']
            update_job_status(job_id, 'failed')
            logger.info("Job status updated to failed")
        except Exception as status_error:
            logger.error(f"Failed to update job status to failed: {status_error}")
        
        raise e

def translate_text(text: str, source_language: str, target_language: str) -> str:
    """Translate text using AWS Translate."""
    try:
        logger.info(f"Starting translation from {source_language} to {target_language}")
        logger.info(f"Text length: {len(text)}")
        
       
        max_chunk_size = 4000  
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        logger.info(f"Text split into {len(chunks)} chunks")
        
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)}")
            response = translate_client.translate_text(
                Text=chunk,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language
            )
            translated_chunks.append(response['TranslatedText'])
        
        result = ''.join(translated_chunks)
        logger.info(f"Translation completed. Result length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise e

def save_translated_content(output_key: str, content: str) -> None:
    """Save translated content to S3 output bucket."""
    try:
        logger.info(f"Saving translated content to S3: {OUTPUT_BUCKET}/{output_key}")
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=output_key,
            Body=content.encode('utf-8'),
            ContentType='text/plain',
            ServerSideEncryption='AES256'
        )
        logger.info("Translated content saved successfully")
    except Exception as e:
        logger.error(f"Error saving translated content: {str(e)}")
        raise e

def update_job_completion(job_id: str, translated_text: str, output_key: str) -> None:
    """Update job with completion details in DynamoDB."""
    try:
        logger.info(f"Updating job completion for job: {job_id}")
        table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
        table.update_item(
            Key={'id': job_id},
            UpdateExpression='SET #status = :status, translated_text = :translated_text, s3_output_key = :output_key, completed_at = :completed_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':translated_text': translated_text,
                ':output_key': output_key,
                ':completed_at': datetime.utcnow().isoformat()
            }
        )
        logger.info("Job completion updated successfully")
    except Exception as e:
        logger.error(f"Error updating job completion: {str(e)}")
        raise e

def update_job_status(job_id: str, status: str) -> None:
    """Update job status in DynamoDB."""
    try:
        logger.info(f"Updating job status to {status} for job: {job_id}")
        table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
        table.update_item(
            Key={'id': job_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': status,
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        logger.info("Job status updated successfully")
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")
        raise e

def test_translation_worker():
    """Test function to verify translation worker is working."""
    test_event = {
        'job_id': 'test-job-123',
        'content': 'Hello world',
        'source_language': 'en',
        'target_language': 'es',
        'file_name': 'test.txt',
        'user_id': 'test-user'
    }
    
    try:
        process_translation_request_direct(test_event)
        print("Test successful!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

