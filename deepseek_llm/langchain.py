from decouple import config
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

def askQuery(query):
    try:
        llm = HuggingFaceEndpoint(
            repo_id="deepseek-ai/deepseek-coder-1.3b-instruct",
            huggingfacehub_api_token=config('HUGGINGFACEHUB_API_TOKEN'),
            temperature=0.1
        )
        
        system_template = """You are a highly skilled AI assistant. 
        Help users with structured, detailed solutions. Ask clarifying questions when needed."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", "{query}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"query": query})
        return response if response else "⚠️ No response received from the AI."
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"