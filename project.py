import streamlit as st
from PIL import Image
import base64
import os
import requests
from urllib.parse import urlparse
from streamlit_lottie import st_lottie
from google.generativeai import configure, GenerativeModel
import fitz  # PyMuPDF
import re
import pandas as pd

# Set up the Generative AI configuration with a placeholder API key
configure(api_key=st.secrets["api_key"])

# Create a Generative Model instance (assuming 'gemini-pro' is a valid model)
model = GenerativeModel('gemini-pro')


# Function to download generated report
def download_generated_report(content, filename, format='txt'):
    extension = format
    temp_filename = f"{filename}.{extension}"
    with open(temp_filename, 'w') as file:
        file.write(content)
    with open(temp_filename, 'rb') as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/{format};base64,{b64}" download="{filename}.{format}">Download Report ({format.upper()})</a>'
    st.markdown(href, unsafe_allow_html=True)
    os.remove(temp_filename)


# Function to load Lottie animations
def load_lottie_url(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to extract topic from prompt
def extract_topic(prompt):
    start_phrases = ["@codex", "codex", "@SoulCare"]
    for phrase in start_phrases:
        if prompt.lower().startswith(phrase):
            return prompt[len(phrase):].strip()
    return prompt.strip()

# Function to fetch YouTube videos
def fetch_youtube_videos(query):
    api_key = st.secrets["youtube_api_key"]
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 4,
        "key": api_key
    }
    response = requests.get(search_url, params=params)
    video_details = []
    if response.status_code == 200:
        results = response.json()["items"]
        for item in results:
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_details.append({
                "title": video_title,
                "url": video_url,
                "video_id": video_id
            })
    else:
        st.error(f"Failed to fetch YouTube videos. Status code: {response.status_code}")
    return video_details


