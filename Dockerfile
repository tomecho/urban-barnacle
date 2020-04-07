FROM ubuntu

WORKDIR /app

RUN apt update && apt install -y python python-pip wget imagemagick tesseract-ocr sqlite3
RUN pip install pipenv
RUN pipenv install

COPY . .
RUN cp -r ./etc/* /etc
#RUN bash ./install_geckodriver.sh

CMD BASH