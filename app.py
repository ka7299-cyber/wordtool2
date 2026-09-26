import streamlit as st
import requests
import pyttsx3
import tempfile
import os

def get_word_info(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    data = response.json()[0]
    phonetic = data.get("phonetic", "無音標")
    
    # 找例句
    example = None
    for meaning in data["meanings"]:
        for definition in meaning["definitions"]:
            if "example" in definition:
                example = definition["example"]
                break
        if example:
            break
    
    return {
        "word": word,
        "phonetic": phonetic,
        "example": example if example else "無例句"
    }

def generate_audio(word):
    engine = pyttsx3.init()
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    engine.save_to_file(word, tmp_file.name)
    engine.runAndWait()
    return tmp_file.name

# Streamlit 介面
st.title("📘 英文單字快查工具")

word = st.text_input("輸入英文單字：")

if word:
    result = get_word_info(word)
    if result:
        st.write(f"**單字**: {result['word']}")
        st.write(f"**音標**: {result['phonetic']}")
        st.write(f"**例句**: {result['example']}")
        
        # 語音播放
        audio_file = generate_audio(word)
        audio_bytes = open(audio_file, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        
        # 清理暫存檔
        os.remove(audio_file)
    else:
        st.error("查不到這個單字，請再試一次。")
