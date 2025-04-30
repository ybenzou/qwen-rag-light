# 🔍 Local RAG Framework using Qwen API

本项目是一个基于 [Qwen](https://qwen.aliyun.com/) 的本地轻量级 RAG（检索增强生成）系统，支持：

- ✅ 从 `.txt`、`.pdf`、`.md`、`.docx` 文档中提取内容
- ✅ 使用 Qwen 的 text-embedding-v1 进行向量嵌入
- ✅ 向量检索 + Qwen Turbo 生成回答
- ✅ Vue3 前端支持输入 API Key 和 Query，展示回答与参考内容
- ✅ 嵌入与查询流程完全分离，便于快速部署

---

## 🚀 快速开始（开发者指南）

### ✅ 1. 克隆项目
```bash
git clone https://github.com/yourname/rag-local-qwen.git
cd rag-local-qwen
```

---

### ✅ 2. 准备文档
将你的 `.txt`、`.pdf`、`.md`、`.docx` 文档放入：
```bash
rag-local-qwen/docs/
```

---

### ✅ 3. 预处理文档嵌入（仅需执行一次）
```bash
cd backend
DASHSCOPE_API_KEY=sk-xxx python embed_documents.py
```
将生成：
```
cache/
├── chunks.json    ← 所有文本段
└── vectors.npy     ← 文本段向量
```

---

### ✅ 4. 启动后端服务
```bash
uvicorn main:app --reload
```
默认地址为：`http://localhost:8000`

---

### ✅ 5. 启动前端页面
```bash
cd ../frontend
npm install
npm run dev
```
默认地址为：`http://localhost:5173`

---

## 💡 使用说明

1. 打开浏览器访问 `http://localhost:5173`
2. 输入你的 DashScope API Key
3. 输入问题（query）点击提交
4. 系统将自动：
   - 读取缓存向量
   - 对 Query 向量化
   - 检索最相关文段
   - 将其交给 Qwen Turbo 回答
5. 页面将展示回答内容和被参考的文段（含来源）

---

## 📁 项目结构
```
rag-local-qwen/
├── docs/             ← 文档目录
├── cache/            ← 嵌入向量缓存（自动生成）
├── backend/
│   ├── embed_documents.py  ← 嵌入生成器
│   └── main.py             ← FastAPI 查询服务
├── frontend/         ← Vue3 + Tailwind 前端
```

---

## 🛠️ 安装依赖（后端）
```bash
pip install -r requirements.txt
# 或手动安装：
pip install openai tqdm numpy python-docx PyMuPDF
```

---

## 📦 安装依赖（前端）
```bash
npm install
```

---

## 📄 License
MIT

