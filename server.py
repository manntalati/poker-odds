from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import base64
import json
import asyncio

# Local imports
from detector import CardDetector
from poker import PokerEngine
from ui import draw_ui

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize global components
detector = CardDetector()
poker = PokerEngine()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive base64 image from client
            data = await websocket.receive_text()
            
            # Message format: { "type": "image"|"lock"|"reset", ... }
            message = json.loads(data)
            
            msg_type = message.get('type')
            
            if msg_type == 'lock':
                success = poker.lock_hero_hand()
                await websocket.send_json({"type": "lock_ack", "success": success})
                
            elif msg_type == 'lock_board':
                success = poker.lock_community()
                await websocket.send_json({"type": "lock_board_ack", "success": success, "count": poker.community_locked_count})

            elif msg_type == 'set_manual':
                # { type: 'set_manual', card_type: 'hero'|'community', index: 0..4, label: 'Ah' }
                success = poker.set_manual_card(message.get('card_type'), message.get('index'), message.get('label'))
                await websocket.send_json({"type": "manual_ack", "success": success})

            elif msg_type == 'reset':
                poker.reset_hand()
                await websocket.send_json({"type": "reset_ack"})
            
            elif msg_type == 'image':
                try:
                    # Decode image
                    encoded_data = message['data'].split(',')[1]
                    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                    
                    if nparr.size == 0:
                        continue
                        
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        continue
                except Exception as e:
                    print(f"Image decode error: {e}")
                    continue

                # Update settings
                num_players = int(message.get('num_players', 2))
                poker.set_num_players(num_players)

                # Detection & Logic
                try:
                    cards = detector.detect(frame)
                    poker.update_state(cards)
                    odds = poker.calculate_odds()
                    
                    # Add hero info to response
                    from treys import Card
                    hero_cards = [Card.int_to_str(c) for c in poker.hero_hand]
                    community_cards = [Card.int_to_str(c) for c in poker.community_cards]
                    
                    response = {
                        "type": "result",
                        "odds": odds,
                        "cards": [c['label'] for c in cards], # debug info for detected
                        "hero_hand": hero_cards,
                        "community_cards": community_cards,
                        "hero_locked": poker.hero_hand_locked
                    }
                    
                    await websocket.send_json(response)
                
                except Exception as e:
                    print(f"Processing error: {e}")
                    await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        print("Client disconnected")
