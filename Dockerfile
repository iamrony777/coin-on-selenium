FROM seleniarm/standalone-chromium:latest
WORKDIR /app
USER root
COPY ./ /app/
RUN mkdir screenshot cache logs

ENV DEBIAN_FRONTEND="noninteractive"

ENV PYTHONPATH="."

RUN apt update && \
    apt install python3-full python3-dev python3-pip -y

RUN apt install ca-certificates git build-essential gcc -y && \
    apt autoremove -y

RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

CMD ["python3", "coin_in_selenium/app.py"]