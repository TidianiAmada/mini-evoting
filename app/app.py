from app import create_app


app = create_app()


# To run the app if app.py is called directly
if __name__ == '__main__':
    
    app.run(debug=True)