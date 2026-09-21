import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables
load_dotenv()

def get_llm():
    """
    Returns the LLM instance based on environment configuration using CrewAI's native LLM class.
    """
    use_deepseek = os.getenv("USE_DEEPSEEK", "true").lower() == "true"
    use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
    
    if use_deepseek:
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        )
    elif use_local:
        return LLM(
            model=os.getenv("OLLAMA_MODEL", "ollama/llama3.2:latest"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    elif use_gemini:
        return LLM(
            model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash"),
            api_key=os.getenv("GEMINI_API_KEY")
        )
    elif use_groq:
        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        # Strip prefixes so we can route via native openai provider with Groq base_url
        if model_name.startswith("groq/"):
            model_name = model_name[len("groq/"):]
        elif model_name.startswith("openai/"):
            model_name = model_name[len("openai/"):]
            
        return LLM(
            model=f"openai/{model_name}",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
    else:
        return LLM(
            model=os.getenv("OPENAI_MODEL_NAME", "openrouter/auto"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        )