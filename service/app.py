import sys
import os
import logging
import asyncio
import json
from typing import Dict, Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保 service 目录在 Python 路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 尝试导入 agents 和 teams
try:
    from agents import user_proxy, llm_config # 需要 llm_config
    from teams import (
        chinese_writing_manager,
        english_writing_manager,
        chinese_revision_manager,
        english_revision_manager
    )
    logger.info("成功导入 agents 和 teams 模块。")
except ImportError as e:
    logger.error(f"导入模块失败: {e}", exc_info=True)
    logger.error("请确保 agents.py 和 teams.py 文件存在，并且依赖已安装 (pip install -r requirements.txt)。")
    sys.exit(1)
except ValueError as e: # 通常是 API Key 错误
    logger.error(f"配置错误: {e}")
    logger.error("请确保 .env 文件存在且包含有效的 OPENAI_API_KEY。")
    sys.exit(1)
except Exception as e:
    logger.error(f"初始化过程中发生未知错误: {e}", exc_info=True)
    sys.exit(1)

# --- FastAPI 应用设置 ---
app = FastAPI(
    title="AutoGen Essay Service",
    description="提供基于 Autogen 的范文写作和修改 API",
    version="0.1.0",
)

# --- 请求模型 ---
class WriteRequest(BaseModel):
    topic: str
    requirements: str | None = None # 提供默认值

class RevisionRequest(BaseModel):
    essay_content: str

# --- 流式响应生成器 ---

async def run_autogen_chat_stream(
    manager: Any, # Autogen GroupChatManager 实例
    initial_message: str,
    request: Request # 用于检查客户端是否断开连接
) -> AsyncGenerator[str, None]:
    """
    运行 Autogen 对话并尝试流式传输中间步骤或最终结果。
    注意：这是一个简化的流式实现。真正的逐条消息流式传输需要更复杂的 Autogen 集成。
    """
    queue = asyncio.Queue()
    is_task_done = asyncio.Event()
    final_result = None

    async def chat_task():
        nonlocal final_result
        try:
            # 尝试捕获 initiate_chat 的最终结果
            # 注意：initiate_chat 是同步的，在异步 FastAPI 中直接调用会阻塞事件循环。
            # 需要在线程池中运行它。
            loop = asyncio.get_running_loop()
            await queue.put(json.dumps({"status": "任务开始", "message": initial_message}))

            # --- 在线程池中运行同步的 initiate_chat ---
            def sync_initiate_chat():
                user_proxy.initiate_chat(
                    manager,
                    message=initial_message
                )
                # 尝试获取最后一条消息作为结果 (这可能不准确，取决于 Autogen 流程)
                # 更好的方法是修改 Agent 或 Manager 以显式返回结果
                last_message = manager.groupchat.messages[-1] if manager.groupchat.messages else None
                return last_message

            result = await loop.run_in_executor(None, sync_initiate_chat)
            final_result = result

            # --------------------------------------------

            await queue.put(json.dumps({"status": "任务完成", "result": final_result}))
        except Exception as e:
            logger.error(f"Autogen 任务执行出错: {e}", exc_info=True)
            await queue.put(json.dumps({"status": "错误", "error": str(e)}))
        finally:
            await queue.put(None) # 发送 None 作为结束信号
            is_task_done.set()

    # 启动后台聊天任务
    task = asyncio.create_task(chat_task())

    while True:
        # 检查客户端是否仍然连接
        if await request.is_disconnected():
            logger.warning("客户端断开连接，取消任务...")
            task.cancel() # 尝试取消后台任务
            break

        try:
            # 等待队列中的下一项，设置超时以允许检查断开连接
            item = await asyncio.wait_for(queue.get(), timeout=1.0)
            if item is None: # 收到结束信号
                break
            yield f"data: {item}\n\n" # SSE 格式
            queue.task_done()
        except asyncio.TimeoutError:
            # 超时，继续循环以检查断开连接
            continue
        except asyncio.CancelledError:
            logger.info("SSE 生成器被取消。")
            break

    # 确保后台任务完成或被取消
    if not task.done():
        task.cancel()
    await asyncio.gather(task, return_exceptions=True) # 等待任务结束
    logger.info("流式传输结束。")


# --- API 端点 ---

@app.post("/write/chinese", summary="中文范文写作 (流式)")
async def api_run_chinese_writing_task(payload: WriteRequest, request: Request):
    topic = payload.topic
    requirements = payload.requirements or "800字左右的议论文" # 使用默认值
    logger.info(f"收到中文写作请求: 主题='{topic}', 要求='{requirements}'")
    message = f"请以“{topic}”为主题，写一篇{requirements}的中文范文。请严格按照 Planner -> Writer -> Scorer -> Reviser 的流程进行协作。最后由 Reviser 输出最终作文。TERMINATE"

    return EventSourceResponse(
        run_autogen_chat_stream(chinese_writing_manager, message, request),
        media_type="text/event-stream"
    )

@app.post("/write/english", summary="英文范文写作 (流式)")
async def api_run_english_writing_task(payload: WriteRequest, request: Request):
    topic = payload.topic
    requirements = payload.requirements or "around 500 words, argumentative essay"
    logger.info(f"收到英文写作请求: Topic='{topic}', Requirements='{requirements}'")
    message = f"Please write an English sample essay on the topic '{topic}'. Requirements: {requirements}. Strictly follow the flow: Planner -> Writer -> Scorer -> Reviser. The Reviser should output the final essay. TERMINATE"

    return EventSourceResponse(
        run_autogen_chat_stream(english_writing_manager, message, request),
        media_type="text/event-stream"
    )

@app.post("/revise/chinese", summary="中文作文修改 (流式)")
async def api_run_chinese_revision_task(payload: RevisionRequest, request: Request):
    essay_content = payload.essay_content
    if not essay_content:
        raise HTTPException(status_code=400, detail="Essay content cannot be empty.")
    logger.info(f"收到中文修改请求 (前50字符): {essay_content[:50]}...")
    message = f"请修改以下中文作文，请严格按照 Scorer -> Planner -> Reviser 的流程进行协作。最后由 Reviser 输出修改后的作文：\n\n{essay_content}\n\nTERMINATE"

    return EventSourceResponse(
        run_autogen_chat_stream(chinese_revision_manager, message, request),
        media_type="text/event-stream"
    )

@app.post("/revise/english", summary="英文作文修改 (流式)")
async def api_run_english_revision_task(payload: RevisionRequest, request: Request):
    essay_content = payload.essay_content
    if not essay_content:
        raise HTTPException(status_code=400, detail="Essay content cannot be empty.")
    logger.info(f"收到英文修改请求 (前50字符): {essay_content[:50]}...")
    message = f"Please revise the following English essay. Strictly follow the flow: Scorer -> Planner -> Reviser. The Reviser should output the final revised essay:\n\n{essay_content}\n\nTERMINATE"

    return EventSourceResponse(
        run_autogen_chat_stream(english_revision_manager, message, request),
        media_type="text/event-stream"
    )

# --- 用于本地测试的启动命令 (在 service 目录下运行) ---
# uvicorn app:app --reload --port 8001
#
# 注意: --reload 标志用于开发，它会在代码更改时自动重启服务器。
# 在生产环境中，通常不使用 --reload。
