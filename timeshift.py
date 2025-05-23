import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image as PILImage
import time
import datetime

# Load environment variables
load_dotenv()

# Set Streamlit page config
st.set_page_config(
    page_title="TimeShift",
    page_icon="https://i.postimg.cc/bvW0mz3x/Screenshot-2025-05-11-at-2-18-40-pm.png",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling
st.markdown("""
<style>
    body {
        font-family: Helvetica, Arial, sans-serif;
        background-color: #FAF9F6;
        color: #333;
    }
    .stApp, .main .block-container {
        background-color: #FAF9F6;
    }
    h1, h2, h3, .stButton button, .stTextInput input, ul, li, .info-msg, .footer, .year-section, .transform-section {
        font-family: Helvetica, Arial, sans-serif;
    }
    .stButton button {
        background-color: #0056D6;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    /* Remove white container box */
    div[data-testid="stHorizontalBlock"] {
        display: none;
    }
    /* Style the results box */
    .results {
        background-color: white;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #EEEEEE;
    }
    .info-msg {
        background-color: #F7F7F7;
        padding: 1rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        font-size: 0.8rem;
        color: #888;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Show global header image
st.image("https://i.postimg.cc/RZMSph8J/timeshift-logo.png", use_container_width=True)

ACCESS_CODE = os.getenv("ACCESS_CODE")

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

def fetch_timeshift_story(role):
    try:
        api_key = os.getenv("AZURE_OPENAI_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if not api_key or not endpoint or not deployment_name:
            raise ValueError("Missing Azure OpenAI credentials.")

        client = AzureOpenAI(
            api_key=api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=endpoint
        )

        prompt = f"""
Create an eye-opening comparison of a {role}'s work in 1995 vs 2025.

Start with this exact phrase:
"Let's go back to 1995: [choose a nostalgic reference from this list or create a similar one: Windows 95 just launched, the DVD was announced, eBay went live, the first Java version released, Toy Story revolutionized animation, Netscape went public, Amazon was just a book store, 'Macarena' topped the charts, Friends was the hit TV show, or another iconic 1995 moment]"

Then use this exact format:

{role}: 1995 vs 2025

- 1995: **[Insert a major limitation or frustration they faced]**
  2025: **[Insert how this limitation has been completely transformed by technology]**

- 1995: - [A specific task that was manual, time-consuming, or limited in reach]
  2025: - [How this same task is now automated, instant, or global in scale]

- 1995: - [A business challenge that was difficult to overcome]
  2025: - [How new tools and capabilities have made this challenge easily solvable]

- 1995: - [Something that required specialized skills or outsourcing]
  2025: - [How AI or technology now empowers anyone to do this themselves]

The nostalgic pop culture opening is required. Focus on dramatic contrasts that show how much more powerful and effective the role has become.
"""

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"My role is {role}. Generate the 1-minute read as described."}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating comparison. Please try again. Technical details: {str(e)}"

def format_result(text, role):
    # Just return wrapped text since it's already formatted as a 1-minute read
    return f'<div class="transform-section"><p>{text.strip()}</p></div>'

# Initialize variables for role and generate
role = None
generate = False

# =============================
# Login Page
# =============================
if not st.session_state.auth_status:
    st.markdown('<div class="info-msg">Enter your access code to unlock a time capsule revealing how your profession has transformed from 1995 to today. See what\'s now possible that once seemed like science fiction.</div>', unsafe_allow_html=True)
    code_input = st.text_input("Access code:", type="password")
    if st.button("Enter TimeShift", use_container_width=True):
        if code_input == ACCESS_CODE:
            st.session_state.auth_status = True
            st.rerun()
        else:
            st.error("Invalid code")

# =============================
# Main App
# =============================
else:
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Sign Out"):
            st.session_state.auth_status = False
            st.rerun()

    st.markdown('<div class="info-msg">Enter your job role to journey through 30 years of evolution — see how your profession has transformed from 1995 to 2025.</div>', unsafe_allow_html=True)
    
    role = st.text_input("", placeholder="Enter your professional role", label_visibility="collapsed")
    generate = st.button("Generate Comparison", use_container_width=True)

# Initialize request tracking
if "request_tracking" not in st.session_state:
    st.session_state.request_tracking = {}

# Get a unique identifier for the user session
def get_user_identifier():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(time.time()) + str(os.urandom(8).hex())
    return st.session_state.user_id

# Get the current hour (for rate limiting)
def get_current_hour():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H")

# Validate if input is a job role/profession
def is_valid_profession(input_text):
    # Basic validation
    if not input_text or input_text.strip() == "":
        return False
    
    # Input should be reasonably sized (not too short, not too long)
    if len(input_text) < 3 or len(input_text) > 100:
        return False
    
    # Check for excessive special characters or numbers that wouldn't typically be in a profession
    special_char_count = sum(1 for char in input_text if not char.isalnum() and not char.isspace())
    if special_char_count > 3 or special_char_count / len(input_text) > 0.2:
        return False
    
    # Check for excessive numbers (most professions don't have many numbers)
    number_count = sum(1 for char in input_text if char.isdigit())
    if number_count > 2:
        return False
    
    # Check for common non-profession patterns
    non_profession_patterns = [
        "http", "www", "://"  # URLs
    ]
    if any(pattern in input_text.lower() for pattern in non_profession_patterns):
        return False
    
    # Most professions are 1-4 words
    word_count = len(input_text.split())
    if word_count > 6:
        return False
    
    # If the input passes all these checks, we'll consider it a valid profession
    return True

if role and generate:
    # Validate if the input is a profession/job role
    if not is_valid_profession(role):
        st.error("Please enter a valid job role or professional designation. Examples: Software Developer, Marketing Manager, Teacher, Doctor, etc.")
        st.stop()
        
    # Get unique user ID and current hour
    user_id = get_user_identifier()
    current_hour = get_current_hour()
    
    # Initialize user in tracking dict if not present
    if user_id not in st.session_state.request_tracking:
        st.session_state.request_tracking[user_id] = {}
    
    # Count requests in the current hour
    if current_hour in st.session_state.request_tracking[user_id]:
        request_count = st.session_state.request_tracking[user_id][current_hour]
        if request_count >= 1:  # Allow only 1 request per hour per user
            st.warning("You've reached the maximum number of comparisons allowed per hour. Please try again in the next hour.")
            st.stop()
        st.session_state.request_tracking[user_id][current_hour] = request_count + 1
    else:
        # First request in this hour
        st.session_state.request_tracking[user_id][current_hour] = 1
    
    # Clean up old entries (keep only current hour)
    st.session_state.request_tracking[user_id] = {current_hour: st.session_state.request_tracking[user_id].get(current_hour, 0)}
    
    with st.spinner("Hold on, jumping through time from 1995 to 2025... almost ready!"):
        result = fetch_timeshift_story(role)
    st.markdown('<div class="results">', unsafe_allow_html=True)
    st.subheader(f"{role}: 1995 vs 2025")
    st.markdown(format_result(result, role), unsafe_allow_html=True)
    if st.button("Start Over", use_container_width=True):
        st.session_state.role_input = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Global footer displayed for all states
st.markdown('''
<div class="footer">
    Built for fun & learning by <a href="https://ifiecas.com/" target="_blank">Ivy Fiecas-Borjal</a><br>
    Powered by OpenAI's GPT-4o via Azure AI Foundry
</div>
''', unsafe_allow_html=True)
