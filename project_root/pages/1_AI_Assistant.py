import streamlit as st

# Set the page configuration (optional, but good practice)
st.set_page_config(page_title="Streamlit Chatbot", page_icon="🤖")

st.title("Echo Bot Assistant")
st.markdown("*A basic chat interface using Streamlit.*")

# --- Initialize Chat History ---
# Messages are stored in st.session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a starting message from the assistant
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am the Echo Bot. How can I help you today?"})

# --- Display Chat Messages ---
# Loop through the history and display each message
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
# Use the walrus operator (:=) to assign and check the prompt
if prompt := st.chat_input("Say something..."):
    
    # 1. Display user message and add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. **Integrate LLM Response Logic Here**
    # --- Start of LLM Integration Block ---
    
    # In a real app, you would call your LLM function here.
    # For this echo example, the response is just the prompt.
    response = f"Echo: {prompt}"
    
    # Example of a function call:
    # with st.spinner("AI is thinking..."):
    #     response = generate_llm_response(prompt, st.session_state.messages)

    # --- End of LLM Integration Block ---

    # 3. Display assistant response and add to history
    with st.chat_message("assistant"):
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})