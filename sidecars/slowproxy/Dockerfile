FROM python:3.12
EXPOSE 1223 2423 9623

COPY slow_proxy.py /
CMD ["/usr/local/bin/python3", "-u", "/slow_proxy.py"]
