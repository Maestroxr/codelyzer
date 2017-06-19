# DOCKER-VERSION 1.1.0

#inherit from the default container, which have all the needed script to launch tasks
FROM    ingi/inginious-c-cpp
LABEL org.inginious.grading.name="intro" 


# Update yum, install pip, update pip
RUN     yum -y update
RUN 	yum -y install gcc-c++
RUN 	yum -y install python-pip
RUN		pip install --upgrade pip

# Install git
RUN		yum -y install git

# Install Scenario
RUN		pip install git+https://github.com/shlomihod/scenario.git --upgrade

#Install Codelyzer
RUN 	pip install --target=/usr/lib64/python2.7/site-packages git+https://github.com/Maestroxr/codelyzer.git

# Install Vera++
RUN		yum -y localinstall https://copr-be.cloud.fedoraproject.org/results/nocnokneo/oecnav/epel-7-x86_64/vera%2B%2B-1.3.0-1.el7.centos/vera++-1.3.0-1.el7.centos.x86_64.rpm

# Copy vera rules and default profile
COPY	vera/profiles /usr/lib64/vera++/profiles/
COPY	vera/rules /usr/lib64/vera++/rules/


