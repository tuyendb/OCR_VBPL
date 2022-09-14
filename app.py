import uvicorn

if __name__ == "__main__":
    uvicorn.run("apis.api:app", host="0.0.0.0", port=6666, reload=False, log_level="debug", debug=True,
                workers=1, factory=False, loop="asyncio", timeout_keep_alive=120)
