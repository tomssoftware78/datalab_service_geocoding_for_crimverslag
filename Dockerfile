#
FROM python:3.9
RUN apt-get update
RUN apt-get install -y cifs-utils nfs-common bash

ENV USERNAME=dummy
ENV PASSW=dummy
ENV SHARE_SRC=//127.0.0.1/DUMMY
ENV MOUNT_POINT=DUMMY
ENV SUBDIR_SRC=DUMMY_SRC
ENV SUBDIR_DEST=DUMMY_DEST

#
WORKDIR /app

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install debugpy

#
COPY ./app /app/

VOLUME /mnt/crimverslag

COPY ./start.sh /app/
RUN chmod +x /app/start.sh


CMD ["/bin/bash", "-c", "/app/start.sh \"$SHARE_SRC\" \"$USERNAME\" \"$PASSW\" \"$MOUNT_POINT\" \"$SUBDIR_SRC\" \"$SUBDIR_DEST\""]