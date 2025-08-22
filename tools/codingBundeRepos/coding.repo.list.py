import http.client
import json
import os
import sys
from typing import Dict, Any


def get_api_token() -> str:
    """从环境变量获取API令牌，如果不存在则提示用户"""
    token = os.environ.get("CODING_API_TOKEN")
    if not token:
        print("错误: 未设置CODING_API_TOKEN环境变量")
        print("请设置环境变量: CODING_API_TOKEN=your_token")
        sys.exit(1)
    return token


def fetch_coding_user_info() -> Dict[str, Any]:
    """获取Coding用户信息"""
    try:
        conn = http.client.HTTPSConnection("e.coding.net", timeout=10)
        payload = json.dumps({})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_api_token()}",
        }
        
        # 使用正确的API路径
        conn.request(
            "POST", "/open-api/?action=DescribeCodingCurrentUser", payload, headers
        )
        
        res = conn.getresponse()
        data = res.read()
        
        if res.status != 200:
            print(f"API请求失败: HTTP {res.status} - {res.reason}")
            return {"error": f"HTTP {res.status}", "message": res.reason}
            
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return {"error": "JSON解析错误", "message": str(e)}
    except http.client.HTTPException as e:
        print(f"HTTP连接错误: {e}")
        return {"error": "HTTP连接错误", "message": str(e)}
    except Exception as e:
        print(f"发生未知错误: {e}")
        return {"error": "未知错误", "message": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    result = fetch_coding_user_info()
    print(json.dumps(result, ensure_ascii=False, indent=2))
