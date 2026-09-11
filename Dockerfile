FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x install.sh

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN ./install.sh

RUN git --version

ENV PATH="/root/.egit/.venv/bin:${PATH}"

ENTRYPOINT ["egit"]
CMD ["--help"]