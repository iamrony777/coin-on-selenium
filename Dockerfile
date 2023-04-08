FROM seleniarm/standalone-chromium:latest
WORKDIR /app
USER seluser
COPY ./ /app/
RUN mkdir screenshot cache logs

ENV DEBIAN_FRONTEND="noninteractive"

ENV PYTHONPATH="."

RUN sudo apt update && \
    sudo apt install python3-full python3-dev python3-pip -y

RUN sudo apt install ca-certificates git build-essential gcc -y && \
    sudo apt autoremove -y

RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

CMD ["bash"]