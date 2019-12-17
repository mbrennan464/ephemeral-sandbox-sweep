FROM gcr.io/connect-sandbox-224121/connect-wipe
ADD scale_reset.py /app/
ADD reset.yaml /app/
ADD dataflow-wipe.yaml /app/
ENTRYPOINT ["/app/scale_reset.py"]
