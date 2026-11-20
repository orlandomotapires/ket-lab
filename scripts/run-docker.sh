#!/bin/sh
# Starts Ket Lab with Docker and gives the terminal back once it is ready.
#
#   curl -fsSL https://raw.githubusercontent.com/orlandomotapires/ket-lab/main/scripts/run-docker.sh | sh
#   sh scripts/run-docker.sh v0.4.0        # a given release instead of the latest one
#
# Prefix `sh` with sudo if your user is not in the docker group. KET_LAB_PORT changes the port
# (default 8080). Progress is kept in the Docker volume ket-lab-progress.
set -eu

VERSION="${1:-latest}"
IMAGE="ghcr.io/orlandomotapires/ket-lab:$VERSION"
PORT="${KET_LAB_PORT:-8080}"
# Show the docker commands the way the user has to type them.
SUDO=""
if [ -n "${SUDO_USER:-}" ]; then SUDO="sudo "; fi

# Fail early, with the fix, when Docker cannot be reached.
if ! problem=$(docker info 2>&1 > /dev/null); then
  case "$problem" in
    *"permission denied"*)
      echo "Your user is not allowed to use Docker. Run the command again with sudo before sh (not before curl):" >&2
      echo "  curl -fsSL https://raw.githubusercontent.com/orlandomotapires/ket-lab/main/scripts/run-docker.sh | sudo sh" >&2
      echo "Or join the docker group once (sudo usermod -aG docker \$USER, then log out and in) to drop the sudo." >&2
      ;;
    *)
      echo "Docker is not reachable. Is it installed and running? It said:" >&2
      echo "  $problem" >&2
      ;;
  esac
  exit 1
fi

docker pull "$IMAGE"

# The container is named after the release (ket-lab-v0.4.0), also when "latest" was pulled.
if [ "$VERSION" = latest ]; then
  LABEL=$(docker image inspect -f '{{ index .Config.Labels "org.opencontainers.image.version" }}' "$IMAGE" 2>/dev/null || true)
  if [ -n "$LABEL" ] && [ "$LABEL" != "<no value>" ]; then VERSION="$LABEL"; fi
fi
NAME="ket-lab-$VERSION"
URL="http://localhost:$PORT"

running() { docker ps -q --filter "name=^${NAME}\$" | grep -q .; }

if running; then
  echo
  echo "Ket Lab is already running: open $URL in your browser."
  echo "The container is \"$NAME\" (${SUDO}docker ps lists it, ${SUDO}docker stop $NAME stops it)."
  exit 0
fi

# The origins must match the address you open, so they follow the port.
docker run -d --rm --name "$NAME" -p "127.0.0.1:$PORT:8080" -v ket-lab-progress:/data "$IMAGE" \
  --allow-origin "http://localhost:$PORT" --allow-origin "http://127.0.0.1:$PORT" > /dev/null

# The engine prints {"event": "ready", ...} once it accepts connections (a few seconds).
waited=0
until docker logs "$NAME" 2>&1 | grep -q '"ready"'; do
  if ! running; then
    echo "Ket Lab stopped while starting. To see why, run it in the foreground:" >&2
    echo "  ${SUDO}docker run --rm -p 127.0.0.1:$PORT:8080 -v ket-lab-progress:/data $IMAGE" >&2
    exit 1
  fi
  waited=$((waited + 1))
  if [ "$waited" -ge 120 ]; then
    echo "Ket Lab did not become ready in 2 minutes. Its log: ${SUDO}docker logs $NAME" >&2
    exit 1
  fi
  sleep 1
done

echo
echo "Ket Lab is up and running: open $URL in your browser."
echo "The container is \"$NAME\": ${SUDO}docker ps lists it, ${SUDO}docker stop $NAME stops it."
echo "Your progress stays in the ket-lab-progress volume when the container stops."
