import urllib.request
import urllib.parse
import json
import time

ALB_URL = 'http://rag-lb-1113719893.ap-southeast-1.elb.amazonaws.com/api'
DOCS_URL = 'http://rag-lb-1113719893.ap-southeast-1.elb.amazonaws.com/docs'
TIMESTAMP = int(time.time())
TEST_EMAIL = f'minh_test_{TIMESTAMP}@enterprise-rag.com'
TEST_PASSWORD = 'Password2026@AWS'

print('=' * 75)
print('   KIEM THU TOAN DIEN HE THONG RAG QUA APPLICATION LOAD BALANCER (ALB)   ')
print('=' * 75)

# TEST 1: HEALTH CHECK VIA ALB
print('\n[1/7] KIEM THU PUBLIC ROUTING QUA LOAD BALANCER (/docs)...')
req = urllib.request.Request(DOCS_URL)
with urllib.request.urlopen(req) as resp:
    print(f'   -> ALB Routing Status: {resp.status} OK (FastAPI Swagger UI)')
    assert resp.status == 200

# TEST 2: AUTH REGISTER
print('\n[2/7] KIEM THU DANG KY NGUOI DUNG MOI (Luu vao AWS RDS PostgreSQL)...')
req = urllib.request.Request(
    f'{ALB_URL}/auth/register',
    data=json.dumps({'email': TEST_EMAIL, 'password': TEST_PASSWORD}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    reg_data = json.loads(resp.read().decode())
    print(f'   -> Status: {resp.status} Created')
    print(f'   -> User ID tao moi: {reg_data.get("id")}')
    print(f'   -> Email da luu: {reg_data.get("email")}')
    assert reg_data.get('email') == TEST_EMAIL

# TEST 3: AUTH LOGIN
print('\n[3/7] KIEM THU DANG NHAP & CAP PHAT TOKEN JWT (Bcrypt + PyJWT)...')
form_data = urllib.parse.urlencode({'username': TEST_EMAIL, 'password': TEST_PASSWORD}).encode('utf-8')
req = urllib.request.Request(f'{ALB_URL}/auth/login', data=form_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(req) as resp:
    login_data = json.loads(resp.read().decode())
    token = login_data.get('access_token')
    print(f'   -> Token Type: {login_data.get("token_type")}')
    print(f'   -> Access Token: {token[:30]}...[TRUNCATED]...{token[-15:]}')
    assert token is not None

# TEST 4: AUTH PROFILE
print('\n[4/7] KIEM THU XAC THUC NGUOI DUNG HIEN TAI (Bearer Authentication)...')
req = urllib.request.Request(f'{ALB_URL}/auth/me', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as resp:
    me_data = json.loads(resp.read().decode())
    print(f'   -> User ID: {me_data.get("id")}')
    print(f'   -> Email: {me_data.get("email")}')
    print(f'   -> Trang thai Active: {me_data.get("is_active")}')
    assert me_data.get('email') == TEST_EMAIL

# TEST 5: CONVERSATION MANAGEMENT
print('\n[5/7] KIEM THU QUAN LY PHIEN HOI THOAI (Conversation trong RDS)...')
req = urllib.request.Request(
    f'{ALB_URL}/conversation/',
    data=json.dumps({'title': 'Khao sat Bao mat Du lieu Y te AWS', 'document_ids': []}).encode('utf-8'),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    conv_data = json.loads(resp.read().decode())
    conv_id = conv_data.get('id')
    print(f'   -> Tao cuoc tro chuyen thanh cong: ID = {conv_id}')
    print(f'   -> Tieu de: "{conv_data.get("title")}"')

req_list = urllib.request.Request(f'{ALB_URL}/conversation/list', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req_list) as resp:
    conv_list = json.loads(resp.read().decode())
    print(f'   -> Danh sach cuoc tro chuyen cua user (So luong: {len(conv_list)})')

# TEST 6: DOCUMENT LIST
print('\n[6/7] KIEM THU TRUY VAN DANH SACH TAI LIEU (PostgreSQL RDS)...')
req_docs = urllib.request.Request(f'{ALB_URL}/document/list', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req_docs) as resp:
    docs = json.loads(resp.read().decode())
    print(f'   -> So luong tai lieu: {len(docs)}')

# TEST 7: AUDIT LOGS
print('\n[7/7] KIEM THU AUDIT TRAIL / ACTIVITY LOGGING (Bao mat Enterprise)...')
req_act = urllib.request.Request(f'{ALB_URL}/activity/me', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req_act) as resp:
    acts = json.loads(resp.read().decode())
    print(f'   -> Nhat ky hoat dong da ghi nhan ({len(acts)} su kien):')
    for a in acts[:5]:
        print(f'      * [{a.get("action")}] {a.get("details")} (Time: {a.get("created_at")})')

print('\n' + '=' * 75)
print('      TAT CA 7 BIEU KIEM CHUC NANG API DA VUOT QUA THANH CONG 100%!     ')
print('=' * 75)
