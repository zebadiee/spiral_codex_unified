from fastapi import FastAPI
from pydantic import BaseModel
from kernel.kernel_mind import KernelMIND

app = FastAPI()
mind = KernelMIND()


class AgentInput(BaseModel):
    agent: str
    glyph: str
    inject: dict = {}


@app.post("/run/agent")
def run_agent(input: AgentInput):
    result = mind.dispatch(input.agent, input.glyph, input.inject)
    return {
        "status": "success",
        "entropy": result.get("entropy", 0.0),
        "result": result,
    }
