import streamlit as st
from openai import AzureOpenAI
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image as PILImage

# Load environment variables
load_dotenv()

# Function to load image from URL
def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = PILImage.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# Set Streamlit page config
st.set_page_config(
    page_title="TimeShift",
    page_icon="⏳",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS styling with Helvetica font
st.markdown("""
<style>
    /* Typography using Helvetica */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    body {
        font-family: Helvetica, Arial, sans-serif;
        color: #333;
        background-color: #FAF9F6;
    }
    
    /* Header image styling */
    .header-image {
        width: 100%;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    /* Minimalist header styling */
    h1 {
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 500;
        color: #333;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    h2, h3 {
        font-family: Helvetica, Arial, sans-serif;
        color: #333;
        font-weight: 500;
        font-size: 1.5rem;
        margin-top: 1.5rem;
    }
    
    /* Clean button styling */
    .stButton button {
        font-family: Helvetica, Arial, sans-serif;
        background-color: #0056D6;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 400;
        box-shadow: none;
    }
    
    /* Minimal input styling */
    .stTextInput input {
        font-family: Helvetica, Arial, sans-serif;
        border-radius: 4px;
        border: 1px solid #E0E0E0;
        padding: 0.5rem;
        background-color: #FAFAFA;
    }
    
    /* Clean card styling */
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #EEEEEE;
        margin-bottom: 1rem;
    }
    
    /* Results styling */
    .results {
        background-color: white;
        padding: 1.5rem;
        border-radius: 4px;
        margin-top: 1rem;
        border: 1px solid #EEEEEE;
    }
    
    /* Info message styling */
    .info-msg {
        font-family: Helvetica, Arial, sans-serif;
        background-color: #F7F7F7;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    /* Footer styling */
    .footer {
        font-family: Helvetica, Arial, sans-serif;
        margin-top: 3rem;
        text-align: center;
        font-size: 0.8rem;
        color: #888;
        padding-bottom: 1rem;
    }
    
    /* Comparison sections */
    .year-section {
        font-family: Helvetica, Arial, sans-serif;
        padding: 1rem 0;
        border-bottom: 1px solid #EEEEEE;
    }
    
    .transform-section {
        font-family: Helvetica, Arial, sans-serif;
        padding: 1rem 0;
        background-color: #F8F8F8;
        border-left: 3px solid #0056D6;
        padding-left: 1rem;
        margin-top: 1rem;
    }
    
    /* Bullet point styling */
    ul {
        font-family: Helvetica, Arial, sans-serif;
        padding-left: 1.2rem;
        margin-top: 0.5rem;
    }
    
    li {
        font-family: Helvetica, Arial, sans-serif;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .card, .results {
            padding: 1rem;
        }
    }
    
    /* Override all text with Helvetica */
    * {
        font-family: Helvetica, Arial, sans-serif !important;
    }
    
    /* Set the background color for the entire app */
    .stApp {
        background-color: #FAF9F6;
    }
    
    /* Ensure background color is consistent */
    .main .block-container {
        background-color: #FAF9F6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

# Add session state for role input
if "role_input" not in st.session_state:
    st.session_state.role_input = ""

# Constants
ACCESS_CODE = "swo"

def fetch_timeshift_story(role):
    """Fetch comparison from Azure OpenAI"""
    try:
        # Azure OpenAI client setup - Updated to fix proxies error
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            # Removed any potential proxy settings that might be causing issues
        )
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # API call with context about enterprise software reselling and dynamic role-based content
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": f"""You are a tech historian specializing in enterprise software evolution who creates highly customized comparisons between 1995 and 2025 specifically for the role of "{role}".

                IMPORTANT CONTEXT: You're responding to someone who works for a company that specializes in reselling software and software delivery solutions to enterprise customers. Your response must be SPECIFICALLY TAILORED to their exact job role, not generic.
                
                Research deeply into the specific challenges, tools, and workflows that a "{role}" would have experienced in 1995 versus 2025. Include industry-specific technologies, methodologies, and business practices that directly relate to this role.
                
                Format your response in a clean, minimalist style with three sections:
                
                1995: 
                [Role-specific bullet points about the exact tools, processes, and environment a {role} would have used in 1995]
                
                2025: 
                [Role-specific bullet points about the exact tools, processes, and environment a {role} uses in 2025]
                
                What Was Impossible Then, Now Possible:
                [3 specific transformative changes that would be MOST RELEVANT to a {role} - focus on game-changing capabilities that specifically transform how someone in this exact role works today]
                
                Every single bullet point must directly connect to the {role}'s daily work. Avoid generic enterprise software facts that aren't directly relevant to this specific role. Use concrete examples, specific tool names, and realistic workflows."""},
                {"role": "user", "content": f"My role is {role}. Create a highly personalized comparison showing how my specific job has evolved from 1995 to 2025, focusing on the tools, processes, and environment I would have used then versus now. For the third section, highlight the most dramatic transformations specifically relevant to someone in my role."}
            ],
            temperature=0.7,  # Slightly higher temperature for more creative, personalized responses
            max_tokens=800    # Increased token limit for more detailed responses
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating comparison. Please try again. Technical details: {str(e)}"

# Format the response in a clean, minimalist way with bullet points
def format_result(result_text, role):
    formatted_text = ""
    
    # Split into sections and process
    if "1995:" in result_text:
        parts = result_text.split("1995:")
        pre_text = parts[0]
        rest = parts[1]
        
        if pre_text.strip():
            formatted_text += f'<div>{pre_text}</div>'
        
        if "2025:" in rest:
            year_parts = rest.split("2025:")
            year_1995 = year_parts[0]
            rest = year_parts[1]
        else:
            year_1995 = rest
            rest = ""
        
        # Process 1995 section
        formatted_text += '<div class="year-section"><strong>1995</strong><ul>'
        
        # Convert text to bullet points if not already
        lines = year_1995.strip().split('\n')
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                if clean_line.startswith('•') or clean_line.startswith('-') or clean_line.startswith('*'):
                    formatted_text += f'<li>{clean_line[1:].strip()}</li>'
                else:
                    formatted_text += f'<li>{clean_line}</li>'
        
        formatted_text += '</ul></div>'
        
        # Process 2025 section if it exists
        if rest:
            tip_split = None
            for tip in ["Tips:", "Adaptation Tips:", "Practical Tips:"]:
                if tip in rest:
                    tip_parts = rest.split(tip)
                    year_2025 = tip_parts[0]
                    tips_text = tip_parts[1]
                    tip_split = True
                    break
            
            if not tip_split:
                year_2025 = rest
                tips_text = ""
            
            # Format 2025 section
            formatted_text += '<div class="year-section"><strong>2025</strong><ul>'
            
            lines = year_2025.strip().split('\n')
            for line in lines:
                clean_line = line.strip()
                if clean_line:
                    if clean_line.startswith('•') or clean_line.startswith('-') or clean_line.startswith('*'):
                        formatted_text += f'<li>{clean_line[1:].strip()}</li>'
                    else:
                        formatted_text += f'<li>{clean_line}</li>'
            
            formatted_text += '</ul></div>'
            
            # Format tips section if it exists, with dynamic title based on role
            if tips_text:
                # Create a dynamic header based on the role
                dynamic_header = f"What Was Impossible for {role}s Then, Now Possible"
                
                formatted_text += f'<div class="transform-section"><strong>{dynamic_header}</strong><ul>'
                
                lines = tips_text.strip().split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if clean_line:
                        if clean_line.startswith('•') or clean_line.startswith('-') or clean_line.startswith('*'):
                            formatted_text += f'<li>{clean_line[1:].strip()}</li>'
                        else:
                            formatted_text += f'<li>{clean_line}</li>'
                
                formatted_text += '</ul></div>'
    else:
        # If the text doesn't follow the expected format, just return it as is
        formatted_text = f'<div>{result_text}</div>'
    
    return formatted_text

# Login Page
# =============================
if not st.session_state.auth_status:
    # Display header image using requests to fetch first
    header_image_url = "https://i.postimg.cc/yYs1QF1g/pic2.png"
    img = load_image_from_url(header_image_url)
    if img:
        st.image(img, use_container_width=True)
    else:
        # Fallback to a more direct HTML approach if loading fails
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <a href='https://postimages.org/' target='_blank'>
                <img src='https://i.postimg.cc/yYs1QF1g/pic2.png' width="100%" alt='TimeShift Logo'/>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("Compare professional roles: 1995 vs 2025")
    
    with st.container():
        st.markdown('<div class="info-msg">Enter access code to compare how enterprise software roles have evolved over three decades.</div>', unsafe_allow_html=True)
        code_input = st.text_input("Access code:", type="password")
        if st.button("Enter TimeShift", use_container_width=True):
            if code_input == ACCESS_CODE:
                st.session_state.auth_status = True
                st.rerun()
            else:
                st.error("Invalid code")
    
    st.markdown('<div class="footer">Built for Fun and Learning: <a href="https://ifiecas.com/" target="_blank">Ivy Fiecas-Borjal</a></div>', unsafe_allow_html=True)

# =============================
# Main App
# =============================
else:
    # Display header image using requests to fetch first
    header_image_url = "https://i.postimg.cc/yYs1QF1g/pic2.png"
    img = load_image_from_url(header_image_url)
    if img:
        st.image(img, use_container_width=True)
    else:
        # Fallback to a more direct HTML approach if loading fails
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <a href='https://postimages.org/' target='_blank'>
                <img src='https://i.postimg.cc/yYs1QF1g/pic2.png' width="100%" alt='TimeShift Logo'/>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Sign-out button
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Sign Out"):
            st.session_state.auth_status = False
            st.rerun()
    
    # Input section
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-msg">
            Enter your role in enterprise software sales or delivery to see how it has evolved 
            from 1995 to 2025. Discover changes in tools, customer expectations, and delivery models.
        </div>
        """, unsafe_allow_html=True)
        
        role = st.text_input("What's your professional role?", 
                            placeholder="Enter your complete role/designation")
                
        generate = st.button("Generate Comparison", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display result
    if role and generate:
        with st.spinner("Generating comparison..."):
            result = fetch_timeshift_story(role)
        
        st.markdown('<div class="results">', unsafe_allow_html=True)
        
        st.subheader(f"{role}: 1995 vs 2025")
        
        formatted_result = format_result(result, role)
        st.markdown(formatted_result, unsafe_allow_html=True)
        
        # Start Over button
        if st.button("Start Over", use_container_width=True):
            # Clear the role input
            role = ""
            st.session_state.role_input = ""
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Initial state message
    if not (role and generate):
        pass
    
    st.markdown('<div class="footer">Built for Fun and Learning: <a href="https://ifiecas.com/" target="_blank">Ivy Fiecas-Borjal</a></div>', unsafe_allow_html=True)
