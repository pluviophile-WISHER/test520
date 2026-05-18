import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 
import numpy as np
import random 
 
# 登录校验
if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()
 
st.title("📊 基本统计分析")
 
# 生成随机数据
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 1000 
    
    # 基本人口学特征
    ages = np.random.normal(60, 15, n).astype(int)
    ages = np.clip(ages, 18, 90)
    genders = np.random.choice(['男', '女'], n, p=[0.6, 0.4])
    
    # 肿瘤特征 
    tumor_locations = np.random.choice(['肺', '胃', '结肠', '肝', '乳腺'], n)
    tnm_stages = np.random.choice(['I', 'II', 'III', 'IV'], n, p=[0.2, 0.3, 0.3, 0.2])
    labels = np.random.binomial(1, 0.7, n)
    
    # 实验室指标
    cea = np.round(np.random.exponential(5, n) * (1 + labels * np.random.normal(2, 0.5, n)), 1)
    ca199 = np.round(np.random.exponential(10, n) * (1 + labels * np.random.normal(1.5, 0.3, n)), 1)
    
    df = pd.DataFrame({
        'age': ages,
        'gender': genders,
        'tumor_location': tumor_locations,
        'tnm_stage': tnm_stages,
        'label': labels,
        'cea': cea,
        'ca199': ca199 
    })
    
    return df
 
df = generate_data()
 
# 顶部 KPI 指标 
col1, col2, col3, col4 = st.columns(4)
col1.metric("总病例数", f"{len(df):,}")
col2.metric("阳性病例", f"{df['label'].sum():,}",
            f"{df['label'].mean()*100:.1f}%")
col3.metric("平均年龄", f"{df['age'].mean():.1f} 岁")
col4.metric("男性占比", f"{(df['gender']=='男').mean()*100:.1f}%")
 
st.divider()
 
# 筛选条件
with st.sidebar:
    st.header("🔍 筛选条件")
    age_range = st.slider("年龄范围", 18, 90, (40, 75))
    gender_filter = st.multiselect("性别", df["gender"].unique(),
                                    default=list(df["gender"].unique()))
    stage_filter = st.multiselect("TNM 分期", df["tnm_stage"].unique(),
                                   default=list(df["tnm_stage"].unique()))
 
df_f = df[
    (df["age"].between(*age_range)) &
    (df["gender"].isin(gender_filter)) &
    (df["tnm_stage"].isin(stage_filter))
]
 
# Tab 切换 
tab1, tab2, tab3 = st.tabs(["人口学特征", "肿瘤特征", "实验室指标"])
 
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df_f, x="age", nbins=30,
                            color="gender", barmode="overlay",
                            title="年龄分布")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(df_f, names="gender", title="性别比例", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
 
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        stage_cnt = df_f["tnm_stage"].value_counts().reset_index()
        fig = px.bar(stage_cnt, x="tnm_stage", y="count",
                      title="TNM 分期分布", color="tnm_stage")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.sunburst(df_f, path=["tumor_location", "tnm_stage"],
                            title="肿瘤位置 × 分期")
        st.plotly_chart(fig, use_container_width=True)
 
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(df_f, x="tnm_stage", y="cea", color="tnm_stage",
                      title="不同分期 CEA 水平")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.box(df_f, x="tnm_stage", y="ca199", color="tnm_stage",
                      title="不同分期 CA19-9 水平")
        st.plotly_chart(fig, use_container_width=True)
 
# 描述性统计表 
st.subheader("📋 描述性统计")
st.dataframe(df_f.describe().round(2), use_container_width=True)