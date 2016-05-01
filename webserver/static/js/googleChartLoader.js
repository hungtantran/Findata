import Q from 'q';
import Network from './network';


class _GoogleChartLoader {
    constructor() {
        this.loading = false;
        this.loaded = false;
        this.promise = Q.defer();
    }

    load() {
        if (this.loading) {
            return this.promise.promise;
        }

        this.loading = true

        var options = {
            dataType: "script",
            cache: true,
            url: "https://www.gstatic.com/charts/loader.js",
        }

        Network.sendGet(options, () => {
            google.charts.load('current', {'packages':['line']});
            google.charts.setOnLoadCallback(() => {
                this.loaded = true;
                this.promise.resolve();
            })
        })

        return this.promise.promise;
    }
}

var GoogleChartLoader = new _GoogleChartLoader()

export default GoogleChartLoader;