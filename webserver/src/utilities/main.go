package main

func main() {
	var config *ProdConfig;
    config.initializeConfig();

	PopulateTickerInfo();
	PopulateExchangeIndexInfo();
	PopulateEconomicsInfo();
}