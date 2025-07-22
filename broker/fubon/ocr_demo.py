from PIL import Image
import pytesseract
import os

def perform_ocr(image_path):
    """
    對圖片進行 OCR 文字識別
    :param image_path: 圖片路徑
    :return: 識別出的文字
    """
    try:
        # 開啟圖片
        image = Image.open(image_path)
        
        # 執行 OCR
        text = pytesseract.image_to_string(image, lang='chi_tra+eng')
        
        return text
    except Exception as e:
        return f"發生錯誤: {str(e)}"

if __name__ == "__main__":
    # 請將 'test.png' 替換為您要識別的圖片路徑
    image_path = "test.png"
    
    if os.path.exists(image_path):
        result = perform_ocr(image_path)
        print("OCR 識別結果：")
        print("-" * 50)
        print(result)
        print("-" * 50)
    else:
        print(f"找不到圖片檔案：{image_path}") 