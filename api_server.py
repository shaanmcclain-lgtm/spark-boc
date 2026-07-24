from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import omni_drive_wasd as odw

app = FastAPI(title="SparkyBotMini REST API")
logger = logging.getLogger("uvicorn")


class PowerRequest(BaseModel):
    power: int


class MoveRequest(BaseModel):
    direction: str  # 'forward', 'backward', 'left', 'right'
    power: Optional[int] = None  # optional override


@app.post("/connect")
async def connect():
    """Connect to the robot. Uses the mr_sparky instance from omni_drive_wasd."""
    try:
        ok = odw.mr_sparky.connect()
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to connect to robot")
        return {"connected": True}
    except Exception as e:
        logger.exception("Error connecting to robot")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/disconnect")
async def disconnect():
    """Disconnect and stop motors."""
    try:
        odw.stop_motors()
        # call disconnect if available
        if hasattr(odw.mr_sparky, "disconnect"):
            odw.mr_sparky.disconnect()
        return {"disconnected": True}
    except Exception as e:
        logger.exception("Error disconnecting")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/power")
async def set_power(req: PowerRequest):
    """Set default power (1-100)"""
    p = req.power
    if not (1 <= p <= 100):
        raise HTTPException(status_code=400, detail="Power must be between 1 and 100")
    odw.current_power = p
    return {"power": odw.current_power}


@app.post("/move")
async def move(req: MoveRequest):
    """Move in a direction. Optional power override."""
    direction = req.direction.lower()
    power = req.power if req.power is not None else odw.current_power
    if not (1 <= power <= 100):
        raise HTTPException(status_code=400, detail="Power must be between 1 and 100")

    try:
        if direction == "forward":
            odw.move_forward(power)
        elif direction == "backward":
            odw.move_backward(power)
        elif direction == "left":
            odw.move_left_strafe(power)
        elif direction == "right":
            odw.move_right_strafe(power)
        else:
            raise HTTPException(status_code=400, detail="Unknown direction")
        return {"moving": direction, "power": power}
    except Exception as e:
        logger.exception("Error sending move command")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop")
async def stop():
    """Stop all motors immediately."""
    try:
        odw.stop_motors()
        return {"stopped": True}
    except Exception as e:
        logger.exception("Error stopping motors")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """Return basic status. Note: mr_sparky connection attribute may vary by SparkyBotMini implementation."""
    # Best-effort connection detection
    connected = None
    try:
        # common attribute names: connected, is_connected
        if hasattr(odw.mr_sparky, "connected"):
            connected = bool(getattr(odw.mr_sparky, "connected"))
        elif hasattr(odw.mr_sparky, "is_connected"):
            attr = getattr(odw.mr_sparky, "is_connected")
            connected = attr() if callable(attr) else bool(attr)
        else:
            # unknown; leave as None
            connected = None
    except Exception:
        connected = None

    return {
        "connected": connected,
        "power": odw.current_power,
        "running": getattr(odw, "running", None),
    }
