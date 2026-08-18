from pydantic import BaseModel

class State(BaseModel):
    """
    State class to represent the state of the application.
    """
    # Add your state attributes here
    query: str
