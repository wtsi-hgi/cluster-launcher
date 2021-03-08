FROM node
COPY . /frontend
WORKDIR /frontend

EXPOSE 8080

RUN npm install
CMD npm run serve -- --mode production
