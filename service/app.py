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
    from agents import user_proxy
    from teams import (
        chinese_writing_team,
        english_writing_team,
        chinese_revision_team,
        english_revision_team
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

# --- 启动事件：打印已注册路由 ---
@app.on_event("startup")
async def startup_event():
    logger.info("--- Registered Routes ---")
    for route in app.routes:
        # 检查路由是否是 APIRoute 以获取方法信息
        if hasattr(route, "methods"):
            logger.info(f"Path: {route.path}, Methods: {route.methods}")
        else:
            # 对于其他类型的路由（如 WebSocketRoute, Mount），只打印路径
            logger.info(f"Path: {route.path}, Type: {type(route).__name__}")
    logger.info("-------------------------")

# --- 请求模型 ---
class WriteRequest(BaseModel):
    topic: str
    requirements: str | None = None # 提供默认值

class RevisionRequest(BaseModel):
    essay_content: str

# --- 流式响应生成器 ---

async def run_autogen_chat_stream(
    manager: Any, # Autogen SelectorGroupChat 实例
    initial_message: str,
    request: Request # 用于检查客户端是否断开连接
) -> AsyncGenerator[str, None]:
    """
    运行 Autogen 对话，并在完成后流式传输对话历史记录和最终结果。
    使用异步方式调用 manager.run()，因为 SelectorGroupChat 的 run() 方法是异步的。
    """
    queue = asyncio.Queue()
    is_task_done = asyncio.Event()

    async def chat_task():
        try:
            await queue.put(json.dumps({"status": "任务开始", "message": initial_message}))
            logger.info("Autogen 任务开始...")

            # --- 直接异步调用 manager.run()，因为它是 coroutine ---
            logger.info("开始执行 manager.run...")
            # 使用 await 调用异步方法 run()
            # 根据文档，run() 返回 TaskResult 对象，其中包含 messages 列表
            task_result = await manager.run(task=initial_message)
            logger.info("manager.run 执行完毕。")

            chat_history = []
            final_essay = None

            # 从 TaskResult 中提取消息历史记录
            if hasattr(task_result, 'messages') and isinstance(task_result.messages, list):
                logger.info(f"从 TaskResult 中获取到 {len(task_result.messages)} 条聊天记录。")
                processed_history = []
                for i, msg in enumerate(task_result.messages):
                    # 尝试获取发送者名称，兼容不同 Autogen 版本或配置
                    sender_name = getattr(msg, 'source', 'Unknown')
                    if sender_name == 'Unknown' and hasattr(msg, 'metadata') and 'name' in msg.metadata:
                        sender_name = msg.metadata['name']

                    content = getattr(msg, 'content', '')
                    if not isinstance(content, str) and hasattr(content, 'to_text'):
                        content = content.to_text()  # 转换为文本，如果是复杂对象

                    role = getattr(msg, 'type', 'assistant')  # 默认为 assistant

                    # 过滤掉可能存在的空消息或不必要的消息
                    if not content:
                        logger.debug(f"跳过第 {i} 条空消息。")
                        continue

                    msg_data = {
                        "sender": sender_name,
                        "role": role,
                        "content": content,
                        # 可以添加时间戳或其他元数据（如果可用）
                    }
                    # 记录被处理的消息
                    logger.debug(f"处理历史消息 {i}: Sender={sender_name}, Role={role}, Content Snippet='{str(content)[:50]}...'")
                    processed_history.append(msg_data)
                chat_history = processed_history
            else:
                logger.warning("无法在 TaskResult 中找到 'messages' 列表，无法获取聊天历史。")
                # 备选方案：尝试直接从 manager 获取 messages，如果 API 允许
                if hasattr(manager, 'messages') and isinstance(manager.messages, list):
                    logger.info("尝试直接从 manager 获取 messages...")
                    processed_history = []
                    for i, msg in enumerate(manager.messages):
                        sender_name = msg.get('name', 'Unknown')
                        content = msg.get('content', '')
                        role = msg.get('role', 'assistant')

                        if not content:
                            logger.debug(f"跳过第 {i} 条空消息。")
                            continue

                        msg_data = {
                            "sender": sender_name,
                            "role": role,
                            "content": content,
                        }
                        logger.debug(f"处理历史消息 {i}: Sender={sender_name}, Role={role}, Content Snippet='{str(content)[:50]}...'")
                        processed_history.append(msg_data)
                    chat_history = processed_history
                    logger.info(f"从 manager 中获取到 {len(chat_history)} 条聊天记录。")
                else:
                    logger.warning("也无法直接从 manager 获取 messages。")

            # 从历史记录中提取最终结果 (假设 Reviser 是最后输出者)
            if chat_history:
                reviser_name = "Reviser"  # 确认 Reviser 在 teams.py 中的名字
                logger.info(f"尝试从历史记录中查找 '{reviser_name}' 的最终输出...")
                found_reviser_output = False
                for msg in reversed(chat_history):
                    # 确保消息内容是字符串且不为空
                    if msg["sender"] == reviser_name and isinstance(msg["content"], str) and msg["content"].strip():
                        final_essay = msg["content"]
                        logger.info(f"找到 Reviser 的最终输出 (前50字符): {final_essay[:50]}...")
                        found_reviser_output = True
                        break
                if not found_reviser_output:
                    logger.warning(f"未在历史记录中找到 '{reviser_name}' 的有效输出。尝试使用最后一条消息。")
                    # 回退：使用最后一条非空字符串消息作为结果
                    for msg in reversed(chat_history):
                        if isinstance(msg["content"], str) and msg["content"].strip():
                            final_essay = msg["content"]
                            logger.info(f"使用最后一条有效消息作为最终输出 (Sender: {msg['sender']}, 前50字符): {final_essay[:50]}...")
                            break
                    if not final_essay:
                        logger.error("聊天历史记录中没有找到任何有效的文本输出作为最终结果。")

            logger.info(f"聊天执行完成。获取到 {len(chat_history)} 条历史记录。")

            # --- 流式传输捕获的历史记录 ---
            logger.info("开始流式传输聊天历史记录...")
            for i, msg_data in enumerate(chat_history):
                if await request.is_disconnected():
                    logger.warning("客户端在流式传输历史记录时断开连接。")
                    raise asyncio.CancelledError("Client disconnected during history streaming")
                logger.debug(f"流式传输历史消息 {i}: {msg_data}")
                await queue.put(json.dumps({"status": "步骤", "data": msg_data}))
            logger.info("聊天历史记录流式传输完毕。")

            # --- 发送最终完成信号和结果 ---
            logger.info(f"发送任务完成信号。最终结果是否为空: {final_essay is None}")
            await queue.put(json.dumps({"status": "任务完成", "result": final_essay}))

        except asyncio.CancelledError:
            logger.warning("Chat task cancelled, likely due to client disconnect.")
            await queue.put(json.dumps({"status": "错误", "error": "任务被取消 (客户端断开连接)"}))
        except Exception as e:
            logger.error(f"Autogen 任务执行出错: {e}", exc_info=True)
            await queue.put(json.dumps({"status": "错误", "error": str(e)}))
        finally:
            # --- 关闭模型客户端 ---
            logger.info("尝试关闭相关代理的模型客户端...")
            try:
                # 获取代理列表（兼容不同属性名）
                agents_list = getattr(manager, 'agents', []) or getattr(manager, '_agents', []) or []
                if not agents_list and hasattr(manager, 'groupchat') and hasattr(manager.groupchat, 'agents'):
                    agents_list = manager.groupchat.agents  # 另一种可能的结构

                closed_clients = set()  # 避免重复关闭同一个 client
                for agent in agents_list:
                    if hasattr(agent, 'llm_config') and isinstance(agent.llm_config, dict):
                        model_client = agent.llm_config.get('model_client')
                        # 检查 model_client 是否存在，是否可关闭，并且尚未关闭
                        if model_client and hasattr(model_client, 'close') and model_client not in closed_clients:
                            try:
                                # 假设 close 是异步方法
                                if asyncio.iscoroutinefunction(model_client.close):
                                    await model_client.close()
                                else:
                                    # 如果是同步方法，在 executor 中运行以防阻塞
                                    loop = asyncio.get_running_loop()
                                    await loop.run_in_executor(None, model_client.close)

                                logger.info(f"已关闭代理 {getattr(agent, 'name', 'Unknown')} 的模型客户端。")
                                closed_clients.add(model_client)
                            except Exception as close_agent_err:
                                logger.error(f"关闭代理 {getattr(agent, 'name', 'Unknown')} 的模型客户端时出错: {close_agent_err}", exc_info=True)

            except Exception as close_err:
                logger.error(f"关闭模型客户端过程中发生错误: {close_err}", exc_info=True)
            finally:
                await queue.put(None)  # 发送 None 作为结束信号
                is_task_done.set()
                logger.info("chat_task 完成。")

    # --- 启动后台聊天任务 ---
    task = asyncio.create_task(chat_task())

    # --- 从队列读取并发送 SSE 事件 ---
    while True:
        if await request.is_disconnected():
            logger.warning("客户端断开连接，停止 SSE 生成器并取消任务...")
            if not task.done():
                task.cancel()
            break

        try:
            item = await asyncio.wait_for(queue.get(), timeout=1.0)
            if item is None:
                logger.info("收到结束信号，停止 SSE 生成器。")
                break
            yield f"data: {item}\n\n"
            queue.task_done()
        except asyncio.TimeoutError:
            continue # 继续检查连接状态
        except asyncio.CancelledError:
            logger.info("SSE 生成器被取消。")
            if not task.done(): # 确保后台任务也被取消
                task.cancel()
            break
        except Exception as e:
            logger.error(f"SSE 生成循环中发生错误: {e}", exc_info=True)
            if not task.done():
                task.cancel()
            break # 出现意外错误时也停止

    # --- 确保后台任务结束 ---
    try:
        await asyncio.wait_for(is_task_done.wait(), timeout=10.0) # 等待任务完成信号
        logger.info("后台 chat_task 已确认完成。")
    except asyncio.TimeoutError:
        logger.warning("等待 chat_task 完成超时。")
    except Exception as gather_err:
         logger.error(f"等待 chat_task 完成时出错: {gather_err}", exc_info=True)

    # 再次检查任务状态并记录
    if task.done():
        if task.cancelled():
            logger.info("后台任务最终状态：已取消。")
        elif task.exception():
            logger.error(f"后台任务最终状态：异常结束 - {task.exception()}")
        else:
            logger.info("后台任务最终状态：正常完成。")
    else:
        logger.warning("后台任务在 SSE 生成器结束后仍未完成。")


# --- API 端点 ---

@app.post("/write/chinese", summary="中文范文写作 (流式)")
async def api_run_chinese_writing_task(payload: WriteRequest, request: Request):
    topic = payload.topic
    requirements = payload.requirements or "800字左右的议论文" # 使用默认值
    logger.info(f"收到中文写作请求: 主题='{topic}', 要求='{requirements}'")
    message = f"请以“{topic}”为主题，写一篇{requirements}的中文范文。请严格按照 Planner -> Writer -> Scorer -> Reviser 的流程进行协作。最后由 Reviser 输出最终作文。"

    return EventSourceResponse(
        run_autogen_chat_stream(chinese_writing_team, message, request),
        media_type="text/event-stream"
    )

@app.post("/write/english", summary="英文范文写作 (流式)")
async def api_run_english_writing_task(payload: WriteRequest, request: Request):
    topic = payload.topic
    requirements = payload.requirements or "around 500 words, argumentative essay"
    logger.info(f"收到英文写作请求: Topic='{topic}', Requirements='{requirements}'")
    message = f"Please write an English sample essay on the topic '{topic}'. Requirements: {requirements}. Strictly follow the flow: Planner -> Writer -> Scorer -> Reviser. The Reviser should output the final essay."

    return EventSourceResponse(
        run_autogen_chat_stream(english_writing_team, message, request),
        media_type="text/event-stream"
    )

@app.post("/revise/chinese", summary="中文作文修改 (流式)")
async def api_run_chinese_revision_task(payload: RevisionRequest, request: Request):
    essay_content = payload.essay_content
    if not essay_content:
        raise HTTPException(status_code=400, detail="Essay content cannot be empty.")
    logger.info(f"收到中文修改请求 (前50字符): {essay_content[:50]}...")
    message = f"请修改以下中文作文，请严格按照 Scorer -> Planner -> Reviser 的流程进行协作。最后由 Reviser 输出修改后的作文：\n\n{essay_content}\n\n"

    return EventSourceResponse(
        run_autogen_chat_stream(chinese_revision_team, message, request),
        media_type="text/event-stream"
    )

@app.post("/revise/english", summary="英文作文修改 (流式)")
async def api_run_english_revision_task(payload: RevisionRequest, request: Request):
    essay_content = payload.essay_content
    if not essay_content:
        raise HTTPException(status_code=400, detail="Essay content cannot be empty.")
    logger.info(f"收到英文修改请求 (前50字符): {essay_content[:50]}...")
    message = f"Please revise the following English essay. Strictly follow the flow: Scorer -> Planner -> Reviser. The Reviser should output the final revised essay:\n\n{essay_content}\n\n"

    return EventSourceResponse(
        run_autogen_chat_stream(english_revision_team, message, request),
        media_type="text/event-stream"
    )

# --- 用于本地测试的启动命令 (在 service 目录下运行) ---
# uvicorn app:app --reload --port 8001
#
# 注意: --reload 标志用于开发，它会在代码更改时自动重启服务器。
# 在生产环境中，通常不使用 --reload。
