# CSS styles for the Streamlit Quote & Invoice App
CUSTOM_STYLES = """
    <style>
    .stMainBlockContainer {
        max-width: 1024px;
    }
    .chat-message {
        padding: 10px;
        margin: 5px;
        border-radius: 10px;
    }
    .agent-message {
        background-color: #f0f0f0;
    }
    .user-message {
        background-color: #e1f5fe;
    }
    .timestamp {
        font-size: 0.8em;
        color: #666;
    }
    .chat-container {
        height: 0px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
        background-color: white;
    }
    .stButton > button {
        height: 38px;
        padding: 0 20px;
    }
    .stTextInput > div > div > input {
        height: 38px;
    }
    .approve-button {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    .control-buttons {
        margin-top: 10px;
    }
    div[data-testid="column"] {
        display: flex;
        align-items: flex-end;
        padding-bottom: 1rem;
    }
    .stButton {
        width: 100%;
    }
    </style>
"""

SIDEBAR_STYLE = """
<style>
[data-testid="stSidebar"] {
    background-color: #e6f3ff;
}
</style>
"""

BUTTON_STYLE = """
<style>
/* Custom styling for submit button (sky blue) */
.stForm .stButton > button {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    transition: all 0.3s ease;
}
.stForm .stButton > button:hover {
    background-color: #357abd;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
"""

CUSTOM_BUTTON_STYLE = """
<style>
.custom-button {
    background-color: #4a90e2;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}
.custom-button:hover {
    background-color: #357abd;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
"""

TEXT_INPUT_STYLE = """
<style>
/* Custom styling for text input area */
.stTextInput > div > div > input {
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    transition: all 0.3s ease;
    background-color: #fafbfc;
}

.stTextInput > div > div > input:focus {
    border-color: #4a90e2;
    box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
    background-color: white;
}

.stTextInput > div > div > input:hover {
    border-color: #b8c5d1;
    background-color: white;
}

/* Label styling */
.stTextInput > label {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 14px;
}
</style>
"""

TEXT_AREA_STYLE = """
<style>
/* Custom styling for text area */
.stTextArea > div > div > textarea {
    border: 2px solid #e1e5e9 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
    background-color: #fafbfc !important;
    resize: none !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #4a90e2 !important;
    box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1) !important;
    background-color: white !important;
}

.stTextArea > div > div > textarea:hover {
    border-color: #b8c5d1 !important;
    background-color: white !important;
}

/* Text area label styling */
.stTextArea > label {
    font-weight: 600 !important;
    color: #2c3e50 !important;
    margin-bottom: 8px !important;
    font-size: 14px !important;
}
</style>
"""

DIVIDER = """
    <div style="height: 2px; background: #e0e0e0; margin: 20px 0;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 5px;"></div>
"""

def apply_styles():
    """Apply all CSS styles to the Streamlit app"""
    import streamlit as st
    
    # Apply sidebar style
    st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)
    
    # Apply button style
    st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
    
    # Apply text input style
    st.markdown(TEXT_INPUT_STYLE, unsafe_allow_html=True)
    
    # Apply text area style
    st.markdown(TEXT_AREA_STYLE, unsafe_allow_html=True)
    
    # Apply custom button style
    st.markdown(CUSTOM_BUTTON_STYLE, unsafe_allow_html=True)
