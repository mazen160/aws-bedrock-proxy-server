<h1 align="center">AWS Bedrock API Proxy Server</h1>

<p align="center">
  <b>Seamlessly interact with AWS Bedrock models through a standardized OLLAMA API format</b>
</p>

A FastAPI-based proxy server that provides an OLLAMA-compatible API interface for AWS Bedrock Claude models. This proxy allows seamless interaction with Claude 3 models through a standardized API format.

## ✨ Features

- **OLLAMA-Compatible API**: Drop-in replacement for OLLAMA API endpoints
- **Claude 3 Support**: Full support for Claude 3 Sonnet and Haiku models
- **Structured Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling with clear error messages
- **AWS Bedrock Integration**: Direct integration with AWS Bedrock service

## 🚀 Supported Models

Currently supported AWS Bedrock models:

- Claude 3.5 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
- Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`)
  
Additional AWS Bedrock models can be added. Contributions are welcome!

### ❓ Why does this project support limited models?

The focus is on supporting well-tested models that can be used across a wide range of use cases. Supporting all models without proper testing could lead to suboptimal results. 

## 📋 Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS credentials configured


## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mazen160/aws-bedrock-proxy-server
   cd aws-bedrock-proxy-server
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mazen160/aws-bedrock-proxy-server
cd aws-bedrock-proxy-server

# Set up Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure AWS credentials
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Start the server
python main.py
```

## 🐳 Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or using Docker directly
docker build -t bedrock-proxy .
docker run -p 11434:11434 \
  -e AWS_ACCESS_KEY_ID="your-key-id" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-key" \
  -e AWS_REGION="us-east-1" \
  bedrock-proxy
```

## ⚙️ Environment Variables

The application can be configured using the following environment variables:

### 🔧 AWS Configuration
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_SESSION_TOKEN`: Your AWS session token (if using temporary credentials)
- `AWS_REGION`: AWS region where Bedrock is enabled

### 🔧 APP Configuration
- `APP_HOST`: 127.0.0.1
- `APP_PORT`: 11434 (default OLLAMA port)


## 🖥️ Usage

1. **Start the server**:
   ```bash
   $ python main.py
   ```
   The server will start on `http://127.0.0.1:11434` by default.

2. **List available models**:
   ```bash
   curl http://127.0.0.1:11434/api/tags
   ```

3. **Generate text**:
   ```bash
   curl -X POST http://127.0.0.1:11434/api/generate \
   -H "Content-Type: application/json" \
   -d '{
       "model": "anthropic.claude-3-haiku-20240307-v1:0",
       "prompt": "What is the capital of France?",
       "system": "You are a helpful assistant.",
       "stream": false
   }'
   ```

## 📚 API Reference

### `GET /api/tags`

List available supported models.

**Response Example**:
```json
{
  "models": [
    {
      "name": "anthropic.claude-3-sonnet-20240229-v1:0",
      "id": "anthropic.claude-3-sonnet-20240229-v1:0",
      "object": "model",
      "owner": "amazon",
      "format": "bedrock",
      "tags": ["bedrock"]
    },
    {
      "name": "anthropic.claude-3-haiku-20240307-v1:0",
      "id": "anthropic.claude-3-haiku-20240307-v1:0",
      "object": "model",
      "owner": "amazon",
      "format": "bedrock",
      "tags": ["bedrock"]
    }
  ]
}
```

### `POST /api/generate`
Generates text using the specified Claude 3 model.

**Request Body**:
```json
{
  "model": "anthropic.claude-3-haiku-20240307-v1:0",
  "system": "Optional system prompt",
  "prompt": "Your prompt here",
  "stream": false
}
```

**Response Example**:
```json
{
  "model": "anthropic.claude-3-haiku-20240307-v1:0",
  "created_at": "1234567890",
  "response": "Generated text response",
  "done": true,
  "total_duration": 1000,
  "load_duration": 1000,
  "prompt_eval_count": 50,
  "prompt_eval_duration": 500,
  "eval_count": 100,
  "eval_duration": 500
}
```

## 🔒 Security Considerations

By default, the server runs on localhost (127.0.0.1). If you plan to expose this service 
to other machines, make sure to:
- Implement proper authentication
- Use HTTPS/TLS for secure communication
- Consider the security implications of exposing AWS credentials
- Review and restrict AWS IAM permissions appropriately

### 🔑 Required AWS Permissions

The AWS credentials used must have the following permissions:
- `bedrock:InvokeModel`
- `bedrock:ListFoundationModels`

Example IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

# ✨ Want to Contribute?

Contributions are welcome! Feel free to create issues, submit pull requests, or suggest enhancements on GitHub.

# 📜 License

This project is licensed under the MIT License.

---

# 💚 Author

**Mazin Ahmed**

- **Website**: [https://mazinahmed.net](https://mazinahmed.net)
- **Email**: [mazin@mazinahmed.net](mailto:mazin@mazinahmed.net)
- **Twitter**: [https://twitter.com/mazen160](https://twitter.com/mazen160)
- **LinkedIn**: [http://linkedin.com/in/infosecmazinahmed](http://linkedin.com/in/infosecmazinahmed)


