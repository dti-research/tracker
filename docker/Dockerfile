FROM ubuntu:18.04

RUN apt-get update && apt-get install -y --no-install-recommends \
         cmake \
         git \
         python3-dev \ 
         python3-pip \
         python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN git clone https://github.com/dti-research/tracker && cd tracker && pip3 install -e .

# Enable bash autocompletion for Tracker on boot
RUN echo ""  >> ~/.bashrc
RUN echo "# Bash autocompletion for Tracker"  >> ~/.bashrc
RUN echo 'eval "$(_TRACKER_COMPLETE=source tracker)"'  >> ~/.bashrc

# Export for Click autocompletion
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
