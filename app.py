# -*- coding: utf-8 -*-
"""
简化版结直肠癌临床预测系统登录界面
使用内存存储用户数据，无需数据库
"""

import streamlit as st 
 
st.set_page_config(
    page_title="结直肠癌临床预测系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# 在内存中存储用户数据
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {
            "password": "admin123",
            "full_name": "管理员",
            "department": "信息科",
            "role": "admin"
        }
    }
 
def login_page():
    st.markdown("<h1 style='text-align:center;'>🏥 结直肠癌临床预测系统</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>"
                "Colorectal Cancer Clinical Prediction System</p>",
                unsafe_allow_html=True)
 
    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
 
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("用户名", key="login_user")
            password = st.text_input("密码", type="password", key="login_pwd")
            if st.button("登录", use_container_width=True, type="primary"):
                if username in st.session_state.users:
                    if st.session_state.users[username]["password"] == password:
                        st.session_state["logged_in"] = True 
                        st.session_state["user_info"] = st.session_state.users[username]
                        st.success(f"欢迎, {st.session_state.users[username]['full_name']}!")
                        st.rerun()
                    else:
                        st.error("密码错误")
                else:
                    st.error("用户名不存在")
 
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            new_user = st.text_input("用户名*", key="reg_user")
            new_pwd = st.text_input("密码*", type="password", key="reg_pwd")
            confirm = st.text_input("确认密码*", type="password", key="reg_confirm")
            full_name = st.text_input("姓名")
            department = st.text_input("科室")
            role = st.selectbox("角色", ["doctor", "researcher", "admin"])
            if st.button("注册", use_container_width=True):
                if new_pwd != confirm:
                    st.error("两次密码不一致")
                elif len(new_pwd) < 6:
                    st.error("密码长度不少于6位")
                elif new_user in st.session_state.users:
                    st.error("用户名已存在")
                else:
                    st.session_state.users[new_user] = {
                        "password": new_pwd,
                        "full_name": full_name,
                        "department": department,
                        "role": role
                    }
                    st.success("注册成功！")
 
# 运行登录页面 
if "logged_in" not in st.session_state:
    login_page()
else:
    st.success(f"您已登录为 {st.session_state.user_info['full_name']}")
    if st.button("退出登录"):
        st.session_state.logged_in = False 
        st.session_state.pop("user_info", None)
        st.rerun()