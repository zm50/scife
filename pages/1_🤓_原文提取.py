import json

import streamlit as st

from utils import is_token_expired, text_extraction, text_extraction_format, print_items

st.title('🤓原文提取')

def main():
    tabs = None
    fns = [item['file_name'] for item in st.session_state['files']]
    if len(fns) > 0:
        tabs = st.tabs(fns)

    for index, item in enumerate(st.session_state['files']):
        with tabs[index]:
            st.write('## ' + item['file_name'] + '\n')

            with st.spinner('解析文档中 ...'):
                items = text_extraction_format(item['id'])
                if not items:
                    st.write('### 大模型貌似开小差了～重新试试吧！\n')
                else:
                    print_items(items)
            # content = get_content_by_uid(item['uid'], 'file_extraction')
            # if content is not None:
            #     print_contents(json.loads(content))
            # else:
            #     with st.spinner('解析文档中 ...'):
                    # result, content = text_extraction(item['file_path'])
            #         if not result:
            #             st.write('### 大模型貌似开小差了～重新试试吧！\n')
            #         else:
            #             print_contents(content)
            #             # 保存到数据库
            #             save_content_to_database(uid=st.session_state['files'][index]['uid'],
            #                                      file_path=st.session_state['files'][index]['file_path'],
            #                                      content=json.dumps(content),
            #                                      content_type='file_extraction')


if "files" not in st.session_state:
    st.session_state['files'] = []

if (not st.session_state['token']) or is_token_expired(st.session_state['token']):
    st.error('还没登录哦')
else:
    main()
