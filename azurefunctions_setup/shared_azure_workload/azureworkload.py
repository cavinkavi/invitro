import time
import socket
import json
import azure.functions as func
import logging
from time import perf_counter

# Global variable for hostname
hostname = socket.gethostname()

# Simulate the busySpin function
def busy_spin(duration_ms: int) -> None:
    end_time = perf_counter() + duration_ms / 1000  # Convert ms to seconds
    while perf_counter() < end_time:
        continue

# Convert TraceFunctionExecution
def trace_function_execution(start: float, time_left_milliseconds: int) -> str:
    time_consumed_milliseconds = int((time.time() - start) * 1000)
    if time_consumed_milliseconds < time_left_milliseconds:
        time_left_milliseconds -= time_consumed_milliseconds
        if time_left_milliseconds > 0:
            busy_spin(time_left_milliseconds)

    return f"OK - {hostname}"

# The handler function for Azure Functions (Python)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request.")

    start_time = time.time()

    # Parse JSON request body
    try:
        req_body = req.get_json()
        logging.info(f"Request body: {req_body}")
    except ValueError:
        logging.error("Invalid JSON received.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    runtime_milliseconds = req_body.get('RuntimeInMilliSec', 1000)
    memory_mebibytes = req_body.get('MemoryInMebiBytes', 128)

    logging.info(f"Runtime requested: {runtime_milliseconds} ms, Memory: {memory_mebibytes} MiB")

    # Trace the function execution (busy work simulation)
    result_msg = trace_function_execution(start_time, runtime_milliseconds)

    # Prepare the response
    response = {
        "Status": "Success",
        "Function": req.url.split("/")[-1],
        "MachineName": hostname,
        "ExecutionTime": int((time.time() - start_time) * 1_000_000), 
        "DurationInMicroSec": int((time.time() - start_time) * 1_000_000),
        "MemoryUsageInKb": memory_mebibytes * 1024,
        "Message": result_msg
    }

    logging.info(f"Response: {response}")

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )

