if __name__ == "__main__":
    from dotenv import load_dotenv
    import uvicorn
    import argparse

    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=args.reload,
    )
