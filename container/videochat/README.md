This container is based on https://github.com/deburau/galene-docker/ which is MIT licensed Copyright (c) 2021-2022 Werner Fleck

## Build and Testrun:
```
sudo docker build --tag galene .
```

```
# remember to check for the correct IP for the turn server
sudo docker run --name galene \
  --publish 0.0.0.0:8443:8443 \
  --env GALENE_TURN="$(hostname -I | cut -d' ' -f1):1194" \
  --env GALENE_INSECURE=1 \
  --network=host \
  --env GALENE_DATA=/data \
  --env GALENE_GROUPS=/groups \
  --volume $PWD/data:/data \
  --volume $PWD/groups:/groups \
  --volume $PWD/../../client/web:/opt/galene/static/client \
  --rm \
  galene
```

- point browser to https://localhost:8443/group/standard/
- use any user/password
- driver interface: https://localhost:8443/client/index.html
- robot interface: https://localhost:8443/client/galene/robot.html

## ToDo
- get passwords from secrets, not hardcoded password hashes
- replace bind mounts with copy in dockerfile
- overwrite galene /opt/galene/static/index.html to forward to driver interface, maybe add small info message and manual forward link