
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="ECHOBOND",
    page_icon="🔊",
    layout="centered"
)

load_dotenv()

# Read API key from local .env or Streamlit Cloud Secrets
API_KEY = os.getenv("GNANI_API_KEY_ID")

if not API_KEY:
    try:
        API_KEY = st.secrets.get("GNANI_API_KEY_ID")
    except Exception:
        API_KEY = None

API_URL = "https://api.vachana.ai/stt/v3"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "transcript": "",
    "agreement_saved": False,
    "work_days": 2,
    "daily_wage": 300,
    "advance": 100,
    "received": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# FRONTEND DESIGN
# --------------------------------------------------

st.html("""
<style>

/* PAGE BACKGROUND */

.stApp {
    background: linear-gradient(
        180deg,
        #f5f7ed 0%,
        #ffffff 65%
    );
    color: #20352d !important;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* HERO SECTION */

.hero {
    background: linear-gradient(
        135deg,
        #173f35,
        #286653
    );
    padding: 35px 30px;
    border-radius: 24px;
    color: #ffffff !important;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(23, 63, 53, 0.13);
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    padding: 6px 12px;
    border-radius: 30px;
    font-size: 12px;
    letter-spacing: 1px;
    margin-bottom: 15px;
    color: #ffffff !important;
}

.hero h1 {
    font-size: 42px;
    margin: 0;
    color: #ffffff !important;
    font-weight: 800;
}

.hero p {
    color: #e1eee8 !important;
    font-size: 16px;
    margin-bottom: 0;
}

/* GENERAL TEXT */

.stApp p,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"] {
    color: #20352d !important;
}

/* HERO TEXT OVERRIDE */

.hero,
.hero h1,
.hero p,
.hero .hero-tag {
    color: #ffffff !important;
}

.hero p {
    color: #e1eee8 !important;
}

/* INPUT FIELDS */

.stApp input,
.stApp textarea {
    color: #20352d !important;
    background-color: #ffffff !important;
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background: #f1f6ef;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #e1eadf;
}

div[data-testid="stMetricLabel"] {
    color: #52665b !important;
}

div[data-testid="stMetricValue"] {
    color: #173f35 !important;
    font-weight: 800 !important;
}

/* SUCCESS, WARNING AND INFO ALERTS */

div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] span {
    color: #ffffff !important;
}

/* BUTTONS */

div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

/* FOOTER */

.footer-note {
    text-align: center;
    color: #64736a !important;
    font-size: 12px;
    padding-top: 25px;
}

.footer-note p {
    color: #64736a !important;
}

</style>

<div class="hero">
    <div class="hero-tag">
        VOICE-BASED WORK AGREEMENT RECORD
    </div>

    <h1>ECHOBOND 🤝</h1>

    <p>A promise spoken. A record remembered.</p>

    <p style="font-size:14px; margin-top:12px;">
        Record your work agreement, keep track of payment,
        and remember what was promised.
    </p>
</div>
""")

# --------------------------------------------------
# AUDIO UPLOAD AND GNANI TRANSCRIPTION
# --------------------------------------------------

st.markdown("### 🎙️ Record your agreement")

st.write(
    "Upload an audio recording of the work agreement. "
    "ECHOBOND will convert your speech into text."
)

language_options = {
    "Malayalam": ("ml-IN", "Malayalam"),
    "English": ("en-IN", "English"),
    "Hindi": ("hi-IN", "Hindi"),
}

selected_language = st.selectbox(
    "Choose the language spoken",
    list(language_options.keys())
)

uploaded_file = st.file_uploader(
    "Upload an audio recording",
    type=["wav", "mp3", "m4a", "flac"],
    help="Audio files only. Video files are not supported."
)

