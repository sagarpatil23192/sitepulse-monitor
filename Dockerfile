FROM node:20-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip

COPY monitor ./monitor
COPY dashboard ./dashboard
COPY logs ./logs
COPY start.sh .

RUN pip3 install -r monitor/requirements.txt

RUN cd dashboard && npm install

RUN chmod +x start.sh

EXPOSE 3000

CMD ["./start.sh"]