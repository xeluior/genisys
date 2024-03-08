import '../imports/ui/App.js';
import moment from 'moment-timezone';

Handlebars.registerHelper('moment', function (time, ago) {
    return moment(time).fromNow(!ago)
});