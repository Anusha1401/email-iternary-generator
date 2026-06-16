# ✈️ Travel Itinerary Generator

A locally-powered travel planner that generates personalised, budget-aware itineraries using [Ollama](https://ollama.com) — no API keys, no cloud costs, runs entirely on your machine.

## Features

- **AI-generated itineraries** — detailed day-by-day plans with morning, afternoon, and evening activities
- **Budget-aware planning** — choose Budget, Mid-range, or Luxury; optionally set a total spend cap in USD
- **Cost breakdown** — estimated costs for accommodation, food, transport, and activities
- **Real-time streaming** — watch the itinerary appear token by token instead of waiting for a blank spinner
- **Personalised modifications** — tell the app what you liked or want to avoid and get an updated plan instantly
- **Email delivery** — send the finished itinerary to any email address via Gmail (or any SMTP provider)
- **Model switcher** — swap between any locally-pulled Ollama model from the sidebar

## Demo

| Step | What to do |
|---|---|
| **Generate** | Enter a city, number of days, and budget level, then click **Generate Itinerary** |
| **Modify** | Use the **Modify Itinerary** section to keep what you loved and replace what you didn't |
| **Email** | Hit **Send Itinerary by Email** to deliver the plan straight to your inbox |

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- At least one Ollama model pulled (e.g. `llama3.2`)
- A Gmail App Password if you want to use the email feature

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/email-iternary.git
cd email-iternary
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull an Ollama model

```bash
# Start Ollama (if not already running)
ollama serve

# Pull a model — llama3.2 is the default
ollama pull llama3.2
```

Other good options:

| Model | Size | Notes |
|---|---|---|
| `llama3.2` | ~2 GB | Default, good balance of speed and quality |
| `llama3.2:1b` | ~1.3 GB | Fastest, lower quality |
| `mistral` | ~4 GB | Strong reasoning, slightly slower |
| `gemma2` | ~5 GB | Google's open model, very capable |

### 5. Configure email (optional)

Copy the example env file and fill in your details:

```bash
cp .env.example .env
```

```env
SMTP_EMAIL=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USER_EMAIL=you@gmail.com            # Pre-fills the recipient field in the UI
```

> **Gmail App Password:** Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), create a password for "Mail", and paste it as `SMTP_PASSWORD`. Do **not** use your regular Gmail password.

### 6. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Usage

1. **Enter a destination** — any city name
2. **Set the number of days** — 1 to 14
3. **Choose a budget level** — Budget / Mid-range / Luxury
4. **Set a total budget** (optional) — leave at 0 to skip
5. **Click Generate Itinerary** — text streams in real time
6. **Email it** — enter a recipient address and click Send
7. **Modify it** — describe what you liked or want to avoid, then click Modify Itinerary

You can switch the Ollama model at any time from the **sidebar**.

## Project Structure

```
.
├── app.py              # Streamlit app — UI, prompts, and email logic
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `ollama` | Local LLM inference via Ollama |
| `python-dotenv` | Load environment variables from `.env` |

## License

MIT
