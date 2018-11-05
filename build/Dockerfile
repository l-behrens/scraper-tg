FROM hls-c1-n1:5000/base_scraper 
WORKDIR /usr/src/app
COPY requirements.txt ./
#COPY filters.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./
CMD [ "python", "/usr/src/app/scraper.py" ]
