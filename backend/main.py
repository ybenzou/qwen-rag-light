from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os, json
import numpy as np
from functools import lru_cache

# === 路径设置 ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CHUNKS_FILE = os.path.join(CACHE_DIR, "chunks.json")
VEC_FILE = os.path.join(CACHE_DIR, "vectors.npy")

# === App 初始化 ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 工具函数 ===
@lru_cache
def init_client(api_key: str):
    return OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

def load_cache():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load(VEC_FILE)
    return chunks, vectors

def cosine_sim(a: np.ndarray, b: np.ndarray):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

# === 接口 ===
@app.post("/api/query")
async def rag_query(request: Request):
    data = await request.json()
    api_key = data.get("api_key", "").strip()
    query = data.get("query", "").strip()

    if not api_key or not query:
        return {"answer": "❌ 缺少 API Key 或 Query", "references": []}

    client = init_client(api_key)

    try:
        # 加载缓存
        chunks, vectors = load_cache()
        if not chunks or len(vectors) == 0:
            return {"answer": "❌ 无嵌入缓存，请先运行 embed_documents.py", "references": []}

        # query 向量
        resp = client.embeddings.create(model="text-embedding-v1", input=[query])
        query_vec = np.array(resp.data[0].embedding)

        # 相似度检索
        sims = [cosine_sim(query_vec, np.array(v)) for v in vectors]
        top_idxs = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:5]

        top_refs = [chunks[i] for i in top_idxs]
        context = "\n\n".join([r["text"] for r in top_refs])

        # 调用 Qwen 生成回答
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": "你是一位根据提供文档回答问题的专家，如无明确答案请直接说不知道"},
                {"role": "user", "content": f"以下是参考内容：\n{context}\n\n问题：{query}"}
            ]
        )

        return {
            "answer": completion.choices[0].message.content,
            "references": top_refs
        }

    except Exception as e:
        return {"answer": f"❌ 请求失败: {str(e)}", "references": []}
