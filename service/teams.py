from autogen_agentchat.teams import SelectorGroupChat
from agents import (
    user_proxy,
    chinese_planner, chinese_writer, chinese_scorer, chinese_reviser,
    english_planner, english_writer, english_scorer, english_reviser
)

# --- 1. 中文范文写作团队 (Chinese Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
chinese_writing_agents = [user_proxy, chinese_planner, chinese_writer, chinese_scorer, chinese_reviser]
chinese_writing_team = SelectorGroupChat(
    chinese_writing_agents,
    model_client=None,  # 将根据实际情况设置
    termination_condition=None,
    allow_repeated_speaker=True
)


# --- 2. 英文范文写作团队 (English Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
english_writing_agents = [user_proxy, english_planner, english_writer, english_scorer, english_reviser]
english_writing_team = SelectorGroupChat(
    english_writing_agents,
    model_client=None,  # 将根据实际情况设置
    termination_condition=None,
    allow_repeated_speaker=True
)


# --- 3. 中文作文修改团队 (Chinese Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
chinese_revision_agents = [user_proxy, chinese_scorer, chinese_planner, chinese_reviser]
chinese_revision_team = SelectorGroupChat(
    chinese_revision_agents,
    model_client=None,  # 将根据实际情况设置
    termination_condition=None,
    allow_repeated_speaker=True
)


# --- 4. 英文作文修改团队 (English Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
english_revision_agents = [user_proxy, english_scorer, english_planner, english_reviser]
english_revision_team = SelectorGroupChat(
    english_revision_agents,
    model_client=None,  # 将根据实际情况设置
    termination_condition=None,
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
