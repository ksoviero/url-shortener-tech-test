build:
	docker build -t pw/url-shortener:latest .

run: build
	docker run -it --rm -p 8000:8000/tcp -v ./:/app/db --name url-shortener pw/url-shortener:latest
