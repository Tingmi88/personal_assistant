# NLP-GENAI-第六期-RAGs

This repo is a modified version of:

https://github.com/run-llama/rags

RAGs is a Streamlit app that lets you create a RAG pipeline from a data source using natural language.

You get to do the following:
1. Describe your task (e.g. "load this web page") and the parameters you want from your RAG systems (e.g. "i want to retrieve X number of docs")
2. Go into the config view and view/alter generated parameters (top-k, summarization, etc.) as needed.
3. Query the RAG agent over data with your questions.

Reference: [GPTs](https://openai.com/blog/introducing-gpts), launched by OpenAI.

### 1. Install dependencies
```commandline
pip install -r requirements.txt
```
### 2. In the main directory, create and set up api keys in .streamlit/secrets
```commandline
[nyt]
api_key=xxx

[WEATHERSTACK_API_KEY]
api_key=yyy

openai_key=zzz
```

### 3. Initiate the app (--title and --city are both optional)
```commandline 
streamlit run 1_🏠_Home.py -- --title "Hello, your_name" --city "your_city_name"

```

