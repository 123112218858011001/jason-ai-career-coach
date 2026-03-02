import streamlit as st
import dashscope
from dashscope import Generation
import datetime
import os

# ⚠️ 重要：填入你的 API Key
# 最佳实践：实际项目中建议放在环境变量里，这里为了学习方便直接填写
# 从环境变量读取 Secret (云端自动注入)，如果没有则尝试使用本地备用 Key (仅本地调试用)
api_key = os.getenv("DASHSCOPE_API_KEY")

if api_key:
    dashscope.api_key = api_key
else:
    # 如果云端没读到，说明你在本地运行，可以临时填在这里测试，但上传 GitHub 前最好注释掉
    dashscope.api_key = "你的本地备用Key_可选"

#dashscope.api_key = "API_KEY" 

# --- 页面配置 ---
st.set_page_config(
    page_title="Jason 的 AI 求职助手",
    page_icon="🤖",
    layout="centered"
)

# --- 标题和介绍 ---
st.title("🤖 Jason 的 AI 求职助手")
st.markdown("""
你好！我是你的专属职业规划导师。
我拥有**记忆功能**，记得我们聊过的所有内容。
聊完后，点击侧边栏的按钮，即可**下载完整的咨询报告 (PDF/MD)**！
""")

# --- 初始化会话状态 (记忆) ---
# Streamlit 每次交互都会重新运行脚本，所以需要用 session_state 来保存记忆
if "messages" not in st.session_state:
    # 初始化系统人设
    st.session_state.messages = [
        {"role": "system", "content": "你是一位专业的职业规划导师，擅长鼓励和指导求职者。用户叫 Jason，45 岁，资深活动策划。"}
    ]

# --- 显示历史聊天记录 ---
# 跳过第一条 system 消息，只显示用户和助手的对话
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 处理用户输入 ---
if prompt := st.chat_input("你想问什么？(例如：我的转型方向是什么？)"):
    # 1. 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. 添加到历史记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. 调用 AI 获取回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 正在思考中...")
        
        try:
            response = Generation.call(
                model='qwen-turbo',
                messages=st.session_state.messages
            )
            
            if response.status_code == 200:
                ai_reply = response.output.text
                message_placeholder.markdown(ai_reply)
                
                # 4. 添加 AI 回复到历史记录
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            else:
                message_placeholder.error(f"出错了：{response.message}")
                
        except Exception as e:
            message_placeholder.error(f"发生异常：{e}")

# --- 侧边栏：下载报告 ---
st.sidebar.header("📂 操作面板")
st.sidebar.markdown("聊天结束后，点击以下按钮保存记录。")

if st.sidebar.button("💾 生成并下载报告 (.md)"):
    if len(st.session_state.messages) <= 1:
        st.sidebar.warning("还没有对话内容哦！")
    else:
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Jason_Chat_{timestamp}.md"
        
        # 写入文件
        content = "# 🤖 Jason 的 AI 求职咨询报告\n\n"
        content += f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
        
        for msg in st.session_state.messages:
            if msg['role'] == 'system': continue
            role_name = "👤 **Jason**" if msg['role'] == 'user' else "🤖 **AI 导师**"
            content += f"### {role_name}:\n\n{msg['content']}\n\n---\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        st.sidebar.success(f"报告已生成：{filename}")
        
        # 提供下载按钮
        with open(filename, 'r', encoding='utf-8') as f:
            st.sidebar.download_button(
                label="📥 点击下载报告文件",
                data=f.read(),
                file_name=filename,
                mime="text/markdown"
            )
        
        st.sidebar.info("💡 提示：下载 .md 文件后，可用 VS Code 打开并右键导出为 PDF。")