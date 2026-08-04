from fastapi import APIRouter


router = APIRouter()


@router.post("/chat")
def chat(
    message: str
):

    message = message.lower()


    if "clean" in message:
        reply = "Clean solar panels regularly to maintain efficiency."

    elif "damage" in message:
        reply = "Check for cracks, hotspots, and loose connections."

    elif "safe" in message:
        reply = "Your solar panel system should be inspected regularly."

    else:
        reply = (
            "I can help with solar panel safety, "
            "maintenance, and damage detection."
        )


    return {
        "message": message,
        "reply": reply
    }