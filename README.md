# lofter-tag-search
简陋的tag查房程序

## 使用说明

1. 在浏览器登录 https://www.lofter.com
2. 打开开发者工具（F12）→ Network → 找到 `TagBean.search.dwr`
3. 选中请求 → Headers → 复制 `Cookie` 字段（整行），粘贴到项目根目录下的 `cookie.txt`
4. 运行： `python api.py`
5. 注意：请不要把 cookie.txt 上传到 GitHub（已在 .gitignore 中忽略）
