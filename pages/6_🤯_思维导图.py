import json
import streamlit as st
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
from pyecharts.charts import Tree
from utils import (
    is_token_expired, 
    extract_files, 
    get_content_by_uid, 
    save_content_to_database,
    generate_mindmap_data,
    delete_content_by_uid
)

# # 设置页面布局为宽屏模式
# st.set_page_config(
#     page_title="思维导图",
#     page_icon="",
#     layout="wide"  # 使用宽屏模式
# )

st.title('🤯思维导图')

def create_mindmap(data):
    """创建思维导图"""
    tree = (
        Tree()
        .add(
            
            series_name="",
            data=[data],
            orient="LR",
            initial_tree_depth=3,
            layout="orthogonal",
            pos_left="3%",      # 设置左边距
            # pos_right="15%",    # 设置右边距
            width="65%",        # 控制图表宽度
            height="86%",    # 控制图表高度
            edge_fork_position="10%",  # 让分叉点靠近父节点
            symbol_size=7,      # 节点大小
            label_opts=opts.LabelOpts(
                position="right",
                horizontal_align="left",
                vertical_align="middle",
                font_size=14,
                padding=[0, 0, 0, -20],
            ),
            
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="文献思维导图"),
            tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                pos_left="right",
                feature={
                    "zoom": {"is_show": True},
                    "restore": {"is_show": True},
                }
            )
        )
    )
    return tree


def gen_mindmap(content, document):
    with st.spinner('正在生成思维导图...'):
        mindmap_data = generate_mindmap_data(content['text'])
        save_content_to_database(
            uid=document['uid'],
            file_path=document['file_path'],
            content=json.dumps(mindmap_data),
            content_type='file_mindmap'
        )
        tree = create_mindmap(mindmap_data)
        st_pyecharts(
            tree,
            height="900px",
            width="100%",
            key=f"mindmap_{document['uid']}"
        )

def main():
    if not st.session_state.files:
        st.write('### 还没上传文档哦')
        return
    
    st.write('### 正在快马加鞭实现中...')

    return
    # 操作区域（上方）
    
    selected_doc = st.selectbox(
        "选择文档",
        options=[file['file_name'] for file in st.session_state.files],
        key="selected_doc"
    )
    
    with st.sidebar:
        if st.button('重新生成', type="primary"):
            doc = next((doc for doc in st.session_state.files if doc['file_name'] == selected_doc), None)
            if doc:
                delete_content_by_uid(doc['uid'], 'file_mindmap')
                st.rerun()
    
    # 思维导图展示区域（下方）
    st.write("---")  # 添加分隔线
    document = next((doc for doc in st.session_state.files if doc['file_name'] == selected_doc), None)
    if document:
        existing_mindmap = get_content_by_uid(document['uid'], 'file_mindmap')
        
        if existing_mindmap:
            mindmap_data = json.loads(existing_mindmap)
            tree = create_mindmap(mindmap_data)
            st_pyecharts(
                tree,
                height="850px",
                width="120%",  # 增加宽度到120%
                key=f"mindmap_{document['uid']}"
            )
        else:
            content = extract_files(document['file_path'])
            if content['result'] == 1:
                gen_mindmap(content, document)
            else:
                st.error('文档解析失败')

if (not st.session_state['token']) or is_token_expired(st.session_state['token']):
    st.error('还没登录哦')
else:
    main()