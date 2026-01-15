from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo")

def main():

    input_question = """
    What is the capital of Germany?
    """

    template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human", "{question}"),
        ]
    )

    chain = template | model 

    response = chain.invoke({"question": input_question})

    print(response.content)

if __name__ == "__main__":
    main()
