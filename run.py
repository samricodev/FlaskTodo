from todo import create_app

if __name__ == "__main__":
    app = create_app()
    context = ('./todo/certificates/cert.pem', './todo/certificates/key.pem')  # Location of certificate & key
    app.run(port=4000, ssl_context=context) 
