## Build and Testrun:
```
# in vacsucket root dir:
sudo docker build --tag controlserver -f container/controlserver/Dockerfile .
```

```
sudo docker run --name controlserver \
  --publish 0.0.0.0:8765:8765 \
  --device=/dev/ttyUSB0 \
  --volume /home/pi/assets:/assets \
  controlserver
```