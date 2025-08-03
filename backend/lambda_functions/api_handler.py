import json
import boto3
import logging
from datetime import datetime
from typing import Dict, Any
import uuid
import base64
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Environment variables
TRANSLATION_JOBS_TABLE = os.environ['TRANSLATION_JOBS_TABLE']
INPUT_BUCKET = os.environ['INPUT_BUCKET']
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']
COGNITO_USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']
TRANSLATION_WORKER_FUNCTION_NAME = os.environ['TRANSLATION_WORKER_FUNCTION_NAME']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
    'Access-Control-Max-Age': '86400',
    'Access-Control-Allow-Credentials': 'true'
}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for API requests and document processing."""
    logger.info("=== LAMBDA HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {context}")
    
    try:
        
        if 'Records' in event and event['Records'] and 's3' in event['Records'][0]:
            logger.info("Processing S3 event for document processing")
            return process_s3_event(event)
        
        # Handle API Gateway requests
        http_method = event['httpMethod']
        path = event['path']
        path_parameters = event.get('pathParameters') or {}
        
        logger.info(f"HTTP Method: {http_method}")
        logger.info(f"Path: {path}")
        logger.info(f"Path Parameters: {path_parameters}")
        logger.info(f"Request Headers: {event.get('headers', {})}")
        logger.info(f"Query Parameters: {event.get('queryStringParameters', {})}")
        
       
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
    
        logger.info(f"Routing request: {http_method} {path}")
        
        if http_method == 'GET' and path == '/languages':
            logger.info("Routing to get_languages")
            return get_languages()
        elif http_method == 'GET' and path == '/translations':
            logger.info("Routing to get_translations")
            return get_translations(event)
        elif http_method == 'POST' and path == '/translations':
            logger.info("Routing to create_translation")
            return create_translation(event)
        elif http_method == 'GET' and path.startswith('/translations/'):
            logger.info(f"Routing to get_translation with ID: {path_parameters.get('id')}")
            return get_translation(path_parameters.get('id'), event)
        else:
            logger.warning(f"No route found for {http_method} {path}")
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Route not found'})
            }
    except Exception as e:
        logger.error(f"=== LAMBDA HANDLER ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        
        error_message = 'Internal server error'
        status_code = 500
        
        if 'Unauthorized' in str(e):
            error_message = 'Unauthorized access'
            status_code = 401
        elif 'Invalid JSON' in str(e):
            error_message = 'Invalid request format'
            status_code = 400
        elif 'Missing required fields' in str(e):
            error_message = 'Missing required fields in request'
            status_code = 400
        elif 'S3' in str(e):
            error_message = 'File upload failed'
            status_code = 500
        elif 'DynamoDB' in str(e):
            error_message = 'Database operation failed'
            status_code = 500
            
        return {
            'statusCode': status_code,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': error_message, 'details': str(e)})
        }

def process_s3_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process S3 events for document processing."""
    logger.info("=== PROCESSING S3 EVENT ===")
    
    try:
        for record in event['Records']:
            if record['eventName'].startswith('ObjectCreated'):
                process_document(record['s3'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Documents processed successfully'})
        }
    except Exception as e:
        logger.error(f"Error processing S3 event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to process documents'})
        }

def process_document(s3_event: Dict[str, Any]) -> None:
    """Process a single document from S3 event."""
    bucket = s3_event['bucket']['name']
    key = s3_event['object']['key']
    
   
    import urllib.parse
    decoded_key = urllib.parse.unquote_plus(key)
    
    logger.info(f"Processing document: {key} from bucket: {bucket}")
    logger.info(f"Decoded key: {decoded_key}")
    
    try:
      
        response = s3_client.get_object(Bucket=bucket, Key=decoded_key)
  
        file_name = key.split('/')[-1]  
        if file_name.lower().endswith('.pdf'):
           
            import base64
            content_bytes = response['Body'].read()
            content = base64.b64encode(content_bytes).decode('utf-8')
            logger.info(f"PDF file read as base64, length: {len(content)}")
        else:
          
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Text file read as UTF-8, length: {len(content)}")
        
      
        job_id = extract_job_id_from_key(decoded_key)
        
      
        job = get_translation_job(job_id)
        
        if not job:
            logger.error(f"Translation job not found for key: {decoded_key}")
            return
        
      
        update_job_status(job_id, 'processing')
        
       
        invoke_translation_worker(job_id, content, job)
        logger.info(f"Invoked translation worker for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        
   
        job_id = extract_job_id_from_key(decoded_key)
        update_job_status(job_id, 'failed')
        
        raise e

def extract_job_id_from_key(key: str) -> str:
    """Extract job ID from S3 key format: input/{user_id}/{job_id}/{filename}"""
    parts = key.split('/')
    return parts[2] if len(parts) > 2 else ''

def get_translation_job(job_id: str) -> Dict[str, Any]:
    """Get translation job from DynamoDB."""
    try:
        table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
        response = table.get_item(Key={'id': job_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting translation job: {str(e)}")
        return None

def update_job_status(job_id: str, status: str) -> None:
    """Update job status in DynamoDB."""
    try:
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
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")

def invoke_translation_worker(job_id: str, content: str, job: Dict[str, Any]) -> None:
    """Invoke translation worker lambda directly."""
    try:
        payload = {
            'job_id': job_id,
            'content': content,
            'source_language': job['source_language'],
            'target_language': job['target_language'],
            'file_name': job['file_name'],
            'user_id': job['user_id']
        }
        
        lambda_client.invoke(
            FunctionName=TRANSLATION_WORKER_FUNCTION_NAME,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps(payload)
        )
    except Exception as e:
        logger.error(f"Error invoking translation worker: {str(e)}")
        raise e

def get_languages() -> Dict[str, Any]:
    """Get list of supported languages."""
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'es', 'name': 'Spanish'},
        {'code': 'fr', 'name': 'French'},
        {'code': 'de', 'name': 'German'},
        {'code': 'it', 'name': 'Italian'},
        {'code': 'pt', 'name': 'Portuguese'},
        {'code': 'ru', 'name': 'Russian'},
        {'code': 'ja', 'name': 'Japanese'},
        {'code': 'ko', 'name': 'Korean'},
        {'code': 'zh', 'name': 'Chinese'},
        {'code': 'ar', 'name': 'Arabic'},
        {'code': 'hi', 'name': 'Hindi'},
        {'code': 'nl', 'name': 'Dutch'},
        {'code': 'sv', 'name': 'Swedish'},
        {'code': 'pl', 'name': 'Polish'}
    ]
    
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps(languages)
    }

def get_translations(event: Dict[str, Any]) -> Dict[str, Any]:
    """Get user's translation jobs with proper user isolation and pre-signed S3 URLs for completed jobs."""
    user_id = get_user_id_from_event(event)
    
    if not user_id:
        return {
            'statusCode': 401,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    try:
        table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
        
     
        response = table.query(
            IndexName='user-id-created-at-index',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id},
            ScanIndexForward=False 
        )
        items = response['Items']
       
        for item in items:
            if item.get('status') == 'completed' and item.get('s3_output_key'):
                try:
                    presigned_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': OUTPUT_BUCKET, 'Key': item['s3_output_key']},
                        ExpiresIn=900  
                    )
                    item['download_url'] = presigned_url
                except Exception as e:
                    logger.error(f"Error generating pre-signed URL for job {item.get('id')}: {str(e)}")
                    item['download_url'] = None
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(items, default=str)
        }
    except Exception as e:
        logger.error(f"Error getting translations: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Failed to get translations'})
        }

