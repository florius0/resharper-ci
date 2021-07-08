FROM mcr.microsoft.com/dotnet/sdk:3.1-focal

ENV PATH="${PATH}:/root/.dotnet/tools"

RUN apt-get update && \
    apt-get -y install python3-pip

RUN pip3 install rich

RUN dotnet tool install -g --add-source . JetBrains.ReSharper.GlobalTools --version 2020.3.0-*

COPY lib lib

ENTRYPOINT ["./lib/main.py"]
