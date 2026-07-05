import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- 頁面設定 ---
st.set_page_config(page_title="描寫字帖產生器", page_icon="✏️")
st.title("✏️ 虛線描寫字帖產生器")
st.write("輸入文字，自動幫你轉換成可以列印下來描寫的虛線圖片！")

# --- 側邊欄設定 ---
st.sidebar.header("字帖設定")
font_size = st.sidebar.slider("字體大小", min_value=50, max_value=300, value=150)
text_color = st.sidebar.color_picker("字體顏色", "#000000") # 預設黑色
bg_color = "#FFFFFF" # 背景固定白色

# --- 主畫面輸入 ---
user_text = st.text_area("請輸入你要產生描寫的文字 (支援多行)：", "S s\nA a\nB b")

def generate_image(text, font_size, text_color):
    try:
        # 請確保你的 GitHub 目錄下有 Trace.ttf 這個字體檔
        font_path = "Quicksand_Dash.otf" 
        if not os.path.exists(font_path):
            st.error("找不到字體檔案！請確認 GitHub 中有上傳 `Trace.ttf`。")
            return None

        font = ImageFont.truetype(font_path, font_size)
        
        # 先建立一個暫時的畫布來計算文字大小
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        
        # 計算文字範圍 (Bounding Box)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 加上留白邊距 (Padding)
        padding = 100
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2
        
        # 建立正式的圖片
        img = Image.new('RGB', (img_width, img_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # 將文字畫上去
        draw.text((padding, padding), text, font=font, fill=text_color)
        
        return img
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return None

# --- 產生與下載區塊 ---
if st.button("產生字帖圖片 🪄"):
    if user_text.strip() == "":
        st.warning("請先輸入文字喔！")
    else:
        with st.spinner("產生中..."):
            img = generate_image(user_text, font_size, text_color)
            
            if img:
                # 顯示圖片
                st.image(img, caption="你的專屬描寫字帖", use_container_width=True)
                
                # 準備下載
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 下載字帖圖片",
                    data=byte_im,
                    file_name="tracing_worksheet.png",
                    mime="image/png"
                )
