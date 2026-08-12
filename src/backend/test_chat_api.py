import urllib.request
import json
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Lấy Token
login_url = "http://localhost:8000/auth/login"
test_email = os.getenv("TEST_USER_EMAIL")
test_password = os.getenv("TEST_USER_PASSWORD")
if not test_email or not test_password:
    raise RuntimeError("Hãy khai báo TEST_USER_EMAIL và TEST_USER_PASSWORD")
login_payload = f"username={test_email}&password={test_password}".encode('utf-8')
req_login = urllib.request.Request(login_url, data=login_payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})

try:
    with urllib.request.urlopen(req_login, context=ctx) as response:
        token_data = json.loads(response.read().decode('utf-8'))
        token = token_data.get("access_token")
except urllib.error.HTTPError as e:
    print(f"Lỗi đăng nhập: {e.read().decode('utf-8')}")
    token = None

if token:
    # 2. Gọi Chat
    chat_url = "http://localhost:8000/chat"
    payload = {"conversation_id": 2, "question": "Xin chào"}
    data = json.dumps(payload).encode('utf-8')
    req_chat = urllib.request.Request(chat_url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    })

    print("Gửi request POST /chat (đã có Token)...")
    try:
        with urllib.request.urlopen(req_chat, context=ctx) as response:
            print(f"Status Code: {response.status}")
            print(f"Response Body: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code}")
        print(f"Response Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Lỗi: {e}")