def create_translation(event: Dict[str, Any]) -> Dict[str, Any]:
    """Create new translation job with user isolation."""
    logger.info("=== CREATE TRANSLATION START ===")
    logger.info(f"Event keys: {list(event.keys())}")
    
    user_id = get_user_id_from_event(event)
    logger.info(f"User ID: {user_id}")
    
    if not user_id:
        logger.warning("No user ID found - unauthorized request")
        return {
            'statusCode': 401,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    try:
        # Add detailed logging for debugging
        logger.info(f"Event body type: {type(event.get('body'))}")
        logger.info(f"Event body length: {len(event.get('body', ''))}")
        logger.info(f"Event body preview: {repr(event.get('body', '')[:200])}...")
        logger.info(f"Event headers: {event.get('headers', {})}")
        logger.info(f"Content-Type header: {event.get('headers', {}).get('Content-Type', 'NOT_SET')}")
        logger.info(f"Content-Length header: {event.get('headers', {}).get('Content-Length', 'NOT_SET')}")
        logger.info(f"User-Agent header: {event.get('headers', {}).get('User-Agent', 'NOT_SET')}")
        logger.info(f"Authorization header present: {'Authorization' in event.get('headers', {})}")
        
        
        if not event.get('body'):
            logger.error("Request body is empty or missing")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        
        try:
            logger.info("Attempting to parse JSON body...")
            
           
            body_content = event['body']
            is_base64 = event.get('isBase64Encoded', False)
            
            if is_base64:
                logger.info("Body is base64 encoded, decoding...")
                import base64
                try:
                    body_content = base64.b64decode(body_content).decode('utf-8')
                    logger.info("Base64 decode successful")
                except Exception as decode_error:
                    logger.error(f"Base64 decode failed: {decode_error}")
                    return {
                        'statusCode': 400,
                        'headers': CORS_HEADERS,
                        'body': json.dumps({'error': 'Invalid base64 encoding in request body'})
                    }
            
            body = json.loads(body_content)
            logger.info(f"JSON parsed successfully. Body keys: {list(body.keys())}")
            logger.info(f"Body values preview:")
            for key, value in body.items():
                if isinstance(value, str):
                    logger.info(f"  {key}: {repr(value[:100])}... (length: {len(value)})")
                else:
                    logger.info(f"  {key}: {value}")
        except json.JSONDecodeError as json_error:
            logger.error(f"=== JSON PARSING ERROR ===")
            logger.error(f"JSON error type: {type(json_error).__name__}")
            logger.error(f"JSON error message: {json_error}")
            logger.error(f"JSON error line: {json_error.lineno}")
            logger.error(f"JSON error column: {json_error.colno}")
            logger.error(f"JSON error position: {json_error.pos}")
            logger.error(f"Body content (raw): {repr(event['body'])}")
            logger.error(f"Body content (first 500 chars): {repr(event['body'][:500])}")
            logger.error(f"Body content (last 500 chars): {repr(event['body'][-500:])}")
            logger.error(f"Is base64 encoded: {event.get('isBase64Encoded', False)}")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
        
        file_name = body.get('fileName')
        source_language = body.get('sourceLanguage')
        target_language = body.get('targetLanguage')
        file_content = body.get('fileContent')
        file_type = body.get('fileType', 'text/plain')
        
        logger.info(f"Extracted fields:")
        logger.info(f"  - fileName: {file_name} (type: {type(file_name)})")
        logger.info(f"  - sourceLanguage: {source_language} (type: {type(source_language)})")
        logger.info(f"  - targetLanguage: {target_language} (type: {type(target_language)})")
        logger.info(f"  - fileContent length: {len(file_content) if file_content else 0}")
        logger.info(f"  - fileType: {file_type}")
        if file_type == 'application/pdf':
            logger.info(f"  - fileContent (PDF base64): {repr(file_content[:100]) if file_content else 'None'}...")
        else:
            logger.info(f"  - fileContent preview: {repr(file_content[:100]) if file_content else 'None'}...")
        
     
        logger.info(f"Field validation:")
        logger.info(f"  - fileName valid: {bool(file_name and isinstance(file_name, str))}")
        logger.info(f"  - sourceLanguage valid: {bool(source_language and isinstance(source_language, str))}")
        logger.info(f"  - targetLanguage valid: {bool(target_language and isinstance(target_language, str))}")
        logger.info(f"  - fileContent valid: {bool(file_content and isinstance(file_content, str))}")
        
        if not all([file_name, source_language, target_language, file_content]):
            logger.error("Missing required fields in request")
            logger.error(f"  - fileName present: {bool(file_name)}")
            logger.error(f"  - sourceLanguage present: {bool(source_language)}")
            logger.error(f"  - targetLanguage present: {bool(target_language)}")
            logger.error(f"  - fileContent present: {bool(file_content)}")
            logger.error(f"  - fileName type: {type(file_name)}")
            logger.error(f"  - sourceLanguage type: {type(source_language)}")
            logger.error(f"  - targetLanguage type: {type(target_language)}")
            logger.error(f"  - fileContent type: {type(file_content)}")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        job_id = str(uuid.uuid4())
        input_key = f"input/{user_id}/{job_id}/{file_name}"
        
        logger.info(f"Generated job ID: {job_id}")
        logger.info(f"S3 input key: {input_key}")
        
        # Upload file to S3 with user-specific path
        try:
            logger.info("Uploading file to S3...")
            logger.info(f"S3 bucket: {INPUT_BUCKET}")
            logger.info(f"S3 key: {input_key}")
            
         
            if file_type == 'application/pdf':
               
                import base64
                file_bytes = base64.b64decode(file_content)
                logger.info(f"PDF file size: {len(file_bytes)} bytes")
                
                s3_response = s3_client.put_object(
                    Bucket=INPUT_BUCKET,
                    Key=input_key,
                    Body=file_bytes,
                    ContentType='application/pdf',
                    ServerSideEncryption='AES256'
                )
            else:
                # For text files, upload as UTF-8 text
                file_bytes = file_content.encode('utf-8')
                logger.info(f"Text file size: {len(file_bytes)} bytes")
                
                s3_response = s3_client.put_object(
                    Bucket=INPUT_BUCKET,
                    Key=input_key,
                    Body=file_bytes,
                    ContentType='text/plain',
                    ServerSideEncryption='AES256'
                )
            
            logger.info(f"S3 upload successful. ETag: {s3_response.get('ETag')}")
            logger.info(f"S3 response: {s3_response}")
        except Exception as s3_error:
            logger.error(f"S3 upload failed: {s3_error}")
            logger.error(f"S3 error type: {type(s3_error).__name__}")
            logger.error(f"S3 error details: {str(s3_error)}")
            import traceback
            logger.error(f"S3 error traceback: {traceback.format_exc()}")
            raise
        
     
        translation_job = {
            'id': job_id,
            'user_id': user_id,  
            'file_name': file_name,
            'source_language': source_language,
            'target_language': target_language,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            's3_input_key': input_key,
            'original_text': file_content,
            'expires_at': int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  
        }
        
        logger.info("Saving translation job to DynamoDB...")
        logger.info(f"DynamoDB table: {TRANSLATION_JOBS_TABLE}")
        logger.info(f"Translation job keys: {list(translation_job.keys())}")
        logger.info(f"Translation job preview: {json.dumps(translation_job, default=str)[:500]}...")
        
        try:
            table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
            table.put_item(Item=translation_job)
            logger.info("Translation job saved to DynamoDB successfully")
        except Exception as db_error:
            logger.error(f"DynamoDB save failed: {db_error}")
            logger.error(f"DynamoDB error type: {type(db_error).__name__}")
            logger.error(f"DynamoDB error details: {str(db_error)}")
            import traceback
            logger.error(f"DynamoDB error traceback: {traceback.format_exc()}")
            raise
        
        
        try:
            logger.info("Invoking translation worker...")
            invoke_translation_worker(job_id, file_content, translation_job)
            logger.info("Translation worker invoked successfully")
        except Exception as worker_error:
            logger.error(f"Failed to invoke translation worker: {worker_error}")
           
        
        logger.info("=== CREATE TRANSLATION SUCCESS ===")
        return {
            'statusCode': 201,
            'headers': CORS_HEADERS,
            'body': json.dumps(translation_job, default=str)
        }
    except Exception as e:
        logger.error(f"=== CREATE TRANSLATION ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Failed to create translation'})
        }

def get_translation(translation_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """Get specific translation job with user isolation and pre-signed S3 URL if completed."""
    user_id = get_user_id_from_event(event)
    
    if not user_id:
        return {
            'statusCode': 401,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    try:
        table = dynamodb.Table(TRANSLATION_JOBS_TABLE)
        response = table.get_item(Key={'id': translation_id})
        
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Translation not found'})
            }
        
    
        if item.get('user_id') != user_id:
            return {
                'statusCode': 403,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Access denied'})
            }
        
       
        if item.get('status') == 'completed' and item.get('s3_output_key'):
            try:
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': OUTPUT_BUCKET, 'Key': item['s3_output_key']},
                    ExpiresIn=900  # 15 minutes
                )
                item['download_url'] = presigned_url
            except Exception as e:
                logger.error(f"Error generating pre-signed URL: {str(e)}")
                item['download_url'] = None
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(item, default=str)
        }
    except Exception as e:
        logger.error(f"Error getting translation: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Failed to get translation'})
        }

def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """Extract user ID from Cognito JWT token with proper validation."""
    logger.info("=== EXTRACTING USER ID ===")
    try:
     
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        
        logger.info(f"Request context keys: {list(request_context.keys())}")
        logger.info(f"Authorizer keys: {list(authorizer.keys())}")
        logger.info(f"Claims keys: {list(claims.keys())}")
        logger.info(f"All claims: {claims}")
        
    
        user_id = claims.get('sub') or claims.get('cognito:username')
        
        logger.info(f"Extracted user ID: {user_id}")
        
        if not user_id:
            logger.warning("No user ID found in token claims")
            logger.warning(f"Available claims: {claims}")
            return None
        
        return user_id
    except Exception as e:
        logger.error(f"=== USER ID EXTRACTION ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None