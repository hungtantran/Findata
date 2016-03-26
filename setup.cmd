rm -rf gen-py/*
thrift -r --gen py thrift_defs/index_model.thrift
set PYTHONPATH=%PYTHONPATH%;.;gen-py/models;gen-py;QueryService;Common;Database;Packages/;Packages/thrift;Packages/thrift/transport;Packages/thrift/server;Packages/thrift/protocol;Packages/beautifulsoup/
