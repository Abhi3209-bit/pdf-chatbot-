from langchain_core.messages import HumanMessage


def rewrite_query(llm, history, query):
    """
    Rewrites the user's latest question into a standalone question
    using the recent conversation history.

    Parameters
    ----------
    llm : ChatGoogleGenerativeAI
        Gemini model instance.

    history : list
        Previous chat messages from session state.

    query : str
        Current user question.

    Returns
    -------
    str
        Standalone rewritten question.
    """

    conversation = ""

    for message in history:

        role = message["role"].capitalize()

        conversation += f"{role}: {message['content']}\n"

    prompt = f"""
You are an expert query rewriting assistant for a FANUC CNC chatbot.

Your task is ONLY to rewrite the user's latest question into a complete standalone question.

Use the previous conversation only to resolve references such as:

- it
- its
- this
- that
- these
- those
- they
- them
- he
- she
- previous parameter
- previous alarm

Rules:

1. Do NOT answer the question.
2. Do NOT add extra information.
3. If the question is already complete, return it unchanged.
4. Return ONLY the rewritten question.

Conversation:
{conversation}

Current Question:
{query}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content.strip()