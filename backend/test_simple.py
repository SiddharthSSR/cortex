#!/usr/bin/env python3
"""Simple test of MLX-LM."""

from mlx_lm import load, generate

print("Loading model...")
model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

print("Generating response...")
response = generate(
    model,
    tokenizer,
    prompt="Say: Hello world!",
    max_tokens=20,
    verbose=True
)

print("\nResponse:", response)
