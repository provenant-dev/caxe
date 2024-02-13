FROM python:3.10.13-alpine3.18 as base-image
FROM base-image as builder

RUN apk add bash patch libsodium-dev linux-headers git gcc musl-dev rustup
RUN rustup-init -y && source $HOME/.cargo/env
ENV PATH="/root/.cargo/bin:${PATH}"
RUN python -m pip install --upgrade pip

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt



FROM base-image
RUN apk update && apk upgrade && apk add bash patch libsodium-dev jq linux-headers
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

COPY --from=builder /usr /usr

RUN addgroup --system --gid 1001 caxe \
  && adduser --system --uid 1001 --disabled-password --shell /bin/false -G caxe caxe
USER caxe

COPY --from=builder --chown=caxe:caxe /app /app
RUN chmod +x /app/scripts/start.sh

CMD /app/scripts/start.sh
