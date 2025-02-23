import os
import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(prefix="", password=os.environ.get("COOKIES_PASSWORD", "My secret password"))

if not cookies.ready():
    st.warning("쿠키 매니저가 초기화되지 않았습니다. 페이지를 새로고침하세요.")
    st.stop()

FASTAPI_URL = "http://localhost:8000"  # FastAPI 서버 주소

# 로그인 함수
def login(user_id):
    response = requests.post(f"{FASTAPI_URL}/login", params={"user_id": user_id})
    if response.status_code == 200:
        st.session_state["session_id"] = response.cookies.get("session_id")
        cookies["session_id"] = user_id
        cookies.save()
        st.success("로그인 성공! 쿠키가 설정되었습니다.")
    else:
        st.error("로그인 실패!")

# 쿠키 확인 함수
def check_cookie():
    if "session_id" not in [i.split("=")[0].strip() for i in st.session_state["CookieManager.sync_cookies"].split(";")]:
        st.error("쿠키가 없습니다. 로그인해주세요.")
        # st.markdown('<meta http-equiv="refresh" content="0;URL=http://localhost:8000/docs#/Session%20Test/login_login_post">', unsafe_allow_html=True)

        return

    cookies = {"session_id": ""}
    # cookies = {"session_id": st.session_state["session_id"]}

    response = requests.get(f"{FASTAPI_URL}/sso/logout", cookies=cookies)
    # st.markdown(response.json())

    if response.status_code == 200: # and response.json().get("message") == "success":
        st.success("인증 성공! 서비스 페이지로 이동 가능")
        st.markdown(response.text)
        # st.markdown('<meta http-equiv="refresh" content="0;URL=https://www.google.com">', unsafe_allow_html=True)

    else:
        st.error("인증 실패! 다시 로그인하세요.")
        # st.markdown('<meta http-equiv="refresh" content="0;URL=http://localhost:8000/docs#/Session%20Test/login_login_post">', unsafe_allow_html=True)


# Streamlit UI
st.title("FastAPI + Streamlit 쿠키 인증")

user_id = st.text_input("사용자 ID 입력")
if st.button("로그인"):
    login(user_id)

if st.button("쿠키 확인"):
    check_cookie()

st.session_state