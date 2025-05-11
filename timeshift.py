import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image as PILImage

# Load environment variables
load_dotenv()

# Set Streamlit page config
st.set_page_config(
    page_title="TimeShift",
    page_icon="⏳",
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
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #EEEEEE;
        margin-bottom: 1rem;
    }
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
st.image("https://i.postimg.cc/prBVFzQT/TIME-1.png", use_container_width=True)

ACCESS_CODE = "swo"

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

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": f"""You are a tech historian specializing in enterprise software evolution who creates highly customized comparisons between 1995 and 2025 specifically for the role of \"{role}\"."""},
                {"role": "user", "content": f"My role is {role}. Please compare how it evolved from 1995 to 2025."}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating comparison. Please try again. Technical details: {str(e)}"

def format_result(text, role):
    formatted = ""

    # Extract transformation blurb
    if "Impossible Then, Possible Now:" in text:
        parts = text.split("Impossible Then, Possible Now:")
        blurb = parts[1].strip().split("1995:")[0].strip()
        formatted += f'<div class="transform-section"><strong>What\'s Impossible in 1995, Now Possible in 2025 for {role}s:</strong><p>{blurb}</p></div>'
        text = "1995:" + text.split("1995:")[1]

    # Extract 3 most critical differences
    if "1995:" in text and "2025:" in text:
        year_1995 = text.split("1995:")[1].split("2025:")[0].strip().splitlines()
        year_2025 = text.split("2025:")[1].strip().splitlines()

        combined_points = list(zip(year_1995, year_2025))
        combined_points = [pair for pair in combined_points if pair[0].strip() and pair[1].strip()][:3]  # Get top 3 pairs

        formatted += '<div class="year-section"><ul>'
        for before, after in combined_points:
            formatted += f'<li><strong>1995:</strong> {before.strip()}<br><strong>2025:</strong> {after.strip()}</li>'
        formatted += '</ul></div>'

    else:
        formatted += f'<div>{text}</div>'

    return formatted

# =============================
# Login Page
# =============================
if not st.session_state.auth_status:
    st.markdown('<div class="info-msg">Enter access code to discover how job roles and skills have shifted.</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="info-msg">Enter your job role in enterprise software to see how it changed from 1995 to 2025.</div>', unsafe_allow_html=True)
    role = st.text_input("What's your professional role?", placeholder="Enter your role/designation")
    generate = st.button("Generate Comparison", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if role and generate:
        with st.spinner("Generating comparison..."):
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
