import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ollama
import streamlit as st
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

DEFAULT_MODEL = "llama3.2"

ITINERARY_PROMPT = """You are an expert travel planner. Create a detailed {days}-day travel itinerary for {city}.

Budget: {budget_desc}

Structure your response as follows:
- Start with a brief introduction about {city}
- For each day, provide:
  * Morning activities (with specific landmarks, cafes, or attractions)
  * Afternoon activities
  * Evening activities and dinner recommendations
  * Practical tips (transport, best time to visit, approximate costs in local currency and USD)
- End with a "Local Tips" section covering: best neighbourhoods to explore, must-try foods, and safety advice
- End with a "Estimated Total Cost" breakdown covering accommodation, food, transport, and activities per day and for the full trip

Tailor ALL recommendations (hotels, restaurants, activities, transport) to the stated budget level.
Be specific with place names, opening hours where relevant, and estimated travel times between locations.
Keep the tone enthusiastic but practical."""

MODIFY_PROMPT = """You are an expert travel planner. Below is an existing {days}-day itinerary for {city}.

Budget: {budget_desc}

CURRENT ITINERARY:
{itinerary}

The traveller has shared the following feedback:
- Places/experiences they LIKED: {liked}
- Places/experiences they want to AVOID or did NOT enjoy: {disliked}

Please create an UPDATED itinerary that:
1. Keeps or expands on the elements the traveller liked
2. Completely removes and replaces any activities related to what they disliked
3. Suggests alternative experiences of a similar type for the replaced slots
4. Maintains the same day-by-day structure as before
5. Keeps all recommendations within the stated budget level

Be specific and enthusiastic. Explain briefly why you made key changes."""


def _budget_desc(tier: str, amount: Optional[int]) -> str:
    base = {"Budget": "budget/backpacker — cheap hostels, street food, free attractions",
            "Mid-range": "mid-range — comfortable hotels, sit-down restaurants, mix of paid and free activities",
            "Luxury": "luxury — upscale hotels, fine dining, premium experiences"}[tier]
    if amount:
        return f"{base}. Total trip budget: ~${amount:,} USD"
    return base


def stream_itinerary(city: str, days: int, model: str, budget_tier: str, budget_amount: Optional[int]):
    prompt = ITINERARY_PROMPT.format(city=city, days=days, budget_desc=_budget_desc(budget_tier, budget_amount))
    for chunk in ollama.generate(model=model, prompt=prompt, stream=True):
        yield chunk["response"]


def stream_modified_itinerary(city: str, days: int, itinerary: str, liked: str, disliked: str, model: str, budget_tier: str, budget_amount: Optional[int]):
    prompt = MODIFY_PROMPT.format(
        city=city,
        days=days,
        itinerary=itinerary,
        liked=liked or "nothing specified",
        disliked=disliked or "nothing specified",
        budget_desc=_budget_desc(budget_tier, budget_amount),
    )
    for chunk in ollama.generate(model=model, prompt=prompt, stream=True):
        yield chunk["response"]


