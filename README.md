
# API Marketplace

## Project Description

The API Marketplace is a web platform that allows users to generate, and deploy APIs automatically based on simple user prompts. Users can describe their API requirements in natural language, and the system will generate Python-based FastAPI code to implement the functionality. The generated APIs include features such as CRUD operations and database interactions tailored to the user's input.

The platform is built using Streamlit for the frontend, Langchain for dynamic code generation, and Uvicorn for real-time API deployment.

## Project Scope

- **API Generation**: The platform lets users input detailed prompts describing their desired API. Based on user input, the system generates API models with FastAPI, including database interaction through SQLAlchemy and validation using Pydantic schemas.
- **Code Deployment**: The generated API code is saved in a file and automatically deployed using Uvicorn, making the API available for immediate use.

## How to Run the Project

### Prerequisites

- Ensure you have Python 3.12+ on your system

### Setup Instructions
- Clone the Repository:
```
git clone https://github.com/swetha3456/zenlegacy-api-marketplace.git
```
- Install the Dependencies
```
pip install langchain langchain_core langchain_community langchain_ollama streamlit sqlalchemy fastapi uvicorn
```
- Replace the ```ip_address``` string in streamlit_frontend.py with the ip address of your local server.

### Run the Streamlit App:
```
streamlit run streamlit_frontend.py
```

### Usage
Open the Streamlit interface in your browser.
Enter a description of the API you want to generate in the prompt field.
Click the Deploy button to generate the code and deploy the api.
API usage instructions will be displayed on screen.

## Novel Features

- API generation from natural language prompts
- Automated deployment

## Future Enhancements

- API Customization: Allowing more customization to the API once it has been generated.
- User Authentication: Implement user accounts for saving and managing API projects.


