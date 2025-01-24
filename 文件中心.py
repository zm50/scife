import datetime
import hashlib
import os
import uuid

import pandas as pd
import requests
import streamlit as st
from streamlit_extras.row import row
from utils import LoggerManager, \
    get_uid_by_md5, is_token_expired, login, register, \
    get_uuid_by_token, get_user_files, server_domain, get_cookies


# 计算文件 MD5
def calculate_md5(file):
    md5_hash = hashlib.md5()
    # 读取文件内容进行 MD5 计算
    for chunk in iter(lambda: file.read(4096), b""):
        md5_hash.update(chunk)
    return md5_hash.hexdigest()


def upload_file():
    # 自定义 CSS
    css = """
    <style>
        /* 覆盖拖拽区域的提示文本 */
        [data-testid="stFileUploaderDropzone"] div div::before {
            content: "将文件拖拽到这里";
            color: #666;
        }
        [data-testid="stFileUploaderDropzone"] div div span {
            display: none;
        }
        [data-testid="stFileUploaderDropzone"] div div::after {
            content: "文件大小限制：200MB";
            font-size: .8em;
            color: #999;
        }
        [data-testid="stFileUploaderDropzone"] div div small {
            display: none;
        }
        /* 覆盖“浏览文件”按钮的文本 */
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "浏览文件";
            display: block;
            position: absolute;
            font-size: 16px;
        }
        [data-testid="stFileUploaderDropzone"] button {
            width: 100px; /* 设置按钮宽度 */
            height: 40px; /* 设置按钮高度 */
            font-size: 0px; /* 设置按钮字体大小 */
            background-color: #007BFF; /* 设置按钮背景颜色 */
            color: white; /* 设置按钮文字颜色 */
            border: none; /* 去掉按钮边框 */
            border-radius: 5px; /* 设置按钮圆角 */
            cursor: pointer; /* 设置鼠标悬停时的指针样式 */
        }
        [data-testid="stFileUploaderDropzone"] button:hover {
            background-color: #0056b3; /* 设置按钮悬停时的背景颜色 */
        }
    </style>
    """

    # 在 Streamlit 应用中应用自定义 CSS
    st.markdown(css, unsafe_allow_html=True)

    uploaded_file = st.file_uploader('请上传文档', type=['pdf'], help='上传文件')
    if uploaded_file is not None:
        file_name = uploaded_file.name

        for file in st.session_state['files']:
            if file['file_name'] == file_name:
                st.error('文件已存在')
                return

        file_content = uploaded_file.getvalue()

        url = f'{server_domain}/api/v1/file/upload'
        files = {'file': (file_name, file_content)}
        resp = requests.post(url, files=files, cookies=get_cookies())
        if resp.status_code != 200:
            st.error('上传失败')
            return

        # # 计算md5
        # md5_value = calculate_md5(uploaded_file)
        # # 生成随机uid作为新文件名,若重复,则沿用
        # if not check_file_exists(md5_value):
        #     uid = str(uuid.uuid4())
        # else:
        #     uid = get_uid_by_md5(md5_value)
        # # 获取文件名和文件后缀,保存文件
        # original_filename = uploaded_file.name
        # file_extension = os.path.splitext(original_filename)[-1]
        # file_name = os.path.splitext(original_filename)[0]
        # saved_filename = f"{uid}{file_extension}"
        # file_path = os.path.join(save_dir, saved_filename)
        # # 将文件保存到本地
        # if not check_file_exists(file_path):
        #     # 返回文件头,之前计算md5已经到文件末尾
        #     uploaded_file.seek(0)
        #     with open(file_path, "wb") as f:
        #         f.write(uploaded_file.read())
        # # 保存到数据库,这里的filename都是带后缀的,后续还会带用户id
        # # 获取当前时间
        # current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # save_file_to_database(original_filename,
        #                       uid,
        #                       st.session_state['uuid'],
        #                       md5_value,
        #                       file_path,
        #                       current_time)
        st.toast("文档上传成功", icon="👌")

        resp_dict = resp.json()
        data = resp_dict['data']

        # 添加path到session
        st.session_state['files'].append({'id': data['id'],
                                          'file_name': file_name,
                                          'created_at': data['created_at'],
                                          })


def load_files():
    files = get_user_files()
    st.session_state['files'] = []
    for file in files:
        st.session_state['files'].append({'id': file['id'],
                                          'file_name': file['file_name'],
                                          'created_at': file['created_at']
                                          })


def print_file_list():
    file_table = {
        '文件名': [],
        '创建时间': []
    }
    for file in st.session_state['files']:
        file_table['文件名'].append(file['file_name'])
        file_table['创建时间'].append(file['created_at'])
    df = pd.DataFrame(file_table)
    rows = row(1)
    rows.table(df)


def main():
    if 'files' not in st.session_state:
        st.session_state['files'] = []
    upload_file()
    load_files()
    if st.session_state['files']:
        print_file_list()


def user_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input('输入用户名:')
        password = st.text_input('输入密码:', type='password')
    button_rows = row([1, 1, 1, 1], vertical_align="center")
    button_rows.write("")
    if button_rows.button('登录', use_container_width=True):
        token, error = login(username, password)
        if error:
            st.error(error)
        else:
            st.toast('✅登陆成功')
            st.session_state['token'] = token
            st.rerun()
    if button_rows.button('注册', use_container_width=True):
        st.session_state['LoginOrRegister'] = 'register'
        st.rerun()


def user_register():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input('输入用户名:')
        password = st.text_input('输入密码:', type='password')
        re_password = st.text_input('再次输入密码:', type='password')
    bt_rows = row([1, 1, 1, 1], vertical_align="center")
    bt_rows.write("")
    if bt_rows.button('返回登录', use_container_width=True):
        st.session_state['LoginOrRegister'] = 'login'
        st.rerun()
    if bt_rows.button('注册', use_container_width=True):
        if password != re_password:
            st.error('两次密码不一致')
        else:
            error = register(username, password)
            if error:
                st.error(error)
            else:
                st.success('注册成功')
                # st.rerun()


# init
# base_dir = os.path.dirname(os.path.abspath(__file__))
# save_dir = os.path.join(base_dir, "uploads")
# os.makedirs(save_dir, exist_ok=True)  # 创建 uploads 目录（如果不存在）
Logger = LoggerManager().get_logger()
# init database
# init_database('./database.sqlite')


# session data
if 'token' not in st.session_state:
    st.session_state['token'] = ''
if 'LoginOrRegister' not in st.session_state:
    st.session_state['LoginOrRegister'] = 'login'
if 'uid' not in st.session_state:
    st.session_state['uid'] = ''
# TODO
# 输入用户名密码,加载文件列表

st.title('智能科研助手')

if not st.session_state['token']:
    if st.session_state['LoginOrRegister'] == 'login':
        st.markdown('<h2 class="title">🤗 登录</h2>', unsafe_allow_html=True)
        user_login()
    else:
        st.markdown('<h2 class="title">😊 注册</h2>', unsafe_allow_html=True)
        user_register()
else:
    st.session_state['uid'] = get_uuid_by_token(st.session_state['token'])

    # 添加侧边栏 API key 设置
    with st.sidebar:
        st.header("设置")

        # 添加退出登录按钮
        if st.button("退出登录", type="primary"):
            # 清除session状态
            st.session_state['token'] = ''
            st.session_state['uid'] = ''
            st.session_state['files'] = []
            st.toast("已退出登录")
            st.rerun()
    main()
