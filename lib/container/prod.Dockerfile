FROM python:3.11-alpine

ARG BUILT_WHEEL

# Debian setup
# ..............................................................................
#RUN groupadd --gid 2000 devuser \
# && useradd --uid 2000 -g devuser --create-home --shell /bin/bash devuser \
# && su - devuser -c "pip install --user --upgrade pip"

# Alpine setup
# ..............................................................................
RUN addgroup --gid 2000 devuser \
 && adduser -u 2000 -G devuser -D devuser \
 && su - devuser -c "pip install --user --upgrade pip"

ADD ./dist/${BUILT_WHEEL} /tmp

RUN --mount=type=cache,target=/home/devuser/.cache,uid=2000,gid=2000 \
    su -l devuser -c "pip install --user /tmp/${BUILT_WHEEL}[prod]"

CMD /home/devuser/.local/bin/uvicorn --proxy-headers --host 0.0.0.0 --port 8080 --factory auth.rest_api.app:create_app
