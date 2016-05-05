import jQuery from 'jquery';

class Network {
    static sendGet(options, success) {
        jQuery.ajax(options).done(success);
    }
}

export default Network;