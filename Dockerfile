FROM python:3-alpine AS builder
WORKDIR /usr/src/app
ENV FIELD_HEIGHT=5
ENV FIELD_WIDTH=4
COPY requirements.txt generate.py ./
RUN pip install --no-cache-dir -r requirements.txt && \
		python generate.py
		
FROM nginx
COPY --from=builder /usr/src/app/static /usr/share/nginx/html
