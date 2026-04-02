# 🚀 Updating Assistant AI to the Latest Version

This guide provides the coordinates for syncing your local **Assistant AI** environment with your active deployment targets (Hugging Face Spaces and Render).

## 🛰️ Syncing Changes

To push the latest updates from your computer to the cloud, run the following commands in your terminal (inside the project directory):

### 1. Synchronize with GitHub
```pwsh
git add .
git commit -m "feat: System Recovery + SQL/Excel/Video Support + Expanded Offline Knowledge"
git push origin deployment-clean --force
```

### 2. Synchronize with Hugging Face
> [!NOTE]
> Hugging Face will automatically rebuild your Space once the push is completed.

```pwsh
git push huggingface deployment-clean --force
```

## 🛠️ Performance Tuning
- **Brevity Protocol**: If the AI begins responding too verbously, check the `assistant_agent/agent.py` system-prompt and ensure `ALWAYS PROVIDE DIRECT, CONCISE, AND OBJECTIVE ANSWERS BY DEFAULT` is strictly enforced.
- **Tokens & TPS**: Performance metrics are logged to the console and database for every query. Monitor these to ensure your API keys (Groq/OpenRouter) are providing the expected speed.

## 📦 Adding New Models
To add more models (e.g., from OpenRouter), update the `call_openrouter` function in `main.py` with the desired model string (e.g., `anthropic/claude-3-5-sonnet:beta`).

---
**Build Status**: `Grounded Retrieval Optimized | Multimodal Ready`
