docker run -d \
  --name rtsp-recorder \
  --memory=512m \
  --restart unless-stopped \
  --env-file "./.env" \
  -v "$(pwd)/recordings:/recordings" \
  rtsp-recorder:version
