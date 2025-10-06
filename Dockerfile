#
FROM python:3.9
RUN apt-get update
RUN apt-get install -y cifs-utils nfs-common bash
 
WORKDIR /app
 
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install debugpy
 
COPY ./app /app/
COPY ./start.sh /app/
RUN chmod +x /app/start.sh

VOLUME /mnt/crimverslag
 
ENV USERNAME=""
ENV PASSW=""
ENV SHARE_SRC=""
ENV MOUNT_POINT="/mnt/crimverslag"
ENV SUBDIR_SRC=""
ENV SUBDIR_DEST=""

CMD ["/bin/bash", "-c", "/app/start.sh \"$SHARE_SRC\" \"$USERNAME\" \"$PASSW\" \"$MOUNT_POINT\" \"$SUBDIR_SRC\" \"$SUBDIR_DEST\""]