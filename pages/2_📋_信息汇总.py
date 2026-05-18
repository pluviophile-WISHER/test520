import streamlit as st
import pandas as pd 
from io import BytesIO 
import numpy as np
import random 
from datetime import datetime, timedelta 
 
if not st.session_state.get("logged_in"):
    st.warning("请先登录")
    st.stop()
 
st.title("📋 病例信息汇总")
 
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 500
    
    # 基本人口学特征 
    patient_ids = [f"P{str(i).zfill(5)}" for i in range(1000, 1000+n)]
    names = [random.choice(["张", "王", "李", "刘", "陈"]) + random.choice(["伟", "芳", "娜", "秀英", "强"]) for _ in range(n)]
    genders = np.random.choice(['男', '女'], n, p=[0.55, 0.45])
    ages = np.random.normal(60, 15, n).astype(int)
    ages = np.clip(ages, 18, 90)
    
    # 肿瘤特征
    tumor_locations = np.random.choice(['结肠', '直肠', '胃', '食管', '肝'], n, p=[0.4, 0.3, 0.15, 0.1, 0.05])
    tnm_stages = np.random.choice(['I', 'II', 'III', 'IV'], n, p=[0.2, 0.3, 0.3, 0.2])
    
    # 实验室指标 
    cea = np.round(np.random.exponential(5, n) * (1 + (np.array(tnm_stages) == 'IV') * np.random.normal(2, 0.5, n)), 2)
    ca199 = np.round(np.random.exponential(10, n) * (1 + (np.array(tnm_stages) == 'IV') * np.random.normal(1.5, 0.3, n)), 2)
    
    # 风险评分和等级
    risk_scores = np.round(np.random.beta(2, 5, n) + (np.array(tnm_stages) == 'IV') * 0.3, 2)
    risk_scores = np.clip(risk_scores, 0, 1)
    risk_levels = np.where(risk_scores < 0.3, '低危', 
                          np.where(risk_scores < 0.7, '中危', '高危'))
    
    # 随访状态和日期
    follow_up = np.random.choice(['已完成', '待随访', '失访'], n, p=[0.6, 0.3, 0.1])
    visit_dates = [datetime(2023,1,1) + timedelta(days=np.random.randint(0, 365)) for _ in range(n)]
    
    df = pd.DataFrame({
        'patient_id': patient_ids,
        'name': names,
        'gender': genders,
        'age': ages,
        'tumor_location': tumor_locations,
        'tnm_stage': tnm_stages,
        'cea': cea,
        'ca199': ca199,
        'risk_score': risk_scores,
        'risk_level': risk_levels,
        'follow_up': follow_up,
        'visit_date': visit_dates 
    })
    
    return df
 
df = generate_data()
 
# 检索区
with st.expander("🔎 检索条件", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        patient_id = st.text_input("病案号 (模糊匹配)")
        name_kw = st.text_input("姓名 (模糊匹配)")
    with c2:
        date_range = st.date_input("就诊日期范围", value=[])
        stage_sel = st.multiselect("TNM 分期", df["tnm_stage"].unique())
    with c3:
        loc_sel = st.multiselect("肿瘤位置", df["tumor_location"].unique())
        risk_sel = st.selectbox("风险等级", ["全部", "低危", "中危", "高危"])
 
df_view = df.copy()
if patient_id:
    df_view = df_view[df_view["patient_id"].astype(str).str.contains(patient_id)]
if name_kw:
    df_view = df_view[df_view["name"].str.contains(name_kw, na=False)]
if stage_sel:
    df_view = df_view[df_view["tnm_stage"].isin(stage_sel)]
if loc_sel:
    df_view = df_view[df_view["tumor_location"].isin(loc_sel)]
if risk_sel != "全部":
    df_view = df_view[df_view["risk_level"] == risk_sel]
if date_range and len(date_range) == 2:
    df_view = df_view[
        (df_view["visit_date"] >= pd.to_datetime(date_range[0])) & 
        (df_view["visit_date"] <= pd.to_datetime(date_range[1]))
    ]
 
# 顶部统计 
c1, c2, c3 = st.columns(3)
c1.metric("筛选结果", f"{len(df_view)} 条")
c2.metric("高危人数", (df_view["risk_level"] == "高危").sum())
c3.metric("待随访", (df_view["follow_up"] == "待随访").sum())
 
# 数据表
st.subheader("📑 病例列表")
st.dataframe(df_view, use_container_width=True, height=400,
             column_config={
                 "risk_score": st.column_config.ProgressColumn(
                     "风险评分", min_value=0, max_value=1, format="%.2f"
                 ),
                 "cea": st.column_config.NumberColumn("CEA (ng/mL)", format="%.2f"),
                 "ca199": st.column_config.NumberColumn("CA19-9 (U/mL)", format="%.2f"),
             })
 
# 单病例详情
st.divider()
st.subheader("🔍 单病例详情")
selected_id = st.selectbox("选择病例", df_view["patient_id"].tolist())
if selected_id:
    rec = df_view[df_view["patient_id"] == selected_id].iloc[0]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**姓名**: {rec['name']}")
        st.markdown(f"**性别**: {rec['gender']}")
        st.markdown(f"**年龄**: {rec['age']}")
        st.markdown(f"**肿瘤位置**: {rec['tumor_location']}")
        st.markdown(f"**TNM 分期**: {rec['tnm_stage']}")
    with c2:
        st.markdown(f"**CEA**: {rec['cea']:.2f} ng/mL")
        st.markdown(f"**CA19-9**: {rec['ca199']:.2f} U/mL")
        st.markdown(f"**风险评分**: {rec['risk_score']:.2f}")
        st.markdown(f"**风险等级**: {rec['risk_level']}")
        st.markdown(f"**随访状态**: {rec['follow_up']}")
 
# 导出 
st.divider()
st.subheader("⬇️ 导出数据")
c1, c2 = st.columns(2)
 
with c1:
    csv = df_view.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📄 下载 CSV", csv,
                       file_name="crc_cases.csv",
                       mime="text/csv",
                       use_container_width=True)
 
with c2:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_view.to_excel(writer, sheet_name="病例汇总", index=False)
    st.download_button("📊 下载 Excel", buffer.getvalue(),
                       file_name="crc_cases.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)