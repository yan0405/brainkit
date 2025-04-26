# upload_download_local_ipfs.py (demo version - file paths hardcoded)

import ipfshttpclient
import os

# --- 配置 ---
UPLOAD_FILE_PATH = "./keystore/encrypted_faiss.bin"
DOWNLOAD_SAVE_PATH = "./dl/copied_encrypted_faiss.bin"

# 连接到本地 IPFS 节点
client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')


def upload_to_local_ipfs(file_path: str) -> str:
    res = client.add(file_path)
    cid = res['Hash']
    print(f"✅ Uploaded to Local IPFS!")
    print(f"📦 CID: {cid}")
    print(f"🔗 Local Gateway URL: http://127.0.0.1:8080/ipfs/{cid}")
    return cid


def download_from_local_ipfs(cid: str, save_path: str):
    content = client.cat(cid)
    # print(content)
    with open(save_path, 'wb') as f:
        f.write(content)
    print(f"✅ Downloaded successfully and saved to {save_path}")


if __name__ == "__main__":
    if not os.path.isfile(UPLOAD_FILE_PATH):
        print(f"❌ Upload file not found: {UPLOAD_FILE_PATH}")
    else:
        cid = upload_to_local_ipfs(UPLOAD_FILE_PATH)
        download_from_local_ipfs(cid, DOWNLOAD_SAVE_PATH)
