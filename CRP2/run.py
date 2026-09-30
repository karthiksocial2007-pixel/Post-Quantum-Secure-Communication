from app import create_app


app = create_app()


if __name__ == "__main__":

    # use_reloader=False keeps the in-memory Alice/Bob session stable
    # during a demo (the reloader would restart and reset it on file edits)
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