def send_email(to_email: str, city: str, itinerary: str) -> None:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not sender_email or not sender_password:
        raise ValueError("SMTP_EMAIL and SMTP_PASSWORD must be set in your .env file.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your Travel Itinerary for {city}"
    msg["From"] = sender_email
    msg["To"] = to_email

    plain_body = f"Your Travel Itinerary for {city}\n\n{itinerary}"
    html_body = f"""
    <html><body>
    <h1>Your Travel Itinerary for {city}</h1>
    <pre style="font-family: Arial, sans-serif; white-space: pre-wrap; line-height: 1.6;">
{itinerary}
    </pre>
    </body></html>
    """

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


# ── UI ────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Travel Itinerary Generator", page_icon="✈️", layout="centered")
st.title("✈️ Travel Itinerary Generator")
st.caption("Powered by Ollama — generate, email, and personalise your perfect trip.")

with st.sidebar:
    st.header("Model Settings")
    model = st.text_input("Ollama model", value=DEFAULT_MODEL, help="Must be pulled locally, e.g. llama3.2, mistral, gemma2")

# City + days inputs
col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("Where do you want to go?", placeholder="e.g. Paris, Tokyo, New York")
with col2:
    days = st.number_input("Days", min_value=1, max_value=14, value=3, step=1)

# Budget inputs
col3, col4 = st.columns([1, 1])
with col3:
    budget_tier = st.selectbox("Budget level", ["Budget", "Mid-range", "Luxury"])
with col4:
    budget_amount = st.number_input("Total budget (USD, optional)", min_value=0, value=0, step=100)
    budget_amount = int(budget_amount) if budget_amount > 0 else None

if st.button("Generate Itinerary", type="primary", use_container_width=True):
    if not city.strip():
        st.warning("Please enter a city name.")
    else:
        try:
            st.divider()
            st.subheader(f"📍 {days}-Day Itinerary: {city.strip()}")
            with st.spinner("Generating your itinerary..."):
                itinerary = st.write_stream(stream_itinerary(city.strip(), days, model, budget_tier, budget_amount))
            st.session_state["itinerary"] = itinerary
            st.session_state["city"] = city.strip()
            st.session_state["days"] = days
            st.session_state["budget_tier"] = budget_tier
            st.session_state["budget_amount"] = budget_amount
            st.session_state["_just_generated"] = True
        except Exception as e:
            st.error(f"Failed to generate itinerary: {e}")

# ── Display itinerary ─────────────────────────────────────────────────────────

if "itinerary" in st.session_state and not st.session_state.get("_just_generated"):
    st.divider()
    st.subheader(f"📍 {st.session_state['days']}-Day Itinerary: {st.session_state['city']}")
    st.markdown(st.session_state["itinerary"])

st.session_state["_just_generated"] = False

if "itinerary" in st.session_state:
    # ── Email section ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📧 Email this Itinerary")
    default_email = os.getenv("USER_EMAIL", "")
    recipient = st.text_input("Recipient email address", value=default_email)

    if st.button("Send Itinerary by Email", use_container_width=True):
        if not recipient.strip():
            st.warning("Please enter an email address.")
        else:
            with st.spinner("Sending email..."):
                try:
                    send_email(
                        recipient.strip(),
                        st.session_state["city"],
                        st.session_state["itinerary"],
                    )
                    st.success(f"Itinerary sent to {recipient}!")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Failed to send email: {e}")

    # ── Modify section ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("✏️ Modify Itinerary")
    st.caption("Tell us what you liked or want to avoid and we'll regenerate your itinerary.")

    liked = st.text_area(
        "Places / experiences you liked",
        placeholder="e.g. Eiffel Tower, Seine river cruise, cosy cafés",
    )
    disliked = st.text_area(
        "Places / experiences to avoid",
        placeholder="e.g. crowded tourist traps, modern art museums, expensive restaurants",
    )

    if st.button("Modify Itinerary", type="secondary", use_container_width=True):
        if not liked.strip() and not disliked.strip():
            st.warning("Please share at least one preference before modifying.")
        else:
            try:
                st.divider()
                st.subheader(f"📍 Updated {st.session_state['days']}-Day Itinerary: {st.session_state['city']}")
                with st.spinner("Updating your itinerary..."):
                    updated = st.write_stream(stream_modified_itinerary(
                        st.session_state["city"],
                        st.session_state["days"],
                        st.session_state["itinerary"],
                        liked.strip(),
                        disliked.strip(),
                        model,
                        st.session_state.get("budget_tier", "Mid-range"),
                        st.session_state.get("budget_amount"),
                    ))
                st.session_state["itinerary"] = updated
                st.session_state["_just_generated"] = True
            except Exception as e:
                st.error(f"Failed to modify itinerary: {e}")
