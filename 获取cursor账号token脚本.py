"""
Cursor Token 获取工具
"""
import hashlib
import base64
import secrets
import uuid
import time
import webbrowser
import requests
from urllib.parse import quote


def generate_pkce():
    array = secrets.token_bytes(32)
    code_verifier = base64.b64encode(array).decode()
    code_verifier = code_verifier.replace('+', '-').replace('/', '_').replace('=', '')
    code_verifier = code_verifier[:43]

    hash_bytes = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.b64encode(hash_bytes).decode()
    code_challenge = code_challenge.replace('+', '-').replace('/', '_').replace('=', '')

    return code_verifier, code_challenge


def get_cursor_token():
    """获取 Cursor Token"""

    verifier, challenge = generate_pkce()
    device_uuid = str(uuid.uuid4())

    auth_url = f"https://www.cursor.com/cn/loginDeepControl?challenge={challenge}&uuid={device_uuid}&mode=login"
    print("请在浏览器中点击 'Yes, Log In' 进行授权...")
    webbrowser.open(auth_url)

    poll_url = f"https://api2.cursor.sh/auth/poll?uuid={device_uuid}&verifier={verifier}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

    for i in range(30):
        print(f"等待授权... ({i + 1}/30)")
        try:
            resp = requests.get(poll_url, headers=headers, timeout=10)

            if resp.status_code == 200 and resp.text:
                data = resp.json()
                access_token = data.get("accessToken")
                auth_id = data.get("authId", "")

                if access_token:
                    user_id = auth_id.split("|")[1] if "|" in auth_id else auth_id
                    return {
                        "userId": user_id,
                        "accessToken": access_token
                    }

        except Exception as e:
            print(f"  错误: {e}")

        time.sleep(2)

    return None


def get_user_email(cookie_encoded):

    url = "https://cursor.com/api/dashboard/get-me"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://cursor.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36",
    }
    cookies = {"WorkosCursorSessionToken": cookie_encoded}

    try:
        resp = requests.post(url, headers=headers, cookies=cookies, json={}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("email")
    except Exception as e:
        print(f"获取用户信息失败: {e}")

    return None


def main():
    print("=" * 50)
    print("Cursor Token 获取工具")
    print("=" * 50)

    # 1. 获取 Token
    result = get_cursor_token()

    if not result:
        print("❌ 获取 Token 失败")
        return

    print(f"\n✅ Token 获取成功!")
    print(f"User ID: {result['userId']}")
    print(f"Access Token: {result['accessToken']}")

    # 2. 生成 URL 编码后的 Cookie
    cookie_value = f"{result['userId']}::{result['accessToken']}"
    cookie_encoded = quote(cookie_value, safe='')

    # 3. 获取 Email
    print(f"\n获取用户信息...")
    email = get_user_email(cookie_encoded)

    if not email:
        print("❌ 获取 Email 失败")
        return

    print(f"✅ Email: {email}")


    # 4. 输出汇总
    print(f"\n{'='*50}")
    print(f"📋 汇总")
    print(f"{'='*50}")
    print(f"Email: {email}")
    print(f"User ID (URL编码): {cookie_encoded}")
    print(f"Access Token: {result['accessToken']}")


if __name__ == "__main__":
    main()