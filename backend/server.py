from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from PIL import Image
import io
import base64
import re
from pymongo import MongoClient
import uuid
from datetime import datetime
import json

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        genai_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini AI: {e}")
        genai_model = None

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['sightmate']
history_collection = db['analysis_history']

def optimize_image(image: Image.Image, max_size: tuple = (1024, 1024)) -> Image.Image:
    """Optimize image for API processing"""
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    return image

@app.get("/")
def read_root():
    return {"message": "SightMate API is running"}

@app.post("/api/vision/objects")
async def detect_objects(file: UploadFile = File(...)):
    """Detect objects in image for visually impaired users"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
            
        if not genai_model:
            raise HTTPException(status_code=500, detail="Gemini AI model not available")
            
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image = optimize_image(image)
        
        # Object detection prompt optimized for accessibility
        prompt = """
        You are an AI assistant helping visually impaired people. Analyze this image and describe what you see in a clear, helpful way.

        Focus on:
        1. Main objects and their approximate locations (left, right, center, near, far)
        2. People (how many, what they're doing, approximate distance)
        3. Important details for navigation and safety
        4. Any text or signs visible

        Keep the description concise but informative. Speak as if you're helping someone navigate their environment.
        Start with the most important things they should know about first.
        """
        
        response = genai_model.generate_content([prompt, image])
        description = response.text
        
        # Save to history
        history_record = {
            "id": str(uuid.uuid4()),
            "type": "object_detection",
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "image_size": f"{image.width}x{image.height}"
        }
        history_collection.insert_one(history_record)
        
        return {
            "success": True,
            "description": description,
            "type": "objects",
            "timestamp": history_record["timestamp"]
        }
        
    except Exception as e:
        print(f"Object detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Object detection failed: {str(e)}")

@app.post("/api/vision/currency")
async def detect_currency(file: UploadFile = File(...)):
    """Detect currency and monetary amounts in image"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
            
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image = optimize_image(image)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        You are helping a visually impaired person identify money and currency. 
        
        Analyze this image and tell me:
        1. Any paper bills - what denomination and currency (dollars, euros, etc.)
        2. Any coins - what type and value
        3. Any digital displays showing amounts
        4. Any credit cards or payment cards visible
        
        Be very specific about amounts and currency types. If you can't clearly identify the denomination, say so.
        Speak as if you're directly helping them handle their money safely.
        """
        
        response = model.generate_content([prompt, image])
        description = response.text
        
        # Try to extract specific amounts
        currency_patterns = {
            'USD': r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'EUR': r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'GBP': r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        }
        
        detected_amounts = {}
        for currency, pattern in currency_patterns.items():
            matches = re.findall(pattern, description)
            if matches:
                detected_amounts[currency] = matches
        
        # Save to history
        history_record = {
            "id": str(uuid.uuid4()),
            "type": "currency_detection",
            "description": description,
            "detected_amounts": detected_amounts,
            "timestamp": datetime.now().isoformat()
        }
        history_collection.insert_one(history_record)
        
        return {
            "success": True,
            "description": description,
            "detected_amounts": detected_amounts,
            "type": "currency",
            "timestamp": history_record["timestamp"]
        }
        
    except Exception as e:
        print(f"Currency detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Currency detection failed: {str(e)}")

@app.post("/api/vision/text")
async def read_text(file: UploadFile = File(...)):
    """Extract and read text from image using OCR"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
            
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image = optimize_image(image)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        You are helping a visually impaired person read text. 
        
        Extract ALL text from this image and organize it in a clear, readable way.
        - If it's a document, read it in logical order (top to bottom, left to right)
        - If it's a sign or label, be clear about what it says
        - If text is partially obscured or unclear, mention that
        - Include any numbers, prices, or important details
        
        Present the text as if you're reading it aloud to help them understand the content.
        """
        
        response = model.generate_content([prompt, image])
        text_content = response.text
        
        # Save to history
        history_record = {
            "id": str(uuid.uuid4()),
            "type": "text_reading",
            "text_content": text_content,
            "timestamp": datetime.now().isoformat()
        }
        history_collection.insert_one(history_record)
        
        return {
            "success": True,
            "text_content": text_content,
            "type": "text",
            "timestamp": history_record["timestamp"]
        }
        
    except Exception as e:
        print(f"Text reading error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text reading failed: {str(e)}")

@app.post("/api/vision/colors")
async def detect_colors(file: UploadFile = File(...)):
    """Detect dominant colors in the image"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
            
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image = optimize_image(image)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        You are helping a visually impaired person understand colors in their environment.
        
        Analyze this image and describe:
        1. The main colors you see (be specific: light blue, dark red, etc.)
        2. What objects have which colors
        3. The overall lighting (bright, dim, natural light, artificial light)
        4. Any color patterns or interesting color combinations
        
        Speak clearly and be descriptive about the colors as if helping someone visualize their surroundings.
        """
        
        response = model.generate_content([prompt, image])
        color_description = response.text
        
        # Save to history
        history_record = {
            "id": str(uuid.uuid4()),
            "type": "color_detection",
            "color_description": color_description,
            "timestamp": datetime.now().isoformat()
        }
        history_collection.insert_one(history_record)
        
        return {
            "success": True,
            "color_description": color_description,
            "type": "colors",
            "timestamp": history_record["timestamp"]
        }
        
    except Exception as e:
        print(f"Color detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Color detection failed: {str(e)}")

@app.get("/api/history")
async def get_history(limit: int = 10):
    """Get recent analysis history"""
    try:
        history = list(history_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.post("/api/emergency/sos")
async def emergency_sos(contact_info: dict):
    """Handle emergency SOS requests"""
    try:
        # In a real app, this would send SMS/email to emergency contacts
        # For now, we'll just log the emergency request
        emergency_record = {
            "id": str(uuid.uuid4()),
            "type": "emergency_sos",
            "contact_info": contact_info,
            "timestamp": datetime.now().isoformat(),
            "status": "initiated"
        }
        
        # Save emergency request
        emergency_collection = db['emergency_requests']
        emergency_collection.insert_one(emergency_record)
        
        return {
            "success": True,
            "message": "Emergency SOS initiated",
            "emergency_id": emergency_record["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency SOS failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
