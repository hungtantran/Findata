rm -rf gen-py/*
thrift -r --gen py thrift_defs/index_model.thrift
set PYTHONPATH=%PYTHONPATH%;.;gen-py/models;gen-py;Packages/;Packages/thrift;Packages/thrift/transport;Packages/thrift/server;Packages/thrift/protocol;QueryService;Common;
