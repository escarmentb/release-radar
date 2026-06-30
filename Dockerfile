FROM python:3.13-slim AS runtime
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app app
COPY --chown=app:app app ./app
USER 10001
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=2s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/live')"]
ENTRYPOINT ["python", "-m", "app.server"]
