# -*- coding: utf-8 -*-
"""GroqPDF.ipynb

Automatically generated by Colab.

"""


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq


llm = ChatGroq(temperature=0,
                      model_name="llama3-70b-8192",
                      api_key="",)

embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap=80,length_function=len
)

loader = PDFPlumberLoader("xxx.pdf")
docs = loader.load_and_split()
chunks = text_splitter.split_documents(docs)

vector_store = Chroma.from_documents(documents=chunks, embedding=embedding)

from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate


retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k":10, "score_threshold":0.1}
    )

prompt = PromptTemplate(
    template="""<|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    You are an expert assistant to search the provided context and answer the question.
    If you can't find the answer, just say that you don't know.
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Question: {input}
    Context: {context}
    Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["input"],
)

document_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, document_chain)



question = "is gatsby a criminal?"

result = chain.invoke({"input":question})

print(result["answer"])

#for doc in result["context"]:
#  print("page content: ", doc.page_content)
