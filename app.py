import streamlit as st
import requests
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="英文單字快查工具", page_icon="📘", layout="centered")

@st.cache_data(show_spinner=False)
def get_word_info_from_dictionaryapi(word: str):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return None
        data = r.json()[0]
        phonetic = data.get("phonetic", "") or ""
        example = None
        definitions = []
        for m in data.get("meanings", []):
            pos = m.get("partOfSpeech", "")
            for d in m.get("definitions", []):
                definitions.append({"pos": pos, "definition": d.get("definition", "")})
                if d.get("example") and not example:
                    example = d.get("example")
        audio_url = None
        for ph in data.get("phonetics", []):
            if ph.get("audio"):
                audio_url = ph.get("audio")
                if audio_url:
                    break
        return {
            "source": "dictionaryapi",
            "phonetic": phonetic,
            "example": example,
            "definitions": definitions,
            "audio_url": audio_url
        }
    except Exception:
        return None

def fallback_translate_zh_libre(word: str):
    """使用 LibreTranslate 公開 API 作為備援翻譯（若被封鎖會回傳 None）"""
    try:
        url = "https://libretranslate.com/translate"
        payload = {"q": word, "source": "en", "target": "zh", "format": "text"}
        r = requests.post(url, data=payload, timeout=6)
        if r.status_code == 200:
            return r.json().get("translatedText")
    except Exception:
        pass
    return None

def generate_tts_file(word: str, lang: str = "en"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    try:
        tts = gTTS(text=word, lang=lang, slow=False)
        tts.save(tmp.name)
        return tmp.name
    except Exception:
        try:
            tmp.close()
            os.remove(tmp.name)
        except Exception:
            pass
        return None

def safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

# ---------- UI ----------
st.title("📘 英文單字快查工具")
st.write("輸入單字後會顯示音標、例句、定義與發音（若有）。若主要來源無結果，會使用備援翻譯與 TTS。")

query = st.text_input("輸入英文單字：", value="", placeholder="例如: apple").strip()

if query:
    word = query.lower()
    with st.spinner("查詢中…"):
        info = get_word_info_from_dictionaryapi(word)

    if info:
        st.markdown(f"**單字**: `{word}`")
        st.markdown(f"**音標**: {info.get('phonetic') or '無'}")
        defs = info.get("definitions", [])
        if defs:
            st.markdown("**定義**:")
            for i, d in enumerate(defs[:5], start=1):
                pos = d.get("pos") or ""
                definition = d.get("definition") or ""
                st.write(f"{i}. {pos} {definition}")
        else:
            st.write("**定義**: 無")

        example = info.get("example")
        if example:
            st.markdown("**例句**:")
            st.write(example)
        else:
            st.write("**例句**: 無")

        audio_url = info.get("audio_url")
        if audio_url:
            try:
                st.audio(audio_url)
            except Exception:
                st.warning("來源音檔無法播放，嘗試備援 TTS。")
                tmp_path = generate_tts_file(word)
                if tmp_path:
                    st.audio(tmp_path)
                    safe_remove(tmp_path)
                else:
                    st.warning("備援 TTS 產生失敗。")
        else:
            tmp_path = generate_tts_file(word)
            if tmp_path:
                st.audio(tmp_path)
                safe_remove(tmp_path)
            else:
                st.warning("沒有找到發音音檔，且備援 TTS 產生失敗。")
        st.success("查詢完成（來源：DictionaryAPI.dev）")
    else:
        st.warning("主要字典查無結果，使用備援翻譯與發音。")
        zh = fallback_translate_zh_libre(word)
        if zh:
            st.markdown(f"**中文翻譯（備援）**: {zh}")
        else:
            st.markdown("**中文翻譯（備援）**: 無法取得（備援翻譯服務可能暫時不可用）")

        tmp_path = generate_tts_file(word)
        if tmp_path:
            st.audio(tmp_path)
            safe_remove(tmp_path)
        else:
            st.warning("備援 TTS 產生失敗。")

        st.info("提示：若常遇到查不到的情況，可考慮使用付費字典 API（如 Oxford、Wordnik 或 Google Cloud）以提高覆蓋率。")
