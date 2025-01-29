#!/bin/bash

# Run FastAPI
cd api
uvicorn main:app --port 5050 &
FASTAPI_PID=$!

# Run Streamlit
cd ..
streamlit run app.py &
STREAMLIT_PID=$!

wait $FASTAPI_PID
wait $STREAMLIT_PID