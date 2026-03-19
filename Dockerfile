FROM python:3.12-slim

ARG VERSION=dev
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="rtsp-recorder" \
  org.opencontainers.image.description="Lightweight RTSP video recorder with date-based segmented output" \
  org.opencontainers.image.version="${VERSION}" \
  org.opencontainers.image.revision="${VCS_REF}"

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY record.py /app/record.py

CMD ["python", "-u", "/app/record.py"]
