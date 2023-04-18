from . import runMswn

app = runMswn.create_app()

if __name__ == "__main__":
    app.run()
