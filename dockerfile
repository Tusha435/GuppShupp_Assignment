FROM node:20-bookworm

WORKDIR /app
COPY . /app/

RUN apt-get update && apt-get install -y python3 python3-pip \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

RUN cd backend && pip install --no-cache-dir -r requirements.txt
RUN cd frontend && npm install && npm run build

CMD ["node", "frontend/server.js"]  # or your real start command
