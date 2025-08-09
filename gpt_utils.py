
import openai
import os

def ask_gpt(prompt):
    """
    Simple function to interact with OpenAI's API
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "Please configure your OpenAI API key in the environment variables."
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"
