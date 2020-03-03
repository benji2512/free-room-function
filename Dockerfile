FROM openfaas/classic-watchdog:0.18.8 as watchdog

FROM python:3.7-alpine

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

WORKDIR /root/

COPY handler.py .
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV fprocess="python3 handler.py"

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]