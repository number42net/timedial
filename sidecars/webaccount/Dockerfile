FROM python
RUN mkdir /opt/webaccount
COPY * /opt/webaccount
COPY templates /opt/webaccount/templates
RUN pip3 install -r /opt/webaccount/requirements.txt

WORKDIR /opt/webaccount

EXPOSE 5000
CMD ["python3", "site.py"]
