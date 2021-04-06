FROM python:3.7
COPY . /backend
WORKDIR /backend
ENV PATH "/backend/terraform:${PATH}"
EXPOSE 5000
RUN apt update && apt install -y uuid-runtime
RUN pip install -r requirements.txt
RUN mkdir terraform && cd terraform
RUN wget https://releases.hashicorp.com/terraform/0.13.5/terraform_0.13.5_linux_amd64.zip && unzip terraform_0.13.5_linux_amd64.zip -d terraform
CMD bash +x startup.sh
