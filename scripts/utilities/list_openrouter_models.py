"""
List Available OpenRouter Models
"""

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def list_models():
    """Fetch available models from OpenRouter."""
    
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    print("Fetching available models from OpenRouter...\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            models = result.get("data", [])
            
            # Filter for free models
            free_models = [m for m in models if m.get("pricing", {}).get("prompt", "0") == "0"]
            
            print(f"{'='*80}")
            print(f"FREE MODELS (Total: {len(free_models)})")
            print(f"{'='*80}\n")
            
            for model in free_models[:20]:  # Show first 20
                model_id = model.get("id", "unknown")
                name = model.get("name", "unknown")
                context = model.get("context_length", 0)
                print(f"✅ {model_id}")
                print(f"   Name: {name}")
                print(f"   Context: {context:,} tokens")
                print()
            
            if len(free_models) > 20:
                print(f"... and {len(free_models) - 20} more free models\n")
            
            # Also show some popular paid models
            print(f"\n{'='*80}")
            print(f"POPULAR PAID MODELS (require credits)")
            print(f"{'='*80}\n")
            
            popular = ["anthropic/claude-3.5-sonnet", "openai/gpt-4-turbo", "google/gemini-pro-1.5"]
            for model in models:
                if model.get("id") in popular:
                    model_id = model.get("id")
                    name = model.get("name")
                    pricing = model.get("pricing", {})
                    prompt_price = pricing.get("prompt", "0")
                    print(f"💰 {model_id}")
                    print(f"   Name: {name}")
                    print(f"   Price: ${float(prompt_price)*1000000:.2f} per 1M tokens")
                    print()
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(list_models())
