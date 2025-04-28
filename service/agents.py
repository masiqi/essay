from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

# 加载 .env 文件中的环境变量
load_dotenv()

# --- LLM 提供商配置 ---
# 从环境变量中读取 API 密钥和基础 URL
# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "")
# Grok
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "")
# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "")
# Ollama (使用 OpenAI 兼容 API)
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# 检查是否至少有一个 API 密钥可用
if not any([OPENAI_API_KEY, DEEPSEEK_API_KEY, GROK_API_KEY, GEMINI_API_KEY]):
    raise ValueError("没有找到任何有效的 API 密钥。请在 .env 文件中设置 OPENAI_API_KEY, DEEPSEEK_API_KEY, GROK_API_KEY 或 GEMINI_API_KEY。")

# --- 辅助函数：根据提供商和模型名称获取 llm_config ---
def get_llm_config(provider: str, model: str, temperature: float = 0.7, cache_seed: int | None = 42) -> dict:
    """
    为指定的提供商和模型创建 llm_config 字典。
    Args:
        provider: 模型提供商 ('openai', 'deepseek', 'grok', 'gemini', 'ollama')
        model: 模型名称 (例如 'gpt-4', 'deepseek-chat', 'grok-1', 'gemini-1.5-flash', 'llama3')
        temperature: 模型温度，控制输出的创造性
        cache_seed: 用于缓存的种子，设置为 None 禁用缓存
    Returns:
        llm_config 字典，适用于 Autogen 代理
    """
    provider = provider.lower()
    # 使用 OpenAIChatCompletionClient (适用于 OpenAI 及其兼容 API)
    api_key = ""
    base_url = None  # None 表示使用默认 OpenAI 端点
    model_info = None  # 默认情况下不覆盖模型信息
    
    if provider == 'openai':
        api_key = OPENAI_API_KEY
    elif provider == 'deepseek':
        api_key = DEEPSEEK_API_KEY
        base_url = DEEPSEEK_BASE_URL if DEEPSEEK_BASE_URL else None
        # 如果需要，指定模型能力
        model_info = ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="unknown"
        )
    elif provider == 'grok':
        api_key = GROK_API_KEY
        base_url = GROK_BASE_URL if GROK_BASE_URL else None
        model_info = ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="unknown"
        )
    elif provider == 'gemini':
        api_key = GEMINI_API_KEY
        base_url = GEMINI_BASE_URL if GEMINI_BASE_URL else None
        model_info = ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="unknown"
        )
    elif provider == 'ollama':
        api_key = OLLAMA_API_KEY
        base_url = OLLAMA_BASE_URL if OLLAMA_BASE_URL else None
        model_info = ModelInfo(
            vision=False,
            function_calling=False,
            json_output=False,
            structured_output=False,
            family="unknown"
        )
    else:
        raise ValueError(f"不支持的提供商: {provider}")
    
    if not api_key:
        raise ValueError(f"提供商 {provider} 的 API 密钥未找到。请在 .env 文件中设置相应的环境变量。")
    
    model_client = OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url if base_url else None,
        model_info=model_info
    )
    
    # 返回适用于 Autogen 代理的 llm_config 字典
    return {
        "model_client": model_client,
        "cache_seed": cache_seed,
        "temperature": temperature,
    }

# --- 通用智能体 ---

# 用户代理 - 代表用户发起请求和提供输入
# 用户代理不需要 LLM 配置，因为它代表人类用户
user_proxy = UserProxyAgent(
    name="UserProxy",
    description="A human user or coordinator."
)

# --- 中文写作/修改相关智能体 ---

# 中文作文规划师
# 使用 DeepSeek 模型 (假设 DeepSeek 在中文任务上表现良好)
chinese_planner = AssistantAgent(
    name="ChinesePlanner",
    model_client=get_llm_config(provider="deepseek", model="deepseek-chat")["model_client"],
    system_message="""你是一位中文作文写作规划师 (Chinese Essay Planner)。
    你的任务是根据用户提供的主题和要求，制定一个详细的中文作文写作大纲或修改计划。
    你需要考虑文章结构、论点、论据和语言风格。
    将最终的计划清晰地呈现出来，使用 Markdown 格式。不要写实际的作文内容，只负责规划。
    Plan the process step-by-step. If the user asks for revision, create a revision plan. If the user asks for writing, create a writing plan (outline).
    Reply 'TERMINATE' when your task is done.
    """
)

# 中文作文写手
# 使用 OpenAI GPT-4 (假设需要高质量的写作)
chinese_writer = AssistantAgent(
    name="ChineseWriter",
    model_client=get_llm_config(provider="gemini", model="gemini-1.5-flash")["model_client"],
    system_message="""你是一位经验丰富的中文作文写手 (Chinese Essay Writer)。
    你会根据规划师提供的大纲和要求，撰写一篇高质量的中文作文。
    注意语言流畅、逻辑清晰、表达准确。
    确保你的输出是完整的作文内容。
    Reply 'TERMINATE' when your task is done.
    """
)

