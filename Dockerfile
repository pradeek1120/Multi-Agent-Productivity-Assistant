FROM python:3.12-slim

ARG TOOLBOX_VERSION=0.28.0
ARG TARGETOS=linux
ARG TARGETARCH=amd64

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -L "https://storage.googleapis.com/genai-toolbox/v${TOOLBOX_VERSION}/${TARGETOS}/${TARGETARCH}/toolbox" \
    -o /usr/local/bin/toolbox \
    && chmod +x /usr/local/bin/toolbox

COPY . .

ENV PYTHONUNBUFFERED=1
ENV TOOLBOX_COMMAND=toolbox
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn productivity_agent.demo_api:app --host 0.0.0.0 --port ${PORT:-8080}"]
