
import time
import platform

import psutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Carbon-Aware Self-Healing DevOps Pipeline",
    description="Failure detection, automated recovery and carbon-aware DevOps.",
    version="1.0.0"
)

START_TIME = time.time()

application_state = {
    "status": "healthy",
    "failure_reason": None,
    "last_recovery_time": None,
    "failure_count": 0,
    "recovery_count": 0
}


class FailureRequest(BaseModel):
    reason: str = Field(
        default="Simulated application failure",
        max_length=200
    )


class RecoveryRequest(BaseModel):
    action: str = Field(
        default="manual_recovery",
        max_length=100
    )


@app.get("/")
def home():
    return {
        "project": "Carbon-Aware Self-Healing DevOps Pipeline",
        "application": "Demo Service",
        "version": "1.0.0",
        "status": application_state["status"],
        "message": "Application is running"
    }


@app.get("/health")
def health_check():
    if application_state["status"] != "healthy":
        raise HTTPException(
            status_code=503,
            detail={
                "status": application_state["status"],
                "message": "Application is unhealthy"
            }
        )

    return {
        "status": "healthy",
        "message": "Application is operational",
        "timestamp": time.time()
    }


@app.get("/status")
def get_status():
    return {
        "application_status": application_state["status"],
        "failure_reason": application_state["failure_reason"],
        "failure_count": application_state["failure_count"],
        "recovery_count": application_state["recovery_count"],
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "last_recovery_time": application_state["last_recovery_time"]
    }


@app.get("/metrics-data")
def get_metrics():
    cpu_usage = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()
    process = psutil.Process()

    process_memory_mb = (
        process.memory_info().rss / (1024 * 1024)
    )

    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": memory.percent,
        "available_memory_mb": round(
            memory.available / (1024 * 1024), 2
        ),
        "process_memory_mb": round(process_memory_mb, 2),
        "platform": platform.system(),
        "timestamp": time.time(),
        "measurement_type": "actual_host_metrics"
    }


@app.post("/simulate/failure")
def simulate_failure(request: FailureRequest):
    if application_state["status"] != "healthy":
        raise HTTPException(
            status_code=409,
            detail="Application is already unhealthy"
        )

    application_state["status"] = "failed"
    application_state["failure_reason"] = request.reason
    application_state["failure_count"] += 1

    return {
        "message": "Failure simulated successfully",
        "status": application_state["status"],
        "reason": request.reason
    }


@app.post("/simulate/recovery")
def simulate_recovery(request: RecoveryRequest):
    if application_state["status"] == "healthy":
        return {
            "message": "Application is already healthy",
            "status": "healthy"
        }

    application_state["status"] = "healthy"
    application_state["failure_reason"] = None
    application_state["recovery_count"] += 1
    application_state["last_recovery_time"] = time.time()

    return {
        "message": "Application recovered successfully",
        "recovery_action": request.action,
        "status": application_state["status"]
    }
