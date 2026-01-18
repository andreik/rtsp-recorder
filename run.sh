docker run -d \
  --name rtsp-recorder \
  --memory=512m \
  --restart unless-stopped \
  --env-file "./.env" \
  -v "$(pwd)/recordings:/recordings" \
  192.168.68.55:5005/rtsp-recorder:latest
