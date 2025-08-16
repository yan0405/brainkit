from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import openai
from openai import OpenAI


def load_and_chunk_markdown(file_path, split_mode="paragraph", min_length=20):
    """
    读取 markdown 文件，并进行简单拆分
    参数：
        file_path: 文件路径
        split_mode: 拆分方式，可选 'paragraph' 或 'line'
        min_length: 最小 chunk 长度，过短的会被丢弃
    返回：
        List[str] 拆分后的文本块
    """
    # 读取文件内容
    text = Path(file_path).read_text(encoding="utf-8")

    # 按段落拆分（双换行），也可以选按行拆
    if split_mode == "paragraph":
        raw_chunks = text.split("\n\n")
    elif split_mode == "line":
        raw_chunks = text.split("\n")
    else:
        raise ValueError("Invalid split_mode. Use 'paragraph' or 'line'.")

    # 清理 + 过滤
    chunks = [
        chunk.strip()
        for chunk in raw_chunks
        if len(chunk.strip()) >= min_length
    ]

    return chunks


def embed_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    """
    对文本块进行向量化
    参数：
        chunks: List[str]，之前切分的文本段
        model_name: 使用的 embedding 模型
    返回：
        embeddings: numpy.ndarray
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings


def build_faiss_index(embeddings):
    """
    构建 FAISS 向量索引
    参数：
        embeddings: numpy.ndarray [num_chunks, dim]
    返回：
        FAISS 索引对象
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  # 使用 L2 距离（欧氏距离）
    index.add(np.array(embeddings))
    return index


def search_top_k(index, query, embed_fn, top_k=3):
    """
    给定用户查询，返回最相关的 chunk 索引和相似度
    """
    query_vec = embed_fn([query])
    distances, indices = index.search(np.array(query_vec), top_k)
    return indices[0], distances[0]


def generate_answer_from_chunks(query, retrieved_chunks, model="gpt-3.5-turbo"):
    """
    使用 OpenAI GPT-3.5/4 (新版SDK) 生成回答
    """
    prompt = (
        "你是一个交易策略顾问，请结合以下知识内容，回答用户提出的问题。\n\n"
        + "相关资料如下：\n"
        + "\n".join(f"- {chunk}" for chunk in retrieved_chunks)
        + f"\n\n问题：{query}\n\n请给出详细建议："
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个非常理性的交易顾问。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# 示例调用
file_path = "../quick_poc/brain_store/secondme.md"
chunks = load_and_chunk_markdown(file_path)
embeddings = embed_chunks(chunks)
model = SentenceTransformer("all-MiniLM-L6-v2")
index = build_faiss_index(embeddings)
# 保存索引（可选）
faiss.write_index(index, "./brain_store/knowledge_index.faiss")

client = OpenAI(api_key="")
# print(f"嵌入维度：{embeddings}")
# # 输出前几个看看
# for i, chunk in enumerate(chunks[:5]):
#     print('======')
#     print(f"Chunk {i+1}:\n{chunk}\n")

# 1. 用户提问
query = "告诉我什么是secondMe, 该怎么建立一个secondMe的应用？"

# 2. 检索相关 chunk
indices, _ = search_top_k(index, query, model.encode, top_k=3)
retrieved_chunks = [chunks[i] for i in indices]

# 3. GPT 回答
answer = generate_answer_from_chunks(
    query, retrieved_chunks, model="gpt-3.5-turbo")
print("💬 GPT 回答：\n", answer)
