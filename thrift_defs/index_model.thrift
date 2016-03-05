namespace py models 

service ServiceQuery {
   void ping(),

   string get_service_name(),

   list<string> get_indices()
}