if uploaded_file is not None:

    st.audio(uploaded_file)

    if st.button(
        "✨ Convert speech to text",
        use_container_width=True
    ):

        if not API_KEY:

            st.error("Gnani API key not found.")

            st.info(
                "Add GNANI_API_KEY_ID to your Streamlit Cloud Secrets."
            )

        else:

            language_code, preferred_language = (
                language_options[selected_language]
            )

            headers = {
                "X-API-Key-ID": API_KEY
            }

            files = {
                "audio_file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            data = {
                "language_code": language_code,
                "preferred_language": preferred_language,
                "format": "transcribe",
                "itn_native_numerals": "true"
            }

            try:

                with st.spinner(
                    "Gnani AI is listening to your recording..."
                ):

                    response = requests.post(
                        API_URL,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=180
                    )

                if response.status_code == 504:

                    st.error(
                        "Gnani AI took too long to respond."
                    )

                    st.info(
                        "Please try again later or use a shorter recording."
                    )

                elif response.status_code == 401:

                    st.error(
                        "Gnani API rejected the key (401 Unauthorized)."
                    )

                    st.info(
                        "Check your Gnani dashboard and Streamlit Cloud "
                        "Secrets. Make sure the API key is active "
                        "and copied correctly."
                    )

                elif response.status_code != 200:

                    st.error(
                        f"Gnani API error: {response.status_code}"
                    )

                    st.caption(response.text[:1000])

                else:

                    result = response.json()
                    transcript = result.get("transcript", "")

                    if transcript:

                        st.session_state["transcript"] = transcript
                        st.session_state["agreement_saved"] = False

                        st.success(
                            "Transcription completed!"
                        )

                    else:

                        st.error(
                            "No transcript returned. "
                            "Please try another recording."
                        )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. Try a shorter recording "
                    "or try again later."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to Gnani AI: {e}"
                )

            except ValueError:

                st.error(
                    "Gnani AI returned an unexpected response. "
                    "Please try again."
                )

# --------------------------------------------------
# REVIEW AND SAVE AGREEMENT
# --------------------------------------------------

if st.session_state["transcript"]:

    st.markdown("---")
    st.markdown("### 📝 Review your agreement")

    st.caption(
        "Check the transcript carefully. Correct any mistakes "
        "before saving your record."
    )

    st.text_area(
        "Transcribed agreement",
        key="transcript",
        height=150
    )

    if st.button(
        "💾 Save agreement",
        use_container_width=True
    ):

        if st.session_state["transcript"].strip():

            st.session_state["agreement_saved"] = True

            st.success("Agreement saved!")

        else:

            st.warning(
                "Please enter the agreement before saving."
            )

# --------------------------------------------------
# PAYMENT CALCULATOR
# --------------------------------------------------

st.markdown("---")
st.markdown("### 💰 Payment calculator")

st.write(
    "Enter the agreed work and payment details "
    "to calculate how much money is still expected."
)

col1, col2 = st.columns(2)

with col1:

    st.number_input(
        "Number of work days",
        min_value=0,
        step=1,
        key="work_days"
    )

    st.number_input(
        "Daily wage (₹)",
        min_value=0,
        step=50,
        key="daily_wage"
    )

with col2:

    st.number_input(
        "Advance received (₹)",
        min_value=0,
        step=50,
        key="advance"
    )

    st.number_input(
        "Final payment received (₹)",
        min_value=0,
        step=50,
        key="received"
    )

total_wage = (
    st.session_state["work_days"]
    * st.session_state["daily_wage"]
)

expected_payment = max(
    total_wage - st.session_state["advance"],
    0
)

received = st.session_state["received"]

difference = received - expected_payment

st.markdown("#### Payment summary")

metric1, metric2 = st.columns(2)

with metric1:

    st.metric(
        "Total agreed wages",
        f"₹{total_wage:,}"
    )

with metric2:

    st.metric(
        "Expected remaining payment",
        f"₹{expected_payment:,}"
    )

if received == expected_payment:

    st.success(
        "The received payment matches the expected amount."
    )

elif received < expected_payment:

    st.warning(
        f"₹{expected_payment - received:,} "
        "is still pending based on the details entered."
    )

else:

    st.info(
        f"₹{received - expected_payment:,} "
        "more than the expected amount has been entered as received."
    )

# --------------------------------------------------
# SAVED AGREEMENT SUMMARY
# --------------------------------------------------

if st.session_state["agreement_saved"]:

    st.markdown("---")
    st.markdown("### 📋 Saved agreement summary")

    st.success(
        "Your agreement record is saved in this app session."
    )

    st.markdown("**Agreement transcript**")

    st.write(st.session_state["transcript"])

    summary1, summary2 = st.columns(2)

    with summary1:

        st.metric(
            "Work days",
            st.session_state["work_days"]
        )

        st.metric(
            "Daily wage",
            f"₹{st.session_state['daily_wage']:,}"
        )

        st.metric(
            "Advance received",
            f"₹{st.session_state['advance']:,}"
        )

    with summary2:

        st.metric(
            "Total wages",
            f"₹{total_wage:,}"
        )

        st.metric(
            "Expected remaining",
            f"₹{expected_payment:,}"
        )

        st.metric(
            "Payment received",
            f"₹{received:,}"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.html("""
<div class="footer-note">

    <p>
        ECHOBOND 🤝 · A promise spoken. A record remembered.
    </p>

    <p>
        This is a personal record-keeping tool, not legal proof
        or a substitute for a written agreement.
    </p>

</div>
""")
