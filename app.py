import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- 頁面設定 ---
st.set_page_config(page_title="描寫字帖產生器", page_icon="✏️")
st.title("✏️ 虛線描寫字帖產生器")
st.write("輸入文字，自動幫你轉換成可以列印下來描寫的虛線圖片！(支援自動換行)")

# --- 側邊欄設定 ---
st.sidebar.header("字帖設定")
font_size = st.sidebar.slider("字體大小", min_value=50, max_value=300, value=100)
line_spacing_ratio = st.sidebar.slider("行距大小", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
text_color = st.sidebar.color_picker("字體顏色", "#000000")
bg_color = "#FFFFFF" 

# --- 主畫面輸入 ---
user_text = st.text_area("請輸入你要產生描寫的文字：", "S s\nA a\nB b\n\nYou can also type a long paragraph here, and it will automatically wrap to the next line just like a real worksheet!", height=200)

def generate_image(text, font_size, text_color, line_spacing_ratio):
    try:
        # 字體檔案路徑
        font_path = "Quicksand_Dash.otf" 
        if not os.path.exists(font_path):
            st.error(f"找不到字體檔案 {font_path}！")
            return None

        font = ImageFont.truetype(font_path, font_size)
        
        # 設定畫布固定寬度 (類似 A4 寬度比例，2480px 約等於 300dpi 的 A4 寬)
        MAX_IMAGE_WIDTH = 2480 
        PADDING = 150 # 左右邊界留白
        MAX_TEXT_WIDTH = MAX_IMAGE_WIDTH - (PADDING * 2)

        # --- 自動換行邏輯 ---
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        
        lines = []
        paragraphs = text.split('\n') # 先處理使用者自己按 Enter 的換行
        
        for paragraph in paragraphs:
            if paragraph == "":
                lines.append("") # 保留空行
                continue
                
            words = paragraph.split(' ') # 用空格把單字切開
            current_line = ""
            
            for word in words:
                # 測試加上這個單字後，會不會超過寬度
                test_line = current_line + word + " "
                width = draw.textlength(test_line, font=font)
                
                if width <= MAX_TEXT_WIDTH:
                    current_line = test_line
                else:
                    if current_line: # 把目前的行存起來
                        lines.append(current_line)
                    current_line = word + " " # 把新單字放到下一行
            
            if current_line:
                lines.append(current_line)

        # --- 計算畫布高度 ---
        # 取得字體大約的高度
        bbox = font.getbbox("Ay") 
        base_line_height = bbox[3] - bbox[1]
        line_height = int(base_line_height * line_spacing_ratio)
        
        # 總高度 = 留白 + (行數 * 行高)
        img_height = (PADDING * 2) + (len(lines) * line_height)
        
        # --- 開始繪製正式圖片 ---
        img = Image.new('RGB', (MAX_IMAGE_WIDTH, img_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        y_text = PADDING
        for line in lines:
            if line:
                draw.text((PADDING, y_text), line, font=font, fill=text_color)
            y_text += line_height
            
        return img
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return None

# --- 產生與下載區塊 ---
if st.button("產生字帖圖片 🪄"):
    if user_text.strip() == "":
        st.warning("請先輸入文字喔！")
    else:
        with st.spinner("排版與產生中..."):
            img = generate_image(user_text, font_size, text_color, line_spacing_ratio)
            
            if img:
                # 顯示圖片 (在網頁上縮放顯示)
                st.image(img, caption="你的專屬描寫字帖", use_container_width=True)
                
                # 準備下載
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 下載 A4 尺寸字帖圖片",
                    data=byte_im,
                    file_name="tracing_worksheet.png",
                    mime="image/png"
                )
