# Urban-Barnacle
It's a multistep OCR project 

1. truncate_pdf.py - cuts out any excess in each page of the pdf, producing a minimal pdf
2. img_pdf_ocr.py - visualizes the truncated pdf and inserts findings into db
3. minimize_pdf.py - reads db and builds a pdf of just the relevant findings
4. verify_current.py - reads db and verifies the entry is still current from the online list

## Running instructions 
1. build docker image
2. run docker image `docker run -itv /local_docs:/docs tomecho/urban-barnacle pipenv run bash -c "pipenv install; python2 SCRIPT ARGS"`
3. recover files from container 
    * `docker cp container:/app/output.db /root/output.db`

## Performance considerations
* i/o and cpu heavy, ram not so much
* 2 vCores and 4gb of ram will result in process crashing
* past 4 vCores it doesn't seem to effect anything, there isn't much going on in parallel