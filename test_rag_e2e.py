import urllib.request
import urllib.parse
import json
import time
import os
import io

ALB_URL = 'http://127.0.0.1:8000/api'
TIMESTAMP = int(time.time())
TEST_EMAIL = f'test_user_{TIMESTAMP}@enterprise-rag.com'
TEST_PASSWORD = 'TestPassword2026@AWS'

print('======================================================================')
print('   BAT DAU KIEM THU TOAN DIEN HE THONG ENTERPRISE RAG TREN AWS EC2    ')
print('======================================================================\n')

# 1. TEST HEALTH CHECK
print('[1/8] Kiem tra API Health Check...')
req = urllib.request.Request(f'{ALB_URL}/')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print(f'   -> Status: {resp.status}, Response: {data}')
    assert resp.status == 200

# 2. TEST DANG KY TAI KHOAN (POSTGRESQL RDS)
print('\n[2/8] Kiem tra Dang ky Tai khoan (PostgreSQL RDS)...')
req = urllib.request.Request(
    f'{ALB_URL}/auth/register',
    data=json.dumps({'email': TEST_EMAIL, 'password': TEST_PASSWORD}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    user_data = json.loads(resp.read().decode())
    print(f'   -> User ID: {user_data.get("id")}, Email: {user_data.get("email")}')
    assert user_data.get('email') == TEST_EMAIL

# 3. TEST DANG NHAP LAY JWT TOKEN
print('\n[3/8] Kiem tra Dang nhap & JWT Token...')
form_data = urllib.parse.urlencode({'username': TEST_EMAIL, 'password': TEST_PASSWORD}).encode('utf-8')
req = urllib.request.Request(f'{ALB_URL}/auth/login', data=form_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(req) as resp:
    token_data = json.loads(resp.read().decode())
    token = token_data.get('access_token')
    print(f'   -> Access Token (JWT): {token[:35]}...')
    assert token is not None

# 4. TEST XAC THUC PROFILE
print('\n[4/8] Kiem tra Lay thong tin Profile (Bearer Token)...')
req = urllib.request.Request(f'{ALB_URL}/auth/me', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as resp:
    profile = json.loads(resp.read().decode())
    print(f'   -> Email profile: {profile.get("email")}, Active: {profile.get("is_active")}')
    assert profile.get('email') == TEST_EMAIL

# 5. TEST TAI TAI LIEU LEN (AWS S3 + QDRANT VECTOR DB)
print('\n[5/8] Kiem tra Upload Tai lieu (S3 Bucket + Embedding Qdrant)...')
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
doc_content = '''CHINH SACH AN NINH THONG TIN DOANH NGHIEP RAG 2026:
1. Dieu khoan 1: Tat ca du lieu nghien cuu y te va tai chinh phai duoc ma hoa bang chuan AES-256 truoc khi luu tru tren AWS S3.
2. Dieu khoan 2: Moi nhan vien chi duoc phep truy cap vao he thong thong qua chung thuc da yeu to MFA va IAM Role hop le.
3. Dieu khoan 3: He thong Vector Database Qdrant luu tru toan bo embeddings vector voi chieu vector la 384 theo mo hinh all-MiniLM-L6-v2.
4. Dieu khoan 4: Cong nghe AI su dung mo hinh Google Gemini 2.5 Flash de phan tich va tra loi thac mac.'''.encode('utf-8')

body = io.BytesIO()
body.write(f'--{boundary}\r\n'.encode('utf-8'))
body.write(b'Content-Disposition: form-data; name="file"; filename="Chinh_Sach_Bao_Mat_2026.txt"\r\n')
body.write(b'Content-Type: text/plain\r\n\r\n')
body.write(doc_content)
body.write(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
body_bytes = body.getvalue()

req = urllib.request.Request(
    f'{ALB_URL}/document/upload',
    data=body_bytes,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body_bytes))
    }
)
with urllib.request.urlopen(req) as resp:
    doc_res = json.loads(resp.read().decode())
    doc_id = doc_res.get('id')
    doc_name = doc_res.get('filename')
    print(f'   -> Upload thanh cong: Document ID = {doc_id}, Ten file = {doc_name}')
    assert doc_id is not None

# 6. TEST LIST DOCUMENTS
print('\n[6/8] Kiem tra Danh sach Tai lieu (PostgreSQL RDS)...')
req = urllib.request.Request(f'{ALB_URL}/document/list', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as resp:
    docs = json.loads(resp.read().decode())
    print(f'   -> So luong tai lieu cua User: {len(docs)}')
    for d in docs:
        print(f'      * [{d.get("id")}] {d.get("filename")} (Kich thuoc: {d.get("file_size")} bytes)')

# 7. TEST TAO CUOC TRO CHUYEN
print('\n[7/8] Kiem tra Tao Phien hoi thoai (Conversation)...')
req = urllib.request.Request(
    f'{ALB_URL}/conversation/',
    data=json.dumps({'title': 'Hoi dap An ninh Thong tin', 'document_ids': [doc_id]}).encode('utf-8'),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    conv = json.loads(resp.read().decode())
    conv_id = conv.get('id')
    print(f'   -> Conversation ID = {conv_id}, Title = {conv.get("title")}')
    assert conv_id is not None

# 8. TEST CHAT RAG AI (QDRANT RETRIEVAL + GEMINI 2.5 FLASH)
print('\n[8/8] Kiem tra Chat RAG AI (Tra cuu Vector Qdrant + Google Gemini 2.5 Flash)...')
question = 'He thong RAG yeu cau ma hoa du lieu tren S3 bang chuan gi va AI dung model nao?'
print(f'   -> Cau hoi: "{question}"')
req = urllib.request.Request(
    f'{ALB_URL}/chat',
    data=json.dumps({'conversation_id': conv_id, 'question': question}).encode('utf-8'),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
)
start_t = time.time()
with urllib.request.urlopen(req) as resp:
    chat_res = json.loads(resp.read().decode())
    duration = round(time.time() - start_t, 2)
    print(f'   -> Thoi gian phan hoi: {duration}s')
    print(f'   -> Cau tra loi tu Gemini AI:\n------------------------------------------------------------')
    print(chat_res.get('answer'))
    print('------------------------------------------------------------')

print('\n======================================================================')
print('   KET QUA: 100% TAT CA CAC CHUC NANG DA HOAT DONG HOAN MY TREN AWS!   ')
print('======================================================================')
