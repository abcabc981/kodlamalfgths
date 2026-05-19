import streamlit as st
import openai

# --- Yapılandırma ---
st.set_page_config(page_title="Mega-Coder Oyun Mimarı", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_all_components=True)

st.title("🏗️ Mega-Coder: Kesintisiz Oyun Geliştirici")
st.info("Bu sistem, oyunu en büyük parçalar halinde yazar. Kod kesilirse 'Devam et' demen yeterlidir.")

# --- Yapay Zeka Sistem Mesajı ---
SISTEM_MESAJI = """Sen dünyanın en iyi oyun programlama asistanısın. 
Görevin: Kullanıcının istediği oyunu EN AZ PARÇAYA BÖLEREK, en uzun ve eksiksiz kod bloklarıyla yazmak. 
Eğer kod çok uzunsa ve kesilirse, bir sonraki mesajda tam olarak kaldığın yerden (en son karakterden) hiçbir şeyi tekrar etmeden devam etmelisin.
Kodların modüler, profesyonel and hatasız olmalı. Sadece kod ve gerekli açıklamaları ver."""

# --- Hafıza Yönetimi ---
if 'chat_gecmisi' not in st.session_state:
    st.session_state.chat_gecmisi = [{"role": "system", "content": SISTEM_MESAJI}]

if 'proje_ozeti' not in st.session_state:
    st.session_state.proje_ozeti = "Henüz bir projeye başlanmadı."

# --- Yan Panel ---
with st.sidebar:
    st.header("🔑 Ayarlar & Hafıza")
    api_key = st.text_input("OpenAI API Key:", type="password")
    
    st.subheader("📝 Proje Özeti")
    st.caption("Yapay zeka bu konsepti hatırlar:")
    st.info(st.session_state.proje_ozeti)
    
    st.subheader("📊 Hafıza Durumu")
    st.caption(f"Toplam Mesaj Sayısı: {len(st.session_state.chat_gecmisi) - 1}")
    
    if st.button("Hafızayı ve Geçmişi Sıfırla"):
        st.session_state.chat_gecmisi = [{"role": "system", "content": SISTEM_MESAJI}]
        st.session_state.proje_ozeti = "Henüz bir projeye başlanmadı."
        st.success("Hafıza sıfırlandı!")
        st.rerun()

# --- Ana İşlem Fonksiyonu ---
def kod_uret_v2():
    if not api_key:
        st.error("Lütfen API anahtarını yan panelden girin!")
        return None
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.chat_gecmisi,
            temperature=0.2
        )
        
        yanit = response.choices[0].message.content
        return yanit
    except Exception as e:
        st.error(f"OpenAI API Hatası: {str(e)}")
        return None

# --- Arayüz sekmeleri ---
tab1, tab2 = st.tabs(["🚀 Kod Üretimi", "🛠️ Kod Kontrol & Özellik Ekle"])

with tab1:
    istek = st.text_area("Oyun özelliklerini buraya yaz (Örn: Clash Royale temel mekaniği, kuleler, iksir sistemi olsun):", height=150)
    col1, col2 = st.columns(2)
    
    if col1.button("Dev Kod Bloğu Oluştur"):
        if istek:
            st.session_state.chat_gecmisi.append({"role": "user", "content": istek})
            st.session_state.proje_ozeti = f"Proje: {istek[:60]}..."
            
            with st.spinner("Yapay zeka sınırları zorluyor, kod yazılıyor..."):
                cevap = kod_uret_v2()
                if cevap:
                    st.session_state.chat_gecmisi.append({"role": "assistant", "content": cevap})
                    st.markdown("### 📜 Üretilen Kod / Yanıt")
                    st.markdown(cevap)
        else:
            st.warning("Lütfen önce bir oyun isteği yazın.")

    if col2.button("Kaldığın Yerden Devam Et"):
        st.session_state.chat_gecmisi.append({
            "role": "user", 
            "content": "Kod yarım kaldı veya kesildi. Lütfen hiçbir ekstra açıklama yapmadan, TAM OLARAK kaldığın satırdan/karakterden itibaren kodun devamını yaz."
        })
        
        with st.spinner("Kodun devamı getiriliyor..."):
            cevap = kod_uret_v2()
            if cevap:
                st.session_state.chat_gecmisi.append({"role": "assistant", "content": cevap})
                st.markdown("### 🏗️ Kodun Devamı")
                st.markdown(cevap)

with tab2:
    st.subheader("Hata Düzeltme veya Yeni Özellik")
    eski_kod = st.text_area("Mevcut kodu yapıştır:", height=200)
    degisiklik = st.text_input("Ne değişecek? (Örn: 'Karakterlerin hızını 2 kat yap ve can barı ekle')")
    
    if st.button("Kodu Güncelle"):
        if eski_kod and degisiklik:
            # Kodun kırılmaması için string birleştirmeleri tamamen tek satırda ve güvenli hale getirildi:
            baslangic = "Mevcut Kod:\n```python\n"
            orta = "\n```\n\nBu kod üzerinde şu değişikliği yap: "
            istek_metni = baslangic + eski_kod + orta + degisiklik
            
            st.session_state.chat_gecmisi.append({"role": "user", "content": istek_metni})
            
            with st.spinner("Kod revize ediliyor..."):
                cevap = kod_uret_v2()
                if cevap:
                    st.session_state.chat_gecmisi.append({"role": "assistant", "content": cevap})
                    st.markdown("### ✅ Güncel Kod")
                    st.markdown(cevap)
        else:
            st.warning("Lütfen hem mevcut kodu hem de yapılacak değişikliği girin.")
