rm -rf gen-py/*
thrift -r --gen py thrift_defs/index_model.thrift
set PYTHONPATH=%PYTHONPATH%;gen-py/models;gen-py;.;thrift;thrift/transport;thrift/server;thrift/protocol
