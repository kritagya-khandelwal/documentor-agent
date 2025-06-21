import hashlib
import json
import os
from typing import Type

from langchain_openai import ChatOpenAI
from pydantic import BaseModel


def call_llm(llm_context: str, type: Type[BaseModel] = None, use_cache: bool = True):
    cache_file = "agent_cache.json"

    if use_cache:
        # create a hash key for the prompt and check if it exists in the cache
        hash_key = hashlib.sha256(llm_context.encode()).hexdigest()
        # check in the cache.json file if the hash key exists
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                if hash_key in cache:
                    return cache[hash_key]
            except Exception as e:
                print(f"Warning: Could not read cache file: {e}")
    
    llm = ChatOpenAI(
        model="gemini-2.5-flash-lite-preview-06-17", 
        temperature=0, 
        api_key=os.getenv("GOOGLE_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    if type is not None:
        llm = llm.with_structured_output(type)
    output = llm.invoke(llm_context)
    
    if use_cache:
        # check if cache.json exists and create it if it doesn't
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception:
                cache = {}
        cache[hash_key] = output
        # add the hash key and output to the cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, default=str)
    return output 