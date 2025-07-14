"""
設定測試環境
pytest 在執行測試時，會先執行 conftest.py 檔案
因此，我們可以將專案根目錄加入 Python 路徑
這樣就可以在測試檔案中，使用專案根目錄下的模組

"""

import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 