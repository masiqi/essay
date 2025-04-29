from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from typing import Sequence
from agents import (
    user_proxy,
    chinese_planner, chinese_writer, chinese_scorer, chinese_reviser,
    english_planner, english_writer, english_scorer, english_reviser
)

# 创建模型客户端 (使用 Gemini 兼容端点，需要在环境中设置 GEMINI_API_KEY 或其他兼容 API 密钥)
model_client = OpenAIChatCompletionClient(model="gemini-1.5-flash-8b")

# 设置终止条件 (当消息中包含 "TERMINATE" 时结束)
termination = TextMentionTermination("TERMINATE")

# 自定义选择函数，确保严格按照流程顺序选择下一个发言者
def chinese_writing_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    if not messages:
        return chinese_planner.name  # 如果没有消息，默认从 Planner 开始
    
    last_message = messages[-1]
    last_source = last_message.source
    
    if last_source == user_proxy.name:
        return chinese_planner.name  # 用户发言后，选择 Planner
    elif last_source == chinese_planner.name:
        return chinese_writer.name  # Planner 发言后，选择 Writer
    elif last_source == chinese_writer.name:
        return chinese_scorer.name  # Writer 发言后，选择 Scorer
    elif last_source == chinese_scorer.name:
        return chinese_reviser.name  # Scorer 发言后，选择 Reviser
    elif last_source == chinese_reviser.name:
        return None  # Reviser 发言后，流程结束，交给终止条件处理
    
    return None  # 默认情况下不选择，返回 None 使用模型选择

def chinese_revision_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    if not messages:
        return chinese_scorer.name  # 如果没有消息，默认从 Scorer 开始
    
    last_message = messages[-1]
    last_source = last_message.source
    
    if last_source == user_proxy.name:
        return chinese_scorer.name  # 用户发言后，选择 Scorer
    elif last_source == chinese_scorer.name:
        return chinese_planner.name  # Scorer 发言后，选择 Planner
    elif last_source == chinese_planner.name:
        return chinese_reviser.name  # Planner 发言后，选择 Reviser
    elif last_source == chinese_reviser.name:
        return None  # Reviser 发言后，流程结束，交给终止条件处理
    
    return None  # 默认情况下不选择，返回 None 使用模型选择

# --- 1. 中文范文写作团队 (Chinese Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
# 注意: 使用自定义选择函数确保严格按照流程顺序选择发言者
chinese_writing_agents = [user_proxy, chinese_planner, chinese_writer, chinese_scorer, chinese_reviser]
chinese_writing_team = SelectorGroupChat(
    chinese_writing_agents,
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=False,  # 不允许同一发言者连续发言
    selector_func=chinese_writing_selector
)

# --- 2. 英文范文写作团队 (English Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
# 注意: agent 列表顺序反映了期望的调用流程，确保从 Planner 开始，依次到 Writer、Scorer 和 Reviser
english_writing_agents = [user_proxy, english_planner, english_writer, english_scorer, english_reviser]
english_writing_team = SelectorGroupChat(
    english_writing_agents,
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=True
)

# --- 3. 中文作文修改团队 (Chinese Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
# 注意: 使用自定义选择函数确保严格按照流程顺序选择发言者
chinese_revision_agents = [user_proxy, chinese_scorer, chinese_planner, chinese_reviser]
chinese_revision_team = SelectorGroupChat(
    chinese_revision_agents,
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=False,  # 不允许同一发言者连续发言
    selector_func=chinese_revision_selector
)

# --- 4. 英文作文修改团队 (English Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
# 注意: agent 列表顺序反映了期望的调用流程，确保从 Scorer 开始，依次到 Planner 和 Reviser
english_revision_agents = [user_proxy, english_scorer, english_planner, english_reviser]
english_revision_team = SelectorGroupChat(
    english_revision_agents,
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=True
)

# Example usage (to be placed in app.py or a similar entry point):
# from teams import chinese_writing_team, user_proxy
#
# user_proxy.initiate_chat(
#     chinese_writing_team,
#     message="请以“科技进步对现代生活的影响”为主题，写一篇800字左右的中文议论文范文。TERMINATE"
# )
#
# from teams import english_revision_team, user_proxy
#
# user_essay_to_revise = """
# Technology is change the world very fast. Many people think it good, some think it bad.
# For example, phone make communication easy. But people look phone too much.
# Also car help travel but make pollution. We need find balance.
# """
#
# user_proxy.initiate_chat(
#     english_revision_team,
#     message=f"Please revise the following English essay:\n\n{user_essay_to_revise}\n\nTERMINATE"
# )
