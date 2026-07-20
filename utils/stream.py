def stream_text(stream):
        """LangChain's llm.stream() yields AIMessageChunk objects, not raw
        strings. st.write_stream needs plain strings, so unwrap .content here."""
        for chunk in stream:
            if chunk.content:
                yield chunk.content