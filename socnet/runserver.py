import uvicorn


# настройки для локального запуска сервера в режиме asgi
if __name__ == "__main__":
    uvicorn.run(
        "socnet.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
