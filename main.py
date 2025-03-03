from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import boto3
import json
import os
from typing import Optional, Dict, Any, List, Union
import uvicorn
import time
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
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

# Initialize AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock',
    region_name=AWS_REGION
)

# Initialize runtime client for inference
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION
)

class Message(BaseModel):
    role: str
    content: str

class GenerateRequest(BaseModel):
    model: str
    prompt: Optional[str] = None
    messages: Optional[List[Message]] = None
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[Union[List[int], str]] = None
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    stream: Optional[bool] = False

    @property
    def has_valid_input(self) -> bool:
        return bool(self.prompt or self.messages)

class OllamaCompatibleErrors:
    MODEL_NOT_FOUND = {"error": "model not found"}
    MODEL_NOT_SUPPORTED = {"error": "model not supported"}
    INVALID_PARAMETER = {"error": "invalid parameter"}
    MISSING_INPUT = {"error": "either prompt or messages must be provided"}


@app.get("/api/tags")
async def list_models():
    try:
        # response = bedrock.list_foundation_models()
        models = []
        
        for model in ALLOWED_MODELS:
            model_info = {
                "name": model,
                "id": model,
                "object": "model",
                "created_at": "",  # Bedrock API doesn't provide this
                "modified_at": "",  # Bedrock API doesn't provide this
                "owner": "amazon",
                "description": model,
                "format": "bedrock",
                "parameter_size": "",  # Bedrock API doesn't provide this
                "quantization_level": "",  # Bedrock API doesn't provide this
                "license": "",  # Bedrock API doesn't provide this
                "system_prompt": "",  # Bedrock API doesn't provide this
                "template": "",  # Bedrock API doesn't provide this
                "context_length": 0,
                "tags": ["bedrock"]
            }
            models.append(model_info)

        return {
            "models": models
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    try:
        logger.info(f"Received generation request for model: {request.model}")
        if not request.has_valid_input:
            raise HTTPException(
                status_code=400, 
                detail=OllamaCompatibleErrors.MISSING_INPUT
            )

        start_time = time.time()


        request.model = request.model or DEFAULT_MODEL
        if request.model not in ALLOWED_MODELS:
            raise HTTPException(
                status_code=400, 
                detail=OllamaCompatibleErrors.MODEL_NOT_SUPPORTED
            )

        payload = {
        "anthropic_version": ANTHROPIC_VERSION,
        "max_tokens": MAX_TOKENS,
        "system": request.system ,
        "temperature": DEFAULT_TEMPERATURE,
        "top_k": DEFAULT_TOP_K,
        "top_p": DEFAULT_TOP_P,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text":  request.prompt,
                    }
                ],
            }
        ],
    }

        try:
            response = bedrock_runtime.invoke_model(
                modelId=request.model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
        except bedrock_runtime.exceptions.ValidationException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except bedrock_runtime.exceptions.ModelNotFound as e:
            raise HTTPException(
                status_code=404, 
                detail=OllamaCompatibleErrors.MODEL_NOT_FOUND
            )
        
        response_body = json.loads(response['body'].read())
        result = ""
        for content in response_body.get('content', []):
            result += content.get('text', '')

        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)  # Convert to milliseconds
        input_tokens = response_body.get('usage', {}).get('input_tokens', 0)
        output_tokens = response_body.get('usage', {}).get('output_tokens', 0)
        # Return in OLLAMA format
        return {
            "model": request.model,
            "created_at": str(int(time.time())),
            "response": result,
            "done": True,
            "context": None,
            "total_duration": duration_ms,
            "load_duration": duration_ms,
            "prompt_eval_count": input_tokens,
            "prompt_eval_duration": duration_ms,
            "eval_count": output_tokens,
            "eval_duration": duration_ms
        }

    except Exception as e:
        logger.error(f"Error during generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT, log_level="debug") 
