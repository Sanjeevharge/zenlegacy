# ZenLegacy API Marketplace

## Project Description

The ZenLegacy API Marketplace is a web platform that allows users to generate and deploy APIs automatically based on simple natural language prompts. Users describe their API requirements in plain English, and the system generates production-style Python FastAPI code complete with CRUD operations and database interactions tailored to the user's input.

The platform is built using Streamlit for the frontend, LangChain + Ollama (Llama3) for local AI-powered code generation, and Uvicorn for real-time API deployment.

## Project Scope

- **API Generation**: The platform lets users input detailed prompts describing their desired API. Based on user input, the system generates FastAPI code including database models via SQLAlchemy, validation schemas via Pydantic, and full CRUD endpoints backed by SQLite.
- **Code Deployment**: The generated API code is saved to `main.py` and automatically deployed using Uvicorn in a background thread, making the API available for immediate use without freezing the UI.
- **API History**: Every generated API is saved to `api_history.json` and accessible from the sidebar. Past APIs can be re-deployed or deleted at any time.

## How to Run the Project

### Prerequisites

- Python 3.12+ installed on your system
- [Ollama](https://ollama.com) installed on your system

### Setup Instructions

- Clone the Repository:

```
git clone https://github.com/swetha3456/zenlegacy-api-marketplace.git
```

- Install the Dependencies:

```
pip install langchain langchain_core langchain_community langchain_ollama streamlit sqlalchemy fastapi uvicorn
```

- Pull the Llama3 model (one-time download, ~4 GB):

```
ollama pull llama3
```

### Running the App

You need **two terminals** running simultaneously:

**Terminal 1 — Start the AI engine:**
```
ollama serve
```
Leave this running. Without it the AI cannot generate code.

**Terminal 2 — Start the Streamlit UI:**
```
streamlit run streamlit_frontend.py
```
Open the URL it prints (usually `http://localhost:8501`) in your browser.

### Usage

1. Open the Streamlit interface in your browser.
2. Enter a description of the API you want to generate in the prompt field.
3. Click the **Deploy API** button and wait 20–60 seconds for Llama3 to write the code.
4. Once deployed, open `http://localhost:8000/docs` to interact with your live API via Swagger UI.
5. Use the sidebar to view, re-deploy, or delete past generated APIs.

### Example Prompts

- `API to store and retrieve employee data with name, role, and salary`
- `API for a todo list with tasks that have title, description, and completed status`
- `API to manage a book library with title, author, and genre`
- `API for user registration with username, email, and password`

## Novel Features

- API generation from natural language prompts using a fully local AI model
- Non-blocking automated deployment — Streamlit stays responsive while the API runs
- Auto IP detection — no hardcoded addresses, works on any machine
- API history with re-deploy support

## Troubleshooting

- **Ollama errors / connection refused**: Make sure `ollama serve` is running in a terminal before starting the app.
- **Model not found**: Run `ollama pull llama3` to download the model.
- **Port already in use**: Change the port number in the UI before clicking Deploy.
- **Generated code has errors**: Try a more specific prompt, or edit `main.py` directly and restart with `uvicorn main:app --reload`.

## Future Enhancements

- **API Customization**: Allowing more customization to the API once it has been generated.
- **User Authentication**: Implement user accounts for saving and managing API projects.
- **Model Selection**: Choose between different Ollama models for code generation.
- **Export Options**: One-click export as a Docker container or zip archive.