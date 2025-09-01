from openai import OpenAI

# ! Setup
API_KEY = "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"

client = OpenAI(api_key=API_KEY)

# ! Chatgpt get answers function with context
def get_gpt_response(prompt: str, context: str = "") -> str:
    # Build the system message with context
    system_message = "You are Alfredo, a helpful smart mirror assistant, you're very positive, the user is called Daniel and built you, you never use emojis. Continue the conversation naturally."
    
    messages = [
        {"role": "system", "content": system_message},
    ]
    
    # Add context if available
    # * will get the context from the frontend by doing a get request 
    if context: 
        # Parse the context string and add to messages
        context_entries = context.split(' - ') 
        for entry in context_entries:
            if entry.startswith('User: '):
                messages.append({"role": "user", "content": entry[6:]})  # Remove 'User: ' prefix
            elif entry.startswith('Assistant: '):
                messages.append({"role": "assistant", "content": entry[11:]})  # Remove 'Assistant: ' prefix
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    return response.choices[0].message.content

# ! Chatgpt get emotion function (unchanged)
def get_emotion(text: str) -> str:
    emotion_prompt = f"Classify the emotion of this text in one word (happy, sad, angry, excited, neutral):\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": emotion_prompt},
        ]
    )
    return response.choices[0].message.content.strip().lower()