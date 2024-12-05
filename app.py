import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
from streamlit.components.v1 import html

def speech_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language='ko-KR')
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError:
        return "음성 인식 서비스에 접근할 수 없습니다."

# HTML/JavaScript 코드 정의
def get_audio_recorder_html():
    return """
        <div class="audio-recorder">
            <button id="recordButton" onclick="toggleRecording()">녹음 시작</button>
            <div id="recordingStatus"></div>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            async function toggleRecording() {
                const button = document.getElementById('recordButton');
                const status = document.getElementById('recordingStatus');
                
                if (!isRecording) {
                    // 녹음 시작
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        // Streamlit으로 데이터 전송
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = function() {
                            const base64data = reader.result;
                            window.parent.postMessage({
                                type: "audio_data",
                                data: base64data
                            }, "*");
                        };
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    button.textContent = "녹음 중지";
                    status.textContent = "녹음 중...";
                } else {
                    // 녹음 중지
                    mediaRecorder.stop();
                    isRecording = false;
                    button.textContent = "녹음 시작";
                    status.textContent = "녹음 완료";
                }
            }
        </script>
    """

def main():
    st.title("🎙️ 실시간 음성 녹음 및 텍스트 변환")
    st.write("버튼을 클릭하여 음성을 녹음하고 텍스트로 변환하세요.")
    
    # 오디오 녹음기 컴포넌트 추가
    html(get_audio_recorder_html(), height=200)
    
    # 파일 업로더도 유지
    uploaded_file = st.file_uploader("또는 WAV 파일을 업로드하세요", type=['wav'])
    
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_audio_{timestamp}.wav"
        
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        text = speech_to_text(temp_file)
        
        st.write("## 변환된 텍스트:")
        st.write(text)
        
        os.remove(temp_file)

if __name__ == "__main__":
    main()