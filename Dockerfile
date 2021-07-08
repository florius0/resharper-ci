FROM mcr.microsoft.com/dotnet/sdk:3.1-focal

COPY lib lib

RUN apt-get update && \
    apt-get update && \
    apt-get -y install python3-pip

RUN pip3 install rich

ENV PATH="${PATH}:/root/.dotnet/tools"

RUN dotnet tool install -g --add-source . JetBrains.ReSharper.GlobalTools --version 2020.3.0-*

CMD ["./lib/main.py"]