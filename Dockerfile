FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
COPY . .
RUN uv add --requirements requirements.txt
RUN uv tree
CMD [ "uv", "run", "webdiag.py"]
