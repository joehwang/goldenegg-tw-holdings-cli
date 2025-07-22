import easyocr

# 初始化 reader（只需要執行一次）
reader = easyocr.Reader(['ch_tra','en'])

# 讀取圖片並進行文字識別
result = reader.readtext('image.png')

 
print(result)