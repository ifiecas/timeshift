import streamlit as st
from openai import AzureOpenAI
import os
from datetime import datetime
from dotenv import load_dotenv

# ✅ Set Streamlit page config FIRST
st.set_page_config(
    page_title="TimeShift",
    page_icon="⏳",
    initial_sidebar_state="collapsed"
)

# ✅ Load environment variables
load_dotenv()

# ✅ DEBUG: Show loaded variables
st.write("🔐 Key loaded:", os.getenv("AZURE_OPENAI_KEY")[:8] + "...")
st.write("🌐 Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
st.write("📦 Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))

# ✅ Custom CSS styling
st.markdown("""
<style>
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #333; }
    h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #111; }
    .stButton button { background-color: #0056D6; color: white; border-radius: 4px; border: none; padding: 0.5rem 1rem; font-weight: 500; }
    .stTextInput input { border-radius: 4px; border: 1px solid #E0E0E0; }
    .stSpinner div { border-color: #0056D6 !important; }
    .results { background-color: #FAFAFA; padding: 1.5rem; border-radius: 6px; margin-top: 2rem; border: 1px solid #EEEEEE; }
    .info-msg { background-color: #F0F7FF; border-left: 4px solid #0056D6; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }
    .footer { margin-top: 3rem; text-align: center; font-size: 0.8rem; color: #888; }
</style>
""", unsafe_allow_html=True)

# ✅ Basic app protection
ACCESS_CODE = "swo"

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

# 🔐 Access Code Page
if not st.session_state.auth_status:
    st.title("⏳ TimeShift")
    st.write("Compare professional roles: 1995 vs 2025")
    code_input = st.text_input("Access code:", type="password")
    if st.button("Enter TimeShift", use_container_width=True):
        if code_input == ACCESS_CODE:
            st.session_state.auth_status = True
            st.experimental_rerun()
        else:
            st.error("Invalid code, please try again")

# 🚀 Main App
else:
    # Azure OpenAI client setup
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-12-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    st.write("🔍 Using deployment:", deployment_name)

    def fetch_timeshift_story(role):
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": "You are a tech historian comparing 1995 vs 2025. Format your response with clear headings and short bullet points for mobile readability."},
                    {"role": "user", "content": f"My role is {role}. Give me a concise 1995 vs 2025 comparison focusing on tools, work culture, and technology. Include 3 practical adaptation tips."}
                ],
                temperature=0.7,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error generating comparison. Please try again. Technical details: {str(e)[:100]}"

    # Header & sign-out
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("⏳ TimeShift")
    with col2:
        if st.button("Sign Out"):
            st.session_state.auth_status = False
            st.experimental_rerun()

    st.write("Compare how professional roles evolved from 1995 to 2025")

    # Input + Button
    role = st.text_input("What's your professional role?", placeholder="e.g. Marketing Manager")
    generate = st.button("Generate Comparison", use_container_width=True)

    # Display result
    if role and generate:
        with st.spinner("Generating comparison..."):
            result = fetch_timeshift_story(role)

        st.markdown("<div class='results'>", unsafe_allow_html=True)
        st.subheader(f"{role}: 1995 vs 2025")
        formatted_result = result.replace("1995:", "**1995:**").replace("2025:", "**2025:**").replace("Tips:", "**Adaptation Tips:**")
        st.markdown(formatted_result)
        st.download_button(
            "Save as Text",
            data=f"TimeShift: {role} from 1995 to 2025\n\n{result}\n\nGenerated on {datetime.now().strftime('%Y-%m-%d')}",
            file_name=f"timeshift_{role.replace(' ', '_').lower()}.txt",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if not (role and generate):
        st.markdown("<div class='info-msg'>Enter your role to see how it has evolved over three decades</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer'>© 2025 TimeShift</div>", unsafe_allow_html=True)
