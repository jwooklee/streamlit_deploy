import streamlit as st
import speech_recognition as sr
import os
import tempfile
from audio_recorder_streamlit import audio_recorder

# 페이지 설정
st.set_page_config(
    page_title="음성 녹음 및 변환",
    page_icon="🎙️",
    layout="centered"
)

# CSS 스타일 추가
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #e87474;
        color: white;
    }
    .recorder-container {
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .status-text {
        color: #6aa36f;
        font-weight: bold;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def speech_to_text(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name

    try:
        r = sr.Recognizer()
        with sr.AudioFile(temp_file_path) as source:
            # 배경 노이즈 감소 설정 추가
            r.dynamic_energy_threshold = True
            r.energy_threshold = 4000
            
            # 오디오 녹음 감도 조정
            audio = r.record(source)
            r.adjust_for_ambient_noise(source)
            
            # 음성을 텍스트로 변환
            text = r.recognize_google(audio, language='ko-KR')
            return text
    except sr.UnknownValueError:
        return "❌ 음성을 인식할 수 없습니다. 다시 녹음해주세요."
    except sr.RequestError:
        return "❌ 음성 인식 서비스에 접근할 수 없습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def main():
    st.title("🎙️ 음성 녹음 및 텍스트 변환")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 실시간 녹음", "📤 파일 업로드"])
    
    with tab1:
        st.markdown("""
        <div class="recorder-container">
        <h3>실시간 음성 녹음</h3>
        <p>마이크 버튼을 클릭하여 음성을 녹음하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 실시간 오디오 녹음
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e87474",
            neutral_color="#6aa36f",
            icon_size="2x"
        )
        
        if audio_bytes:
            st.markdown('<p class="status-text">✅ 녹음이 완료되었습니다!</p>', unsafe_allow_html=True)
            
            # 녹음된 오디오 재생
            st.audio(audio_bytes, format="audio/wav")
            
            with st.spinner('텍스트 변환 중...'):
                text = speech_to_text(audio_bytes)
            
            st.markdown("### 📝 변환된 텍스트:")
            st.info(text)
    
    with tab2:
        st.markdown("""
        <div class="recorder-container">
        <h3>음성 파일 업로드</h3>
        <p>WAV 형식의 음성 파일을 업로드하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=['wav'])
        
        if uploaded_file is not None:
            st.markdown('<p class="status-text">✅ 파일이 업로드되었습니다!</p>', unsafe_allow_html=True)
            
            # 업로드된 파일 재생
            st.audio(uploaded_file, format="audio/wav")
            
            with st.spinner('텍스트 변환 중...'):
                audio_bytes = uploaded_file.read()
                text = speech_to_text(audio_bytes)
            
            st.markdown("### 📝 변환된 텍스트:")
            st.info(text)

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ using Streamlit</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()