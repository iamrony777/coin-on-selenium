FROM seleniarm/standalone-firefox:latest

WORKDIR /app
COPY ./ /app/
RUN mkdir screenshot

ENV PYTHONPATH="." \
    PATH="${PATH}:${HOME}/.local/bin"

RUN sudo apt-get update

RUN sudo apt-get install python3-pip -y && \
    sudo apt-get autoremove -y

RUN pip3 install --no-cache-dir -U poetry

RUN poetry install --no-ansi --no-cache --without=dev

CMD ["poetry", "run", "python3", "coin_in_selenium/app.py"]