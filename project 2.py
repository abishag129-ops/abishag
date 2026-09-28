import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="ComicCraft Backend")

# Initialize Gemini Client (set GEMINI_API_KEY in your environment)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class ComicRequest(BaseModel):
    theme: str
    num_panels: int = 4

@app.post("/api/generate-comic")
async def generate_comic_story(request: ComicRequest):
    prompt = f"""
    You are an expert comic book creator.
    Generate a {request.num_panels}-panel comic strip storyline based on this theme:
    "{request.theme}"

    For each panel, provide:
    1. "panel_number": integer
    2. "visual_description": detailed prompt to generate comic art for this panel
    3. "dialogue": text spoken or caption for the panel
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "panel_number": {"type": "INTEGER"},
                            "visual_description": {"type": "STRING"},
                            "dialogue": {"type": "STRING"}
                        },
                        "required": ["panel_number", "visual_description", "dialogue"]
                    }
                }
            )
        )
        return {"comic": json.loads(response.text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("route:app", host="0.0.0.0", port=8000, reload=True)