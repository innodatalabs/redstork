# How to debug C/C++ code

## Build `dbg` docker image (if not built yet)

```bash
docker build . -f docker/Dockerfile.debug -t dbg
```

## Run container

```bash
docker run -it -v`pwd`:/self -v/home/mike/REDSync/testResources/izguts:/test dbg bash
```

Inside container:

```bash
cd /self/docker
make
```

## Debug it

```bash
gdb ./main
(gdb) run
```