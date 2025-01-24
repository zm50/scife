import streamlit as st
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models import ChatTongyi
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig

from utils import chat_completion, is_token_expired, extract_files

# st.set_page_config(page_title="论文问答", page_icon="🤖")
st.title('🤖论文问答')

def show_chat(msgs):
    avatars = {"human": "user", "ai": "assistant"}
    for idx, msg in enumerate(msgs):
        with st.chat_message(avatars[msg['type']]):
            # Render intermediate steps if any were saved
            # for step in st.session_state.steps.get(str(idx), []):
            #     if step[0].tool == "_Exception":
            #         continue
            #     with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
            #         st.write(step[0].log)
            #         st.write(step[1])
            st.write(msg['content'])


def reset_chat_history(msgs):
    """重置聊天历史"""
    msgs.clear()
    if 'steps' in st.session_state:
        st.session_state.steps = {}
    # 清除文档相关的缓存
    if 'current_doc' in st.session_state:
        del st.session_state.current_doc


def main():
    if prompt := st.chat_input('ack'):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write('功能正在实现中...')
    # msgs = []

    # # 初始化 selected_doc_index
    # if 'selected_doc_index' not in st.session_state:
    #     st.session_state.selected_doc_index = 0
    
    # # 通过下拉框选择文档
    # document_names = [file['file_name'] for file in st.session_state['files']]
    # selected_doc_name = st.selectbox(
    #     "选择文档", 
    #     document_names,
    #     index=st.session_state.selected_doc_index,  # 使用保存的索引
    #     on_change=lambda: reset_chat_history(msgs),
    #     key='doc_selector'  # 添加唯一的key
    # )
    
    # # 更新选中的文档索引
    # st.session_state.selected_doc_index = document_names.index(selected_doc_name)
    
    # # 检查是否需要重新加载文档
    # current_doc = st.session_state.get('current_doc', {})
    # if current_doc.get('name') != selected_doc_name:
    #     # 只在文档改变时重新加载
    #     st.session_state.current_doc['name'] = selected_doc_name

    #     show_chat(msgs)
    #     if prompt := st.chat_input('ack'):
    #         st.error('!!!!!!!!!!!!!!!')
    #         st.chat_message("user").write(prompt)
    #         # print('xxxxxxxxxx')

    #         # chat_completion(prompt)


# init
if 'files' not in st.session_state:
    st.session_state.files = []

if 'current_doc' not in st.session_state:
    st.session_state.current_doc = {}

if (not st.session_state['token']) or is_token_expired(st.session_state['token']):
    st.error('还没登录哦')
elif not st.session_state.files:
    st.write('### 还没上传文档哦')
else:
    main()
