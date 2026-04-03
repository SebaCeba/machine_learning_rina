from app import __init___simple as app_module

app = app_module.create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
