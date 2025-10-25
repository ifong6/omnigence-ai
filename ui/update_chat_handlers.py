import streamlit as st
import requests


def handle_chat_submit(user_input: str):
    """Handle chat submission and API interaction"""
    if not user_input.strip():
        st.warning("Please enter a message")
        return

    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Show processing message
    with st.spinner("AI代理正在處理您的請求..."):
        request_url = "http://localhost:8000/call-main-flow"

        try:
            response = requests.post(
                url=request_url,
                json={
                    "message": user_input,
                    "session_id": st.session_state.session_id
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

            response_data = response.json() 

            if response.status_code == 200:
                if response_data.get("status") == "interrupt":
                    # Handle interrupt response (form needed)
                    interrupt_data = response_data.get("result", {})

                    # Add AI response to chat history
                    ai_message = interrupt_data.get("message", "I'll help you with that.")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_message})

                    # Show the message in chat
                    st.success(ai_message)

                    # Update session state to show form
                    if interrupt_data.get("show_quote_form"):
                        st.session_state.show_quote_form = True
                        st.session_state.quotation_data = interrupt_data.get("quotation_data")
                        st.session_state.next_step = interrupt_data.get("next_step")

                elif response_data.get("status") == "success":
                    # Handle successful completion
                    result = response_data.get("result", {})
                    ai_message = result.get("message", "Task completed successfully.")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_message})
                    st.success(ai_message)

                else:
                    st.error(f"Unexpected response: {response_data}")

            else:
                st.error(f"Server error: {response.status_code}")

        except Exception as e:
            st.error(f"Failed to communicate with AI agent: {str(e)}")
            print(f"Error details: {e}")



