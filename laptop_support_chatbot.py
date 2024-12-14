import os
from typing import List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

# Configuration for the Ollama LLM
class OllamaConfig:
    MODEL_NAME = "llama3.2"  # Ensure this matches your Ollama model
    BASE_URL = "http://localhost:11434"

# Predefined conversation contexts for different support scenarios
SUPPORT_CONTEXTS = {
    "billing": """You are a helpful customer support agent for a laptop selling website. 
    Assist the customer with billing-related inquiries, such as payment methods, 
    invoice details, and refund processes.""",
    
    "technical": """You are a technical support agent for a laptop selling website. 
    Provide detailed, step-by-step troubleshooting guidance for laptop issues, 
    including hardware and software problems.""",
    
    "product_inquiry": """You are a product expert for a laptop selling website. 
    Help customers understand laptop specifications, compare models, 
    and provide recommendations based on their needs."""
}

# Laptop Support Chatbot Class
class LaptopSupportChatbot:
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(
            model=OllamaConfig.MODEL_NAME, 
            base_url=OllamaConfig.BASE_URL
        )

    def create_context_prompt(self, context_type: str) -> PromptTemplate:
        """Create a context-specific prompt template"""
        return PromptTemplate(
            template="{context}\n\nCustomer Query: {query}\n\nResponse:",
            input_variables=["context", "query"]
        )

    def generate_response(self, context_type: str, query: str) -> str:
        """Generate a contextual response using Ollama"""
        context = SUPPORT_CONTEXTS.get(context_type, SUPPORT_CONTEXTS['product_inquiry'])
        prompt = self.create_context_prompt(context_type)
        
        # Create the full prompt
        full_prompt = prompt.format(context=context, query=query)
        
        # Generate response
        try:
            response = self.llm.invoke(full_prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Request and Response Models
class SupportRequest(BaseModel):
    context: str = Field(default="product_inquiry", description="Support context type")
    query: str = Field(..., description="Customer's support query")

class SupportResponse(BaseModel):
    response: str
    context: str

# FastAPI Applicationc
app = FastAPI(
    title="Laptop Support Chatbot",
    description="AI-powered customer support chatbot for laptop sales"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize the chatbot
chatbot = LaptopSupportChatbot()

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Root endpoint with interactive frontend
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/support")
async def handle_support_request(request: SupportRequest):
    """Handle support requests via REST API"""
    response_text = chatbot.generate_response(
        context_type=request.context, 
        query=request.query
    )
    
    return SupportResponse(
        response=response_text, 
        context=request.context
    )

# Example Usage and Testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Requirements.txt content
"""
fastapi==0.109.0
uvicorn==0.27.0
langchain==0.1.0
langchain-community==0.0.19
pydantic==2.6.0
websockets==12.0
"""