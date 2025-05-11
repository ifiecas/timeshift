# TimeShift

![TimeShift Screenshot](https://i.postimg.cc/qvswc8Zn/Screenshot-2025-05-11-at-4-44-47-pm.png)

**TimeShift** is an AI-powered web app that lets users explore how job roles and skills have evolved over the last three decades. Built with Streamlit and powered by Azure AI Foundry, it’s inspired by Morgan Housel’s *Same As Ever* — highlighting how humans constantly pursue efficiency even as the world changes.

---

## 🔗 Live Demo

> **Access Code Notice:** The app requires users to enter an access code on the homepage.  
> If you’d like to try the app, feel free to reach out to me for access.


👉 Try the app here: [Launch TimeShift](https://timeshift-app-b0d4aha0fvb5ftda.australiaeast-01.azurewebsites.net/)

---

## 🔍 Features

- Enter any job title to compare past and present responsibilities
- Highlights skill shifts and enduring role traits
- AI-generated insights using Azure-hosted OpenAI models
- Fast, secure, and simple interface via Streamlit

---

## 🧰 Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python 3.10  
- **AI**: Azure OpenAI via Azure AI Foundry  
- **Secrets**: dotenv  
- **Utilities**: Requests, Pillow

---

## 🛠️ Getting Started (Local)

### Prerequisites

- Python 3.10+
- Access to Azure OpenAI via Azure AI Foundry
- Git + virtualenv

### 1. Clone and Set Up Environment

```bash
git clone https://github.com/yourusername/timeshift.git
cd timeshift
python -m venv antenv
source antenv/bin/activate
pip install -r requirements.txt
