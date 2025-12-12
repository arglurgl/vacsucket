This container is based on https://github.com/deburau/galene-docker/ which is MIT licensed Copyright (c) 2021-2022 Werner Fleck

## Build and Run:
```
sudo docker build --tag galene .
```

```
sudo docker run --name galene \
  --publish 127.0.0.1:8443:8443 \
  --env GALENE_DATA=/data \
  --env GALENE_GROUPS=/groups \
  --volume $PWD/data:/data \
  --volume $PWD/groups:/groups \
  galene
```

- point browser to https://localhost:8443/group/standard/
- user: pleasedont password: hackcutethings 

## ToDo
- add proper users and groups with sensible permissions
- get passwords from secrets, not hardcoded test passwords