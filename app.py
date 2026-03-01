import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 레이아웃을 'wide'로 설정하고, 페이지 제목과 아이콘을 지정하세요.
st.set_page_config(
    page_title="나의 멋진 앱",
    page_icon="📱",
    layout="wide", # 휴대폰 화면을 꽉 채우기 좋습니다.
    initial_sidebar_state="collapsed" # 모바일에서 사이드바가 가리지 않게 숨김
)

st.title("안드로이드 앱 모드 🚀")
st.write("이제 터미널을 꺼도 백그라운드에서 돌아가고 있습니다.")

# 파일 경로 설정
DB_FILE = "prayers.csv"

# 페이지 설정
st.set_page_config(page_title="우리들의 기도", page_icon="🙏")

# --- 데이터 관리 함수 ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if 'counts' not in df.columns:
            df['counts'] = 0
        return df
    else:
        return pd.DataFrame(columns=["name", "content", "date", "counts"])

def save_data(name, content):
    df = load_data()
    safe_name = name.strip() if name.strip() else "익명"
    new_data = pd.DataFrame([{
        "name": safe_name,
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "counts": 0
    }])
    updated_df = pd.concat([df, new_data], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def update_count(index):
    df = load_data()
    df.at[index, 'counts'] += 1
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.rerun()

# --- 팝업(Dialog) 함수 ---
@st.dialog("기도 삭제 확인")
def show_delete_dialog(index, target_name):
    st.write(f"⚠️ **{target_name}** 님의 기도 제목을 삭제하시겠습니까?")
    st.write("삭제를 확인하려면 작성하셨던 이름을 입력해주세요.")
    
    input_name = st.text_input("이름 확인", key=f"confirm_name_{index}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("진짜 삭제", type="primary", use_container_width=True):
            if input_name.strip() == target_name:
                df = load_data()
                df = df.drop(index)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("삭제되었습니다!")
                st.rerun()
            else:
                st.error("이름이 일치하지 않습니다.")
    with col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

# --- UI 레이아웃 ---
st.title("🙏 우리들의 기도 수첩")

# 1. 입력 폼
with st.form("prayer_form", clear_on_submit=True):
    name = st.text_input("작성자 이름 (삭제 시 필요)")
    content = st.text_area("기도 제목을 적어주세요")
    submit = st.form_submit_button("기도 등록")

    if submit:
        if content and name:
            save_data(name, content)
            st.success("기도가 등록되었습니다!")
            st.rerun()
        else:
            st.warning("이름과 내용을 모두 입력해주세요.")

# 2. 리스트 출력
st.divider()
df = load_data()

if not df.empty:
    for index in reversed(df.index):
        row = df.loc[index]
        with st.container(border=True): # 테두리 있는 카드 형태
            st.markdown(f"**👤 {row['name']}** <small style='color:gray;'>({row['date']})</small>", unsafe_allow_html=True)
            st.info(row['content'])
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"🙌 중보합니다 ({row['counts']})", key=f"pray_{index}"):
                    update_count(index)
            with col2:
                # 클릭 시 팝업 창을 띄움
                if st.button("🗑️ 삭제", key=f"del_{index}", use_container_width=True):
                    show_delete_dialog(index, row['name'])
else:
    st.write("아직 등록된 기도가 없습니다.")

