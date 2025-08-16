# upload_download_pinata.py


import os
import requests

# Load JWT from environment variable
# PINATA_JWT = os.getenv("PINATA_JWT")
PINATA_JWT = ""
if not PINATA_JWT:
    raise ValueError("Please set the PINATA_JWT environment variable.")

HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}"
}


def upload_file_to_pinata(file_path: str) -> str:
    """
    Uploads a file to Pinata and returns the IPFS CID.
    """
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(
            "https://api.pinata.cloud/pinning/pinFileToIPFS",
            headers=HEADERS,
            files=files
        )
    if response.status_code == 200:
        cid = response.json()['IpfsHash']
        print(f"✅ Uploaded to Pinata! CID: {cid}")
        print(f"🔗 IPFS URL: https://gateway.pinata.cloud/ipfs/{cid}")
        return cid
    else:
        raise Exception(
            f"Upload failed: {response.status_code} {response.text}")


def download_file_from_ipfs(cid: str, save_path: str):
    """
    Downloads a file from IPFS via Pinata's gateway using the provided CID.
    """
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded successfully and saved to {save_path}")
    else:
        raise Exception(
            f"Download failed: {response.status_code} {response.text}")


# Example usage
if __name__ == "__main__":
    # Upload
    cid = upload_file_to_pinata("./keystore/encrypted_faiss.bin")

    # Download (optional testing)
    download_file_from_ipfs(cid, "downloaded_encrypted_faiss.bin")
