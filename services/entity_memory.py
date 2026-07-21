import re
import streamlit as st


def initialize_entity_memory():
    """
    Creates entity memory when the app starts.
    """

    if "entity_memory" not in st.session_state:

        st.session_state.entity_memory = {
            "current_parameter": None,
            "current_alarm": None,
            "current_topic": None,
            "current_page": None,
        }


def update_entity_memory(query: str):
    """
    Extract important entities from the user's question.
    """

    memory = st.session_state.entity_memory

    # -----------------------------
    # FANUC Parameter
    # -----------------------------
    parameter = re.search(
        r"\bparameter\s*(\d{3,4})\b",
        query,
        re.IGNORECASE,
    )

    if parameter:

        memory["current_parameter"] = parameter.group(1)

        memory["current_topic"] = "parameter"

    # -----------------------------
    # Alarm
    # -----------------------------
    alarm = re.search(
        r"\balarm\s*(\d{3,4})\b",
        query,
        re.IGNORECASE,
    )

    if alarm:

        memory["current_alarm"] = alarm.group(1)

        memory["current_topic"] = "alarm"


def get_entity_memory():

    return st.session_state.entity_memory