from flask import Flask, request, jsonify
import boto3
import json
import os
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration (same as FastAPI version)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '11434'))
ALLOWED_MODELS = ["anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-haiku-20240307-v1:0"]
DEFAULT_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
MAX_TOKENS = 8129
ANTHROPIC_VERSION = "bedrock-2023-05-31"
DEFAULT_TEMPERATURE = 1.0
DEFAULT_TOP_K = 250
DEFAULT_TOP_P = 0.999

# Initialize AWS clients (same as FastAPI version)
bedrock = boto3.client(
    service_name='bedrock',
    region_name=AWS_REGION
)

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION
)

# Error messages (same structure)
OllamaCompatibleErrors = {
    "MODEL_NOT_FOUND": {"error": "model not found"},
    "MODEL_NOT_SUPPORTED": {"error": "model not supported"},
    "INVALID_PARAMETER": {"error": "invalid parameter"},
    "MISSING_INPUT": {"error": "either prompt or messages must be provided"}
}

@app.route('/api/tags', methods=['GET'])
def list_models():
    try:
        models = []
        for model in ALLOWED_MODELS:
            models.append({
                "name": model,
                "id": model,
                "object": "model",
                "created_at": "",
                "modified_at": "",
                "owner": "amazon",
                "description": model,
                "format": "bedrock",
                "tags": ["bedrock"]
            })
        return jsonify({"models": models})
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    start_time = time.time()
    try:
        data = request.get_json()
        logger.info(f"Received generation request for model: {data.get('model')}")

        # Validate request
        model = data.get('model', DEFAULT_MODEL)
        if model not in ALLOWED_MODELS:
            return jsonify(OllamaCompatibleErrors["MODEL_NOT_SUPPORTED"]), 400
            
        if not data.get('prompt') and not data.get('messages'):
            return jsonify(OllamaCompatibleErrors["MISSING_INPUT"]), 400

        # Prepare payload (same structure as FastAPI version)
        payload = {
            "anthropic_version": ANTHROPIC_VERSION,
            "max_tokens": MAX_TOKENS,
            "system": data.get('system'),
            "temperature": DEFAULT_TEMPERATURE,
            "top_k": DEFAULT_TOP_K,
            "top_p": DEFAULT_TOP_P,
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": data.get('prompt')
                }]
            }]
        }

        # Invoke model
        response = bedrock_runtime.invoke_model(
            modelId=model,
            body=json.dumps(payload)
        )
        response_body = json.loads(response['body'].read())
        
        # Process response
        result = "".join([content.get('text', '') for content in response_body.get('content', [])])
        
        # Calculate timing
        duration_ms = int((time.time() - start_time) * 1000)
        usage = response_body.get('usage', {})
        
        # Return OLLAMA-compatible response
        return jsonify({
            "model": model,
            "created_at": str(int(time.time())),
            "response": result,
            "done": True,
            "total_duration": duration_ms,
            "load_duration": duration_ms,
            "prompt_eval_count": usage.get('input_tokens', 0),
            "eval_count": usage.get('output_tokens', 0)
        })

    except Exception as e:
        logger.error(f"Error during generation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host=APP_HOST, port=APP_PORT) 