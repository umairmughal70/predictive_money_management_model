# 
# Copyright 2020-2022 SpireTech, Inc. All rights reserved.
# Description: 
# Generic Dockerfile for python application

# registry.access.redhat.com/ubi7/python-38:1-41
# Ref: https://catalog.redhat.com/software/containers/ubi7/python-38/5e8388a9bed8bd66f839abb3

ARG PYTH_BASE_IMAGE=registry.access.redhat.com/ubi7/python-38:1-41

FROM ${PYTH_BASE_IMAGE}

LABEL "authur"="Spiretech.co" \
      "source-repo"="git@gitlab.com:ai.spiretech.co/predictivemoneymanagement/inference/predictivemoneymanagement.model.git" \
      "copyright"="Copyright 2020-2022 SpireTech, Inc. All rights reserved."

WORKDIR /code

RUN pip install --upgrade pip

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code

CMD [ "python3", "main.py"]
# CMD ["uvicorn", "app.main:app", "--reload"]
