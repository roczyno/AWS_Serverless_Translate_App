import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to handle CORS preflight requests and add CORS headers to responses.
    """
    logger.info(f"Event: {json.dumps(event)}")
    
  
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
 
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'true'
    }
    
   
    if http_method == 'OPTIONS':
        logger.info("Handling CORS preflight request")
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }
    
   
    logger.info("Returning CORS headers for main request")
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'corsHeaders': cors_headers,
            'originalRequest': {
                'httpMethod': http_method,
                'path': path,
                'body': event.get('body'),
                'headers': event.get('headers'),
                'queryStringParameters': event.get('queryStringParameters'),
                'pathParameters': event.get('pathParameters')
            }
        })
    } 