# 中文作文评分/评估师 (可复用)
# 使用 Gemini (假设 Gemini 适合评估任务)
chinese_scorer = AssistantAgent(
    name="ChineseScorer",
    model_client=get_llm_config(provider="gemini", model="gemini-1.5-flash")["model_client"],
    system_message="""你是一位严格的中文作文评分员 (Chinese Essay Scorer)。
    你的任务是评估给定的中文作文草稿或最终稿。
    你需要从内容相关性、结构逻辑、语言表达、思想深度等多个维度进行评分（例如，满分100分）。
    除了评分，你还需要提供具体的、有建设性的修改意见，指出优点和不足之处。
    请以清晰的 Markdown 格式输出评分和修改意见。
    Example Output:
    ```markdown
    **评分:** 85/100

    **优点:**
    *   论点清晰，紧扣主题。
    *   结构完整，段落过渡自然。

    **不足与修改建议:**
    *   部分语句表达略显啰嗦，建议精简。例如，将“我们必须认识到环境保护的重要性”改为“环境保护至关重要”。
    *   第三段论据稍显不足，建议补充具体实例或数据。
    *   结尾可以更有力，尝试升华主题。
    ```
    Reply 'TERMINATE' when your task is done.
    """
)

# 中文作文修改师
# 使用 Grok (假设 Grok 擅长修改和润色)
chinese_reviser = AssistantAgent(
    name="ChineseReviser",
    model_client=get_llm_config(provider="grok", model="grok-1")["model_client"],
    system_message="""你是一位专业的中文作文修改师 (Chinese Essay Reviser)。
    你会根据评分员的意见和原始作文，对中文作文进行修改和润色。
    你的目标是提升作文的整体质量，修正语法错误、改进表达、增强逻辑性。
    输出修改后的完整作文。
    Reply 'TERMINATE' when your task is done.
    """
)


# --- 英文写作/修改相关智能体 ---

# 英文作文规划师
# 使用 Ollama 上的本地模型 (假设用于测试或资源受限场景)
english_planner = AssistantAgent(
    name="EnglishPlanner",
    model_client=get_llm_config(provider="ollama", model="llama3")["model_client"],
    system_message="""You are an English essay writing planner.
    Your task is to create a detailed outline or revision plan for an English essay based on the user's topic and requirements.
    Consider the essay structure (introduction, body paragraphs with topic sentences, conclusion), arguments, supporting evidence, and writing style (e.g., formal, informal).
    Present the final plan clearly using Markdown. Do not write the actual essay content, only plan.
    Plan the process step-by-step. If the user asks for revision, create a revision plan. If the user asks for writing, create a writing plan (outline).
    Reply 'TERMINATE' when your task is done.
    """
)

# 英文作文写手
# 使用 OpenAI GPT-4 (高质量写作)
english_writer = AssistantAgent(
    name="EnglishWriter",
    model_client=get_llm_config(provider="gemini", model="gemini-1.5-flash")["model_client"],
    system_message="""You are an experienced English essay writer.
    You will write a high-quality English essay based on the outline and requirements provided by the planner.
    Pay attention to grammar, vocabulary, fluency, logical coherence, and accurate expression.
    Ensure your output is the complete essay content.
    Reply 'TERMINATE' when your task is done.
    """
)

# 英文作文评分/评估师 (可复用)
# 使用 Gemini
english_scorer = AssistantAgent(
    name="EnglishScorer",
    model_client=get_llm_config(provider="gemini", model="gemini-1.5-flash")["model_client"],
    system_message="""You are a strict English essay scorer.
    Your task is to evaluate the given English essay draft or final version.
    You need to score it from multiple dimensions such as task achievement, coherence and cohesion, lexical resource, and grammatical range and accuracy (e.g., out of 100 points or using IELTS/TOEFL band descriptors).
    Besides scoring, you must provide specific, constructive feedback, pointing out strengths and weaknesses with examples.
    Output the score and feedback in a clear Markdown format.
    Example Output:
    ```markdown
    **Score:** 7.5/9.0 (IELTS Band)

    **Strengths:**
    *   Addresses all parts of the task.
    *   Good range of vocabulary used appropriately.
    *   Logical paragraphing and clear central topic in each paragraph.

    **Areas for Improvement & Suggestions:**
    *   Some grammatical errors related to articles ('a'/'an'/'the'). E.g., "Importance of **the** education..." should be "Importance of education...".
    *   Could use more varied sentence structures. Try incorporating complex sentences with subordinate clauses.
    *   Cohesion could be improved with more diverse linking words (e.g., 'Furthermore', 'Nevertheless' instead of repeating 'Also').
    ```
    Reply 'TERMINATE' when your task is done.
    """
)

# 英文作文修改师
# 使用 Grok
english_reviser = AssistantAgent(
    name="EnglishReviser",
    model_client=get_llm_config(provider="grok", model="grok-1")["model_client"],
    system_message="""You are a professional English essay reviser.
    You will revise and polish the English essay based on the scorer's feedback and the original essay.
    Your goal is to improve the overall quality of the essay by correcting grammatical errors, enhancing vocabulary and sentence structure, and ensuring logical flow.
    Output the revised complete essay.
    Reply 'TERMINATE' when your task is done.
    """
)
