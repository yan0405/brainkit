# 🧠 CyberBrain

> 把你的 RAG（向量知识库）做成**可拥有、可授权、可交易**的数字资产。  
> 通过 **AES + Proxy Re‑Encryption (pyUmbral)** 加密与授权，结合 **IPFS** 存储，并以 **ERC‑721（NFT）** 承载所有权/元数据：**NFT = 拥有权；PRE = 使用权**。

**[English](README.md)** | **简体中文**

## 🧠 一句话
**NFT 承载拥有权，PRE 掌握使用权。**  
**Mint your knowledge; keep decryption power in your own hands.**

![System Overview](system_overview.jpg)

---

## ✨ 核心要点
- 🔒 **内容始终加密**：RAG（如 `.faiss`）先用 AES 加密，再用 PRE 封装 AES 密钥  
- 🗝️ **细粒度授权**：对接收者（Bob）生成 kfrags → 代理重加密 → 本地解密可用  
- 🌐 **本地/托管 IPFS**：可使用本地离线节点或 Pinata 等托管服务  
- 🪙 **ERC‑721（NFT）**：NFT 承载 CID/元数据；**不**包含明文与密钥  
- 🤖 **即插即用**：解密后的 RAG 可直接给 LLM/Agent 检索使用（LangChain/LlamaIndex/自研皆可）

---

## 📂 当前目录结构
```
.
├─ brain_store/
│  ├─ knowledge_index.faiss         # 明文向量库（示例）
│  └─ secondme.md                   # 示例文档
├─ dl/
│  └─ copied_encrypted_faiss.bin    # 示例/拷贝的密文
├─ ipfs_local_node/
│  └─ docker-compose.yaml           # 本地离线 IPFS 节点（可选）
├─ keystore/                        # 授权/密钥材料（⚠️ 建议 gitignore）
│  ├─ alice_pk.key / alice_sk.key / alice_sign.key
│  ├─ bob_pk.key   / bob_sk.key   / bob_sign.key
│  ├─ capsule.bin                  # Umbral capsule（密钥封装）
│  ├─ encrypted_aes.key            # Umbral 加密过的 AES 密钥
│  └─ encrypted_faiss.bin          # AES 加密后的 .faiss 密文
├─ .gitignore
├─ downloaded_encrypted_faiss.bin   # 从 IPFS 下载的密文（示例）
├─ knowledge_processing.py          # 知识处理/切分/向量化（示例）
├─ knowledge_protection.py          # AES + Umbral PRE 加密/授权/解密（PoC 主流程）
├─ knowledge_store.py               # 通过 Pinata 上传并用 CID 下载
├─ local_knowledge_store.py         # 本地 IPFS 存取（可选）
└─ README.zh-CN.md
```

---

## 🚀 快速演示（End‑to‑End）

### 1) 准备 RAG 索引
把你的文件放到 `/brain_store/`，例如：
```
./brain_store/secondme.md
```
运行 `knowledge_processing.py` 将内容转换为 FAISS 索引（输出：`brain_store/knowledge_index.faiss`）。

### 2) 加密 & 生成授权材料（PRE）
运行 PoC 主流程：
```bash
python knowledge_protection.py
```
将会生成：
- `keystore/encrypted_faiss.bin`（AES 密文）
- `keystore/encrypted_aes.key`、`keystore/capsule.bin`
- Alice/Bob 的密钥材料（`*_sk.key / *_pk.key / *_sign.key`）

### 3) 上传密文到 IPFS，并通过 CID 下载
```bash
python knowledge_store.py
```
脚本会通过 **Pinata** 上传至 IPFS 并返回 **CID**，随后按 CID 再下载进行校验。

### 4) 授权解密（给持有人）
- Alice 为 Bob 生成 `kfrags`，代理重加密得到 `cfrags`  
- Bob 使用 `cfrags + capsule + encrypted_aes.key` 恢复 AES 密钥  
- 本地解密 `encrypted_faiss.bin`，得到明文 `.faiss`，即可作为 RAG 数据源给 LLM/Agent 使用

---

## 🪙 与 ERC‑721（NFT）（TODO）
- **NFT 承载所有权与元数据**（如 `name/description/properties/cid/format/version`）  
- **不包含明文与密钥**；使用权由 **PRE** 独立控制  
- 建议提供 `metadata.json` 示例与最小 ERC‑721 合约/铸造脚本（本地链/测试网）

---

## 🛣️ Roadmap
- [ ] 最小 ERC‑721 合约与铸造脚本（本地链/测试网）  
- [ ] 授权自动化（监听 NFT 转移 → 触发 PRE 发放/撤销）  
- [ ] 多知识库/多租户编排（批量授权）  
- [ ] 本地 Web 控制台（管理 CID/授权/下载/解密）  
- [ ] 审计与日志（解密事件记录、可选上链）

---

## 🤝 参与贡献
欢迎对本项目感兴趣的开发者提交 PR。  
提交 PR 时，请说明修改动机、设计思路与测试点。

---

## 📄 License
建议使用 **MIT** 或 **Apache‑2.0**（按你的偏好）。请在 `LICENSE` 中注明。

---

## 🙏 Acknowledgements
- [pyUmbral (NuCypher)](https://github.com/nucypher/pyUmbral)  
- [IPFS](https://ipfs.tech/)  
- [FAISS](https://github.com/facebookresearch/faiss)
