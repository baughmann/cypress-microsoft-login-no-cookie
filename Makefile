start_server: # Starts the FastAPI server for the app
	@uv run fastapi dev backend/main.py --port 9090

start_cypress: # Opens the cypress test runner
	cd client && npm run cypress:open

client: # Run this after making changes to the client code
	cd client && npm run build
	rm -rf app2/static
	mkdir -p app2/static
	cp -r client/dist/* app2/static/

start: client # Starts both app one and app two
	@make -j2 start_server start_cypress