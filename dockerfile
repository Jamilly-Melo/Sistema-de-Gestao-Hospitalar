FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . ./

# Imagem usada pelo serviço `testes` do docker-compose.yaml, que já sobrescreve
# `command:` com ["uv", "run", "pytest", "-v"]. O CMD abaixo é só o default
# sensato para quando a imagem é rodada isoladamente (sem override).
CMD ["uv", "run", "pytest", "-v"]