import requests, re, urllib.parse, csv, time
from datetime import datetime

# ===== 读取 cookie.txt =====
def load_cookie():
    with open("cookie.txt", "r", encoding="utf-8") as f:
        return f.read().replace("\n", "").strip()

COOKIE = load_cookie()
URL = "https://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "text/plain",
    "Origin": "https://www.lofter.com",
    "Referer": "https://www.lofter.com",
    "Cookie": COOKIE,
}

# ===== 解析响应文本 =====
def parse_posts(text):
    posts = []
    for m in re.finditer(r'blogPageUrl="([^"]+)".*?createTime=(\d+);', text, re.S):
        url, ts = m.groups()
        ts = int(ts)
        dt = datetime.fromtimestamp(ts / 1000)
        posts.append((url, dt, ts))  # 顺便保留原始毫秒时间戳
    return posts

# ===== 抓取一页 =====
def fetch_page(tag, offset=0, size=20, order="new", last_time=0):
    encoded_tag = urllib.parse.quote(tag)
    data = (
        "callCount=1\n"
        "scriptSessionId=${scriptSessionId}187\n"
        "httpSessionId=\n"
        "c0-scriptName=TagBean\n"
        "c0-methodName=search\n"
        "c0-id=0\n"
        f"c0-param0=string:{encoded_tag}\n"
        "c0-param1=number:0\n"
        "c0-param2=string:\n"
        f"c0-param3=string:{order}\n"
        "c0-param4=boolean:false\n"
        "c0-param5=number:0\n"
        f"c0-param6=number:{size}\n"
        f"c0-param7=number:{offset}\n"
        f"c0-param8=number:{last_time}\n"
        "batchId=1\n"
    )
    resp = requests.post(URL, headers=HEADERS, data=data)
    return parse_posts(resp.text)

# ===== 统计指定时间范围 =====
def count_in_range(tag, start_dt, end_dt, page_size=20):
    total = 0
    all_posts = []
    offset = 0
    last_time = 0

    while True:
        posts = fetch_page(tag, offset=offset, size=page_size, last_time=last_time)
        if not posts:
            break

        print(f"第 {offset // page_size + 1} 页 {len(posts)} 条")

        for url, dt, ts in posts:
            if start_dt <= dt <= end_dt:
                total += 1
                all_posts.append((url, dt))

        # 更新游标
        offset += page_size
        last_time = posts[-1][2]

        # 如果最后一条比 start_dt 还早，可以停
        if posts[-1][1] < start_dt:
            break

        time.sleep(1)

    return total, all_posts

# ===== 日期解析 =====
def parse_date_input(date_str, is_start=True):
    """
    将用户输入的日期字符串解析成 datetime
    支持格式：
    - 2025-09-01
    - 20250901
    - 2025/09/01
    - 2025 09 01
    """
    date_str = date_str.strip().replace("/", "-").replace(" ", "-")
    if date_str.isdigit() and len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if is_start:
        return dt.replace(hour=0, minute=0, second=0)
    else:
        return dt.replace(hour=23, minute=59, second=59)

# ===== 主程序 =====
if __name__ == "__main__":
    TAG = input("请输入要查询的 tag：").strip()
    start_input = input("请输入开始日期 (如 2025-09-01 / 20250901 / 2025 09 01)：").strip()
    end_input = input("请输入结束日期 (如 2025-09-26 / 20250926 / 2025 09 26)：").strip()

    START = parse_date_input(start_input, is_start=True)
    END = parse_date_input(end_input, is_start=False)

    count, posts = count_in_range(TAG, START, END)

    print(f"\n【结果】标签 {TAG} 在 {START} ~ {END} 的更新数：{count}")
    for url, dt in posts:
        print(dt, url)

    with open("result.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["时间", "链接"])
        for url, dt in posts:
            writer.writerow([dt.strftime("%Y-%m-%d %H:%M:%S"), url])

    print("✅ 已导出到 result.csv")
