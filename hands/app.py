from app import create_app

app = create_app()

if __name__ == "__main__":
    # Start the Flask development server
    # debug=True enables hot reload and better error messages
    app.run(debug=True, host="0.0.0.0", port=5000)