import streamlit as st
import google.generativeai as genai
import os

# --- CÁC HÀM HỖ TRỢ ---
def rfile(name_file):
    """Hàm đọc nội dung từ file văn bản một cách an toàn."""
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file `{name_file}`. Vui lòng đảm bảo file này tồn tại.")
        return "" # Trả về chuỗi rỗng nếu file không tồn tại

# --- KIỂM TRA VÀ KHỞI TẠO API KEY ---
gemini_api_key = st.secrets.get("GOOGLE_API_KEY")
if not gemini_api_key:
    st.error("Chưa tìm thấy Gemini API Key. Vui lòng thêm key vào Streamlit Secrets với tên `GOOGLE_API_KEY`.")
    st.stop()

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-pro")

# --- GIAO DIỆN NGƯỜI DÙNG ---
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)

title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
    unsafe_allow_html=True
)

# --- LOGIC CHATBOT ---

if "messages" not in st.session_state:
    system_prompt = rfile("01.system_trainning.txt")
    assistant_greeting = rfile("02.assistant.txt")
    if system_prompt and assistant_greeting:
        st.session_state.messages = [
            {"role": "user", "content": system_prompt},
            {"role": "assistant", "content": assistant_greeting}
        ]
    else:
        st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung bạn cần tư vấn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chuẩn bị đoạn hội thoại cho Gemini (không hỗ trợ vai trò "system")
    history = [m["content"] for m in st.session_state.messages if m["role"] != "system"]

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(history)
            output = response.text
            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"Đã có lỗi xảy ra khi kết nối tới Gemini: {e}")
