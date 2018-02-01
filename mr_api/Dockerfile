FROM centos:7
MAINTAINER Steve Baker <steven.a.baker@jpl.nasa.gov>

ENV INSTALL_PATH /mr_api
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN yum install epel-release -y
RUN yum install python34 python34-pip -y
RUN pip3 install -U pip
RUN pip3 install -U virtualenv
RUN virtualenv venv
RUN yum install git -y

RUN yum -y install ssmtp \
    && sed -i 's/^mailhub.*/mailhub=smtp.jpl.nasa.gov:25/' /etc/ssmtp/ssmtp.conf \
    && sed -i 's/^#FromLineOverride=YES.*/FromLineOverride=YES/' /etc/ssmtp/ssmtp.conf \

ADD . $INSTALL_PATH
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install -e .

RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/config.git
RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/ocio_sciencelogic.git
RUN venv/bin/pip install -e ./ocio_sciencelogic
RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/ocio_utilities.git
RUN venv/bin/pip install -e ./ocio_utilities
RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/ocio_remedy.git
RUN venv/bin/pip install -e ./ocio_remedy
RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/mr_utilities.git
RUN venv/bin/pip install -e ./mr_utilities
RUN git clone https://sabaker:ddb307985aaa1986d8bca768440e3d85b3a71298@github.jpl.nasa.gov/sabaker/mr_tasks.git
RUN venv/bin/pip install -e ./mr_tasks

CMD ["venv/bin/python", "mr_api.py"]
