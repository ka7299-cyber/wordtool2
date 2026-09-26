import streamlit as st
import requests

def get_word_info(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    data = response.json()[0]
    phonetic = data.get("phonetic", "無音標")
    
    example = None
    for meaning in data["meanings"]:
        for definition in meaning["definitions"]:
            if "example" in definition:
                example = definition["example"]
                break
        if example:
            break
    
    audio_url = None
    if "phonetics" in data:
        for ph in data["phonetics"]:
            if "audio" in ph and ph["audio"]:
                audio_url = ph["audio"]
                break
    
    return {
        "word": word,
        "phonetic": phonetic,
        "example": example if example else "無例句",
        "audio_url": audio_url
    }

st.title("📘 英文單字快查工具")

word = st.text_input("輸入英文單字：")

if word:
    result = get_word_info(word)
    if result:
        st.write(f"**單字**: {result['word']}")
        st.write(f"**音標**: {result['phonetic']}")
        st.write(f"**例句**: {result['example']}")
        
        if result["audio_url"]:
            st.audio(result["audio_url"])
        else:
            st.warning("⚠️ 沒有找到發音音檔")
    else:
        st.error("查不到這個單字，請再試一次。")
