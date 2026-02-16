import os
import json
import requests

LLM_MODE = os.environ.get('LLM_MODE', 'stub')


def _hf_generate(prompt: str, model: str, max_tokens: int = 512, params: dict = None) -> dict:
    """Call Hugging Face Inference API for text generation.
    Requires env var `HUGGINGFACE_API_KEY` set to a valid token.
    """
    api_key = os.environ.get('HUGGINGFACE_API_KEY')
    if not api_key:
        return {"text": "[huggingface error] missing HUGGINGFACE_API_KEY", "model": model, "tokens": 0}
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    body = {"inputs": prompt}
    if params:
        body["parameters"] = params
    try:
        r = requests.post(url, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        # HF returns list of generated outputs for text-generation models; adapt as needed
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            text = data[0].get('generated_text') or data[0].get('text') or json.dumps(data[0])
        elif isinstance(data, dict) and 'generated_text' in data:
            text = data.get('generated_text')
        else:
            # fallback: stringify response
            text = json.dumps(data)
        return {"text": text, "model": model, "tokens": max_tokens}
    except Exception as e:
        return {"text": f"[huggingface error] {e}", "model": model, "tokens": 0}


def generate(prompt: str, max_tokens: int = 512, **kwargs) -> dict:
    """
    Modular LLM entrypoint. Supported modes:
      - stub: deterministic local response
      - openai: requires OPENAI_API_KEY env var (optional)
      - huggingface: calls Hugging Face Inference API using HUGGINGFACE_API_KEY
      - bedrock: placeholder for AWS Bedrock
      - local: placeholder for local Llama runtime

    Returns dict: {"text": str, "model": str, "tokens": int}
    """
    mode = LLM_MODE.lower()
    if mode == 'openai':
        try:
            import openai
            resp = openai.Completion.create(engine=kwargs.get('engine', 'text-davinci-003'), prompt=prompt, max_tokens=max_tokens)
            text = resp.choices[0].text
            return {"text": text, "model": getattr(resp, 'model', 'openai'), "tokens": max_tokens}
        except Exception as e:
            return {"text": f"[openai error] {e}", "model": "openai-error", "tokens": 0}
    elif mode == 'huggingface':
        model = os.environ.get('LLM_MODEL', 'google/flan-t5-large')
        params = kwargs.get('params') or {"max_new_tokens": max_tokens}
        return _hf_generate(prompt, model=model, max_tokens=max_tokens, params=params)
    elif mode == 'bedrock':
        return {"text": "[bedrock stub] " + prompt[:512], "model": "bedrock-stub", "tokens": max_tokens}
    elif mode == 'local':
        # try to use llama-cpp-python if available and LLM_MODEL_PATH env provided
        try:
            from llama_cpp import Llama
        except Exception:
            return {"text": "[local-llm error] llama_cpp not installed", "model": "local-error", "tokens": 0}
        model_path = os.environ.get('LLM_MODEL_PATH')
        if not model_path:
            return {"text": "[local-llm error] LLM_MODEL_PATH not set", "model": "local-error", "tokens": 0}
        try:
            llm_client = Llama(model_path=model_path)
            resp = llm_client(prompt=prompt, max_tokens=max_tokens)
            # llama_cpp returns dict with 'choices' list
            text = ''
            if isinstance(resp, dict) and 'choices' in resp and len(resp['choices']) > 0:
                text = resp['choices'][0].get('text', '')
            elif isinstance(resp, str):
                text = resp
            else:
                text = str(resp)
            return {"text": text, "model": f"llama-cpp:{model_path}", "tokens": max_tokens}
        except Exception as e:
            return {"text": f"[local-llm error] {e}", "model": "local-error", "tokens": 0}
    else:
        out = "Generated SAR draft based on provided case and templates.\n\n" + prompt[:2000]
        return {"text": out, "model": "stub-v0", "tokens": len(out)}
