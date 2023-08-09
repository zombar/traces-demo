echo "---> [Building app image]"
docker $BUILDX build $FLAGSX -t ghcr.io/zombar/traces-demo:latest -f - . <<EOF
FROM python:3.11

COPY ./ /app/

WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install "uvicorn[standard]"

ENTRYPOINT ["python", "utils.py"]
EOF