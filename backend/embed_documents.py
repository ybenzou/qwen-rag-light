import os, glob, fitz, json
import docx
import numpy as np
from tqdm import tqdm
from openai import OpenAI

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def extract_docx_text(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def split_and_store(text, source, chunks):
    text = text.strip()
    if len(text) < 20:
        return
    if len(text) < 300:
        chunks.append({"text": text, "source": source})
    else:
        for i in range(0, len(text), 300):
            chunk = text[i:i+300].strip()
            if chunk:
                chunks.append({"text": chunk, "source": source})

def get_all_chunks():
    chunks = []

    for path in glob.glob(os.path.join(DOCS_DIR, "*.txt")):
        with open(path, "r", encoding="utf-8") as f:
            split_and_store(f.read(), os.path.basename(path), chunks)

    for path in glob.glob(os.path.join(DOCS_DIR, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            split_and_store(f.read(), os.path.basename(path), chunks)

    for path in glob.glob(os.path.join(DOCS_DIR, "*.docx")):
        text = extract_docx_text(path)
        split_and_store(text, os.path.basename(path), chunks)

    for path in glob.glob(os.path.join(DOCS_DIR, "*.pdf")):
        pdf = fitz.open(path)
        for page_num, page in enumerate(pdf):
            text = page.get_text()
            split_and_store(text, f"{os.path.basename(path)} page {page_num+1}", chunks)

    return chunks

def main():
    print("📄 正在提取文档片段...")
    chunks = get_all_chunks()
    print(f"✅ 提取 {len(chunks)} 个段落")

    print("🔗 正在生成嵌入向量...")
    vectors = []
    for c in tqdm(chunks):
        resp = client.embeddings.create(model="text-embedding-v1", input=[c["text"]])
        vectors.append(resp.data[0].embedding)

    print("💾 正在保存缓存...")
    with open(os.path.join(CACHE_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    np.save(os.path.join(CACHE_DIR, "vectors.npy"), np.array(vectors))
    print("✅ 完成！嵌入向量缓存已保存")

if __name__ == "__main__":
    main()
