---
title: "OMAi API Reference"
tags: [api, reference, documentation]
type: reference
weight: 1.3
---

# OMAi API Reference

## Authentication

### API Key Authentication
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.omai.ai/v1/endpoint
```

### Session-based Authentication
```python
import requests

session = requests.Session()
session.auth = ('username', 'password')
response = session.post('https://api.omai.ai/v1/auth/login')
```

## Endpoints

### Chat API

#### POST /v1/chat/completions
Create a chat completion request.

**Request Body:**
```json
{
  "model": "omai-gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

### Embeddings API

#### POST /v1/embeddings
Generate embeddings for text input.

**Request Body:**
```json
{
  "model": "text-embedding-ada-002",
  "input": "The quick brown fox jumps over the lazy dog"
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023064255, -0.009327292, ...],
      "index": 0
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 9,
    "total_tokens": 9
  }
}
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with exponential backoff |

## Rate Limits

| Tier | Requests per minute | Tokens per minute |
|------|--------------------|-------------------|
| Basic | 60 | 40,000 |
| Pro | 3,000 | 2,000,000 |
| Enterprise | Unlimited | Unlimited |

## SDK Examples

### Python
```python
from omai import OMAi

client = OMAi(api_key="your-api-key")

response = client.chat.completions.create(
    model="omai-gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### JavaScript
```javascript
import { OMAi } from 'omai';

const omai = new OMAi({ apiKey: 'your-api-key' });

const response = await omai.chat.completions.create({
  model: 'omai-gpt-4',
  messages: [{ role: 'user', content: 'Hello!' }],
});

console.log(response.choices[0].message.content);
```