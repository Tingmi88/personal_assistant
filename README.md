# AI NLP 第六期

# 图书推荐助手

本应用使用LlamaIndex基于用户输入推荐图书。该应用通过Streamlit部署。

## 概述

图书推荐助手是一个基于RAG（检索增强生成）的应用，帮助用户发现符合其兴趣的图书。系统使用向量嵌入来根据流派、作者或主题偏好找到语义相似的图书。

## 功能特点

- 基于用户输入的自然语言图书推荐
- 使用向量相似度搜索进行语义匹配
- 易于使用的Streamlit界面
- 由LlamaIndex和Hugging Face嵌入技术提供支持

## 使用方法

1. 在输入框中输入图书流派、作者或主题
2. 点击"获取推荐"
3. 应用会根据您的输入提供推荐图书
4. 探索推荐结果，发现您的下一本好书！

## 安装步骤

1. 克隆此仓库：
   ```
   git clone <repository-url>
   cd book-recommendation-agent
   ```

2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # Windows系统: venv\Scripts\activate
   ```

3. 安装所需的包：
   ```
   pip install -r requirements.txt
   ```

4. 设置环境变量：
   - 在项目根目录创建`.env`文件
   - 添加您的OpenAI API密钥：`OPENAI_API_KEY=your_api_key_here`

## 运行应用

启动Streamlit应用：

```
streamlit run streamlit_app.py
```

## 依赖要求

应用依赖以下包：
- streamlit
- llama-index
- llama-index-llms-groq
- llama-index-embeddings-huggingface
- llama-index-tools-google
- pandas
- python-dotenv

## 数据

应用使用存储在`data/books.csv`的图书数据集。CSV文件至少应包含：
- id
- title (标题)
- authors (作者)

## 贡献

欢迎贡献！请随时提交拉取请求。