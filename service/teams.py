from autogen_agentchat.teams import GroupChat, GroupChatManager # 尝试从 .teams 导入
from agents import (
    user_proxy,
    chinese_planner, chinese_writer, chinese_scorer, chinese_reviser,
    english_planner, english_writer, english_scorer, english_reviser,
    llm_config # Import llm_config for the manager
)

# --- 1. 中文范文写作团队 (Chinese Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
chinese_writing_agents = [user_proxy, chinese_planner, chinese_writer, chinese_scorer, chinese_reviser]
chinese_writing_groupchat = GroupChat(
    agents=chinese_writing_agents,
    messages=[],
    max_round=15, # 限制最大对话轮数
    speaker_selection_method="auto", # 自动选择下一个发言者。AutoGen v0.2+ 改进了 'auto' 模式
    # 对于更精确的控制，可以考虑自定义 speaker_selection_method 函数
    # allow_repeat_speaker=False, # 可以设置为 False 避免同一 Agent 连续发言（除非必要）
)

chinese_writing_manager = GroupChatManager(
    groupchat=chinese_writing_groupchat,
    name="ChineseWritingManager",
    llm_config=llm_config,
    # system_message 可以指导 Manager 如何协调流程
    system_message="""协调中文范文写作流程。
    1.  确保 Planner 根据用户要求创建大纲。
    2.  确保 Writer 根据大纲撰写草稿。
    3.  确保 Scorer 评估草稿并提供反馈。
    4.  确保 Reviser 根据反馈修改草稿。
    5.  将最终的范文呈现给用户。按顺序协调智能体完成任务。"""
)


# --- 2. 英文范文写作团队 (English Sample Essay Writing Team) ---
# 流程: User -> Planner -> Writer -> Scorer -> Reviser -> User
english_writing_agents = [user_proxy, english_planner, english_writer, english_scorer, english_reviser]
english_writing_groupchat = GroupChat(
    agents=english_writing_agents,
    messages=[],
    max_round=15,
    speaker_selection_method="auto",
)

english_writing_manager = GroupChatManager(
    groupchat=english_writing_groupchat,
    name="EnglishWritingManager",
    llm_config=llm_config,
    system_message="""Coordinate the English sample essay writing process.
    1. Ensure the Planner creates an outline based on user requirements.
    2. Ensure the Writer drafts the essay based on the outline.
    3. Ensure the Scorer evaluates the draft and provides feedback.
    4. Ensure the Reviser revises the draft based on the feedback.
    5. Present the final sample essay to the user. Coordinate the agents sequentially."""
)


# --- 3. 中文作文修改团队 (Chinese Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
chinese_revision_agents = [user_proxy, chinese_scorer, chinese_planner, chinese_reviser]
chinese_revision_groupchat = GroupChat(
    agents=chinese_revision_agents,
    messages=[],
    max_round=12,
    speaker_selection_method="auto", # 'auto' 应该能处理 User -> Scorer -> Planner -> Reviser 的流程
)

chinese_revision_manager = GroupChatManager(
    groupchat=chinese_revision_groupchat,
    name="ChineseRevisionManager",
    llm_config=llm_config,
    system_message="""协调中文作文修改流程。
    1.  用户提供需要修改的作文。
    2.  确保 Scorer 首先评估作文并给出评分和意见。
    3.  确保 Planner 根据 Scorer 的意见制定修改计划。
    4.  确保 Reviser 根据计划执行修改。
    5.  将最终修改后的作文呈现给用户。按顺序协调智能体完成任务。"""
)


# --- 4. 英文作文修改团队 (English Essay Revision Team) ---
# 流程: User -> Scorer -> Planner -> Reviser -> User
english_revision_agents = [user_proxy, english_scorer, english_planner, english_reviser]
english_revision_groupchat = GroupChat(
    agents=english_revision_agents,
    messages=[],
    max_round=12,
    speaker_selection_method="auto",
)

english_revision_manager = GroupChatManager(
    groupchat=english_revision_groupchat,
    name="EnglishRevisionManager",
    llm_config=llm_config,
    system_message="""Coordinate the English essay revision process.
    1. The user provides the essay for revision.
    2. Ensure the Scorer first evaluates the essay and provides a score and feedback.
    3. Ensure the Planner creates a revision plan based on the Scorer's feedback.
    4. Ensure the Reviser implements the revision plan.
    5. Present the final revised essay to the user. Coordinate the agents sequentially."""
)

# Example usage (to be placed in app.py or a similar entry point):
# from teams import chinese_writing_manager, user_proxy
#
# user_proxy.initiate_chat(
#     chinese_writing_manager,
#     message="请以“科技进步对现代生活的影响”为主题，写一篇800字左右的中文议论文范文。TERMINATE"
# )
#
# from teams import english_revision_manager, user_proxy
#
# user_essay_to_revise = """
# Technology is change the world very fast. Many people think it good, some think it bad.
# For example, phone make communication easy. But people look phone too much.
# Also car help travel but make pollution. We need find balance.
# """
#
# user_proxy.initiate_chat(
#     english_revision_manager,
#     message=f"Please revise the following English essay:\n\n{user_essay_to_revise}\n\nTERMINATE"
# )
