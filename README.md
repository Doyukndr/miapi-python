# MIAPI — Grounded AI Answers API

Official Python client for [MIAPI](https://miapi.uk) — get AI-powered answers grounded in real-time web search.

## Install

```bash
pip install miapi-sdk
```

## Quick Start

```python
from miapi import MIAPI

client = MIAPI("YOUR_API_KEY")

# Get a grounded answer with citations
result = client.answer("What is quantum computing?", citations=True)
print(result.answer)     # AI-generated answer with [1][2] markers
print(result.sources)    # List of source URLs
print(result.confidence) # 0.0 - 1.0
```

## Features

### Web-Grounded Answers
```python
result = client.answer("Who won the last World Cup?")
print(result.answer)
```

### Knowledge Mode — Answer From Your Data
```python
result = client.answer(
    "What is the return policy?",
    mode="knowledge",
    knowledge="Returns accepted within 30 days with receipt..."
)
print(result.answer)
```

### Search Only — Raw Results
```python
sources = client.search("latest AI research papers")
for source in sources:
    print(source.title, source.url)
```

### News Search
```python
news = client.news("technology", num_results=5)
for article in news:
    print(article.title, article.date)
```

### Image Search
```python
images = client.images("golden retriever")
for img in images:
    print(img.url, img.width, img.height)
```

### Streaming
```python
for event in client.stream("Explain quantum computing"):
    if event['type'] == 'answer':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'done':
        print(f"\nDone in {event.get('query_time_ms')}ms")
```

### Check Usage
```python
info = client.usage()
print(f"Used {info.queries_this_month}/{info.monthly_limit} this month")
print(f"Tier: {info.tier}")
```

### Custom Options
```python
result = client.answer(
    "Compare Python and Rust",
    response_format="markdown",   # text, short, json, markdown
    temperature=0.5,              # 0.0 (precise) to 1.0 (creative)
    max_tokens=800,               # Max answer length
    language="French",            # Answer in any language
    search_domains=["wikipedia.org"],  # Restrict sources
    system_prompt="Answer like a professor",
)
```

## Error Handling

```python
from miapi import MIAPI, MIAPIError, RateLimitError, AuthenticationError

client = MIAPI("YOUR_API_KEY")

try:
    result = client.answer("Hello")
except AuthenticationError:
    print("Bad API key")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except MIAPIError as e:
    print(f"Error: {e.message} (HTTP {e.status_code})")
```

## OpenAI Drop-in Replacement

MIAPI is also compatible with the OpenAI Python client:

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_MIAPI_KEY",
    base_url="https://api.miapi.uk/v1"
)

response = client.chat.completions.create(
    model="miapi-grounded",
    messages=[{"role": "user", "content": "What is AI?"}]
)
print(response.choices[0].message.content)
```

## Get Your API Key

Sign up free at [miapi.uk](https://miapi.uk) — 500 queries/month included.

## Links

- [Website](https://miapi.uk)
- [API Docs](https://miapi.uk/#docs)
- [Playground](https://miapi.uk/#playground)
- [Pricing](https://miapi.uk/#pricing)