# Main application
def main():
    st.set_page_config(page_title="Mental Health Support App", page_icon="💀", layout="wide",
                       initial_sidebar_state="expanded")

    st.sidebar.image("soul.png", use_column_width=True)
    page = st.sidebar.selectbox("::Menu::",
                                ["🏠 Home", "Mental Health Instructor ➕", "Report Analyzer ⚡", "Know Your Medicine 🌐",
                                 "Contact Experts", "Privacy Policy"])

    if page == "🏠 Home":
        st.title("Welcome to SoulCare AI ➕")
        st.markdown("""
        **SoulCare AI**:
        SoulCare, powered by the Gemini API, is a basic chatbot designed for Mental Health Care. 
        Project: SoulCare

**Guidelines:**

Respectful Conduct: Users are expected to engage in respectful and considerate interactions within the SoulCare community. Any form of harassment, hate speech, or derogatory behavior will not be tolerated.

Accuracy of Information: While SoulCare aims to provide helpful information and support, users should understand that the content provided is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for personalized guidance.

Data Privacy: SoulCare respects user privacy and confidentiality. Personal information shared within the platform will be handled with the utmost care and will not be shared with third parties without explicit consent, except as required by law.

Community Support: SoulCare encourages users to support each other in a positive and constructive manner. Users are welcome to share their experiences, insights, and advice, but should refrain from giving medical diagnoses or prescribing treatments.

Feedback and Suggestions: We value user feedback and suggestions for improving SoulCare. Users are encouraged to provide feedback on their experience with the platform and suggest features or content that would enhance their user experience.

Safety and Well-being: SoulCare prioritizes the safety and well-being of its users. If you or someone you know is in crisis or experiencing a medical emergency, please seek immediate assistance from a qualified healthcare professional or emergency services.**

        Developed by SKAV TECH, a company focused on creating practical AI projects, SoulCare is intended for educational purposes only. We do not endorse any illegal or unethical activities.
        """)

        # Embedding Lottie animation
        st.markdown("""
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <lottie-player src="https://lottie.host/ee1e5978-9014-47cb-8031-45874d2dc909/tXASIvRMrN.json" background="#FFFFFF" speed="1" style="width: 300px; height: 300px" loop controls autoplay direction="1" mode="normal"></lottie-player>
        """, unsafe_allow_html=True)

    elif page == "Mental Health Instructor ➕":
        #st.image("soul.png")
        st.header("Mental Health Instructor ➕")

        lottie_url = "https://lottie.host/0c079fc2-f4df-452a-966b-3a852ffb9801/WjOxpGVduu.json"
        # Load and display Lottie animation
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=220, height=300, key="lottie_animation")
        else:
            st.error("Failed to load Lottie animation.")

        st.markdown(
            "SoulCare may provide inaccurate responses. Read all the guidelines and usage instructions. Contact a doctor before proceeding.")

        question = st.text_input("Ask the model a question:")
        if st.button("Ask AI"):
            topic = extract_topic(question)

            with st.spinner("Generating response 😉"):
                try:
                    response = model.generate_content(f"You are an expert mental healthcare professional: {question}")
                    if response.text:
                        st.text("SoulCare Response:")
                        st.write(response.text)
                        st.markdown('---')

                        # Fetch YouTube video suggestions
                        video_suggestions = fetch_youtube_videos(topic)
                        if video_suggestions:
                            st.markdown("### YouTube Video Suggestions:")

                            # Summary provided by the model
                            summary = response.text

                            # Display the summary
                            st.markdown(f"**Summary:** {summary}")

                            for video in video_suggestions:
                                st.write(f"[{video['title']}]({video['url']})")
                                st.video(video["url"])

                    else:
                        st.error("No valid response received from the AI model.")
                        st.write(f"Safety ratings: {response.safety_ratings}"
                                 f"Change the prompt to continue")
                except ValueError as e:
                    st.info(f"🤐 Unable to assist with that prompt due to: {e}"
                            f"Change the prompt to continue")
                except IndexError as e:
                    st.info(f"🤐 Unable to assist with that prompt due to: {e}"
                            f"Change the prompt to continue")
                except Exception as e:
                    st.info(f"An unexpected error occurred 😕, Change the prompt to continue: {e}")

                report_keywords = ["report", "health", "illness", "summary", "sick"]
                if any(keyword in question.lower() for keyword in report_keywords):
                    if response.text:
                        download_generated_report(response.text, "report")
        st.markdown('---')

    elif page == "Report Analyzer ⚡":
        st.title("Report Analyzer")

        lottie_url = "https://lottie.host/c072814c-e678-429b-983e-83d0d2f6855d/cpGp0hsXPO.json"

        # Load and display Lottie animation
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=620, height=330, key="lottie_animation")
        else:
            st.error("Failed to load Lottie animation.")
        uploaded_pdf = st.file_uploader("Upload your medical report (PDF)", type="pdf")

        if uploaded_pdf:
            with st.spinner("Extracting Summary of the Report ..."):
                report_text = extract_text_from_pdf(uploaded_pdf)

            # Generate a summary using the model
            response = model.generate_content(f"your are mental healthcare, General surgeon Doctor with 17+ years of experience, Provide a summary for the following medical report: {report_text}")
            summary = response.text if response.text else "Summary could not be generated."

            # Display the summary
            st.markdown(f"**Summary:** {summary}")


    elif page == "Know Your Medicine 🌐":
        st.title("Know Your Medicine")

        input_method = st.radio("Choose input method", ("Text", "PDF"))

        if input_method == "Text":
            medicine_name = st.text_input("Enter the medicine name")
            if st.button("Get Information"):

                lottie_url = "https://lottie.host/3c9492e6-52ef-4987-a9c4-77b2b5147d36/VCJCsVmrQO.json"

                # Load and display Lottie animation
                lottie_animation = load_lottie_url(lottie_url)
                if lottie_animation:
                    st_lottie(lottie_animation, speed=1, width=150, height=100, key="lottie_animation")
                else:
                    st.error("Failed to load Lottie animation.")

                with st.spinner("Generating summary..."):
                    response = model.generate_content(f"Provide a summary for the medicine: {medicine_name}")
                    if response.text:
                        st.write(response.text)
                    else:
                        st.error("Failed to generate summary.")

        else:
            uploaded_pdf = st.file_uploader("Upload a PDF file containing information about the medicine", type="pdf")
            if uploaded_pdf:
                with st.spinner("Extracting text from PDF 💀..."):
                    medicine_text = extract_text_from_pdf(uploaded_pdf)
                    st.write(medicine_text)

                    with st.spinner("Generating summary..."):
                        response = model.generate_content(f"Provide a summary for the following text: {medicine_text}")
                        if response.text:
                            st.write(response.text)
                        else:
                            st.error("Failed to generate summary.")

    elif page == "Privacy Policy":
        st.title("Privacy Policy")
        st.markdown("""1. Information Collection and Use:

SoulCare may collect personal information, such as name, email address, and demographic data, to provide personalized services and improve user experience.
This information will be used for internal purposes only and will not be shared with third parties without user consent, except as required by law.

2. **Data Security**:

SoulCare employs industry-standard security measures to protect user data from unauthorized access, alteration, disclosure, or destruction.
Users are responsible for maintaining the confidentiality of their account credentials and should report any suspicious activity or unauthorized access to their account.

3. **Cookies and Tracking**:

SoulCare may use cookies and similar tracking technologies to enhance user experience and gather information about user interactions with the platform.
Users have the option to disable cookies in their web browser settings, but this may affect certain features and functionality of the platform.

4. **Third-party Links**:

SoulCare may contain links to third-party websites or services for additional resources and information. These third-party sites have their own privacy policies, and SoulCare is not responsible for their practices.

5. **Children's Privacy**:

SoulCare is not intended for use by children under the age of 13. We do not knowingly collect personal information from children, and if we become aware of such data, we will take steps to delete it.

6. **Policy Updates**:

SoulCare may update its privacy policy from time to time to reflect changes in data practices or legal requirements. Users will be notified of any significant changes to the policy.

""")
        st.title("""**Terms and Conditions**
1. **Acceptance of Terms**:

By accessing or using SoulCare, you agree to comply with these terms and conditions, as well as any additional guidelines or rules provided by the platform.

2. **User Conduct**:

Users are responsible for their conduct within SoulCare and must not engage in any activity that violates these terms, infringes on the rights of others, or disrupts the functioning of the platform.

3. **Intellectual Property**:

SoulCare and its content, including text, graphics, logos, and images, are protected by intellectual property laws and belong to SKAV TECH. Users may not use, reproduce, or distribute this content without permission.

4. **Limitation of Liability**:

SoulCare is provided on an "as is" and "as available" basis, without warranties of any kind. SKAV TECH is not liable for any direct, indirect, incidental, or consequential damages arising from the use of SoulCare.

5. **Indemnification**:

Users agree to indemnify and hold harmless SKAV TECH, its affiliates, and partners from any claims, losses, or damages arising from their use of SoulCare or violation of these terms.

6. **Governing Law**:

These terms and conditions are governed by the laws of [Jurisdiction], and any disputes will be resolved through arbitration in accordance with those laws.
These guidelines, privacy policy, and terms and conditions outline the expectations and responsibilities for users of the SoulCare platform. By using SoulCare, users agree to abide by these terms and contribute to a positive and supportive community environment.""")

    elif page == "Contact Experts":
        st.title("Contact Experts")
        st.markdown("""
            If you need immediate assistance, please contact a healthcare professional.

            - **Emergency Contact Numbers**: [Emergency Contact Numbers](https://drsafehands.com/counseling/Hyderabad)
            
            - **Popular Centers**: 
              1. [Counseling Centre in Vijayawada](https://threebestrated.in/counseling-centre-in-vijayawada-ap)
              2. [Psychology Services in Vijayawada](https://www.starofservice.in/dir/andhra-pradesh/krishna/vijayawada/psychology)
              3. [Mental Health Counsel Online](https://www.talkspace.com/)
        """)


if __name__ == "__main__":
    main()
