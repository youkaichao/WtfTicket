/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-11-30
 * Time: 上午11:43
 */

function check_percent(p) {
    if (p > 100.0) {
        return 100.0;
    } else {
        return p;
    }
}

function checktime(){
    var checklist = ['#input-start-year','#input-start-month','#input-start-day','#input-start-hour','#input-start-minute',
                     '#input-end-year','#input-end-month','#input-end-day','#input-end-hour','#input-end-minute',
                     '#input-book-start-year','#input-book-start-month','#input-book-start-day','#input-book-start-hour','#input-book-start-minute',
                     '#input-book-end-year','#input-book-end-month','#input-book-end-day','#input-book-end-hour','#input-book-end-minute'];
    for(var i in checklist){
        var value = $(checklist[i]).val();
        if (value == '' || value == undefined){
            $(checklist[i]).popover({
                html: true,
                placement: 'top',
                title:'',
                content: '<span style="color:red;">不应为空</span>',
                trigger: 'focus',
                container: 'body'
            });
            $(checklist[i]).focus();
            return false;
        }
    }
    var actstart = new Date($('#input-start-year').val(), $('#input-start-month').val()-1, $('#input-start-day').val(), $('#input-start-hour').val(), $('#input-start-minute').val());
    var actend = new Date($('#input-end-year').val(), $('#input-end-month').val()-1, $('#input-end-day').val(), $('#input-end-hour').val(), $('#input-end-minute').val());
    var bookstart = new Date($('#input-book-start-year').val(), $('#input-book-start-month').val()-1, $('#input-book-start-day').val(), $('#input-book-start-hour').val(), $('#input-book-start-minute').val());
    var bookend = new Date($('#input-book-end-year').val(), $('#input-book-end-month').val()-1, $('#input-book-end-day').val(), $('#input-book-end-hour').val(), $('#input-book-end-minute').val());
    var now = new Date();
    if(locals.activity.status == 0){
        if(bookstart <= now){
            $('#input-book-start-year').popover({
                    html: true,
                    placement: 'top',
                    title:'',
                    content: '<span style="color:red;">“抢票开始时间”应晚于“当前时间”</span>',
                    trigger: 'focus',
                    container: 'body'
            });
            $('#input-book-start-year').focus();
            return false;
        }
    }
    
    if(bookend <= bookstart){
        $('#input-book-end-year').popover({
            html: true,
            placement: 'top',
            title:'',
            content: '<span style="color:red;">“抢票结束时间”应晚于“抢票开始时间”</span>',
            trigger: 'focus',
            container: 'body'
        });
        $('#input-book-end-year').focus();
        return false;
    }

    if(actstart <= bookend){
        $('#input-start-year').popover({
                html: true,
                placement: 'top',
                title:'',
                content: '<span style="color:red;">“活动开始时间”应晚于“订票结束时间”</span>',
                trigger: 'focus',
                container: 'body'
        });
         $('#input-start-year').focus();
        return false;
    }
    if(actend <= actstart){
        $('#input-end-year').popover({
            html: true,
            placement: 'top',
            title:'',
            content: '<span style="color:red;">“活动结束时间”应晚于“活动开始时间”</span>',
            trigger: 'focus',
            container: 'body'
        });
         $('#input-end-year').focus();
        return false;
    }
    return true;
}

function checkname(){
    var name = $('#input-name').val();
    if (name == '') {
        $('#input-name').popover({
                    html: true,
                    placement: 'top',
                    title:'',
                    content: '<span style="color:red;">“活动名称不能为空”</span>',
                    trigger: 'focus',
                    container: 'body'
            });
            $('#input-name').focus();
            return false;
        return false;
    } else {
        return true;
    }
}

function checkticket(){
    var num = $('#input-total_tickets').val();
    if (num == '') {
        $('#input-total_tickets').popover({
                    html: true,
                    placement: 'top',
                    title:'',
                    content: '<span style="color:red;">“抢票数量不能为空”</span>',
                    trigger: 'focus',
                    container: 'body'
            });
            $('#input-total_tickets').focus();
            return false;
        return false;
    } else if(Number(num) <= 0) {
        $('#input-total_tickets').popover({
                    html: true,
                    placement: 'top',
                    title:'',
                    content: '<span style="color:red;">“票数最少设置为1”</span>',
                    trigger: 'focus',
                    container: 'body'
            });
            $('#input-total_tickets').focus();
            return false;
    } else {
        return true;
    }
}

function initialProgress(checked, ordered, total) {
    $('#tickets-checked').css('width', check_percent(100.0 * checked / total) + '%')
        .tooltip('destroy').tooltip({'title': '已检入：' + checked + '/' + ordered + '=' + (100.0 * checked / ordered).toFixed(2) + '%'});
    $('#tickets-ordered').css('width', check_percent(100.0 * (ordered - checked) / total) + '%')
        .tooltip('destroy').tooltip({'title': '订票总数：' + ordered + '/' + total + '=' + (100.0 * ordered / total).toFixed(2) + '%' + '，其中未检票：' + (ordered - checked) + '/' + ordered + '=' + (100.0 * (ordered - checked) / ordered).toFixed(2) + '%'});
    $('#tickets-remain').css('width', check_percent(100.0 * (total - ordered) / total) + '%')
        .tooltip('destroy').tooltip({'title': '余票：' + (total - ordered) + '/' + total + '=' + (100.0 * (total - ordered) / total).toFixed(2) + '%'});
}

var keyMap = {
    'name': 'value',
    'key': 'value',
    'description': 'value',
    'start_time': 'time',
    'end_time': 'time',
    'place': 'value',
    'book_start': 'time',
    'book_end': 'time',
    'pic_url': 'value',
    'total_tickets': 'value',
    'seat_status': 'value'
}, lockMap = {
    'value': function(dom, lock) {
        dom.attr('disabled', lock);
    },
    'text': function(dom, lock) {
        dom.attr('disabled', lock);
    },
    'time': function(dom, lock) {
        var parts = dom.children(), i, len, part;
        for (i = 0, len = parts.length; i < len; ++i) {
            part = $(parts[i]).children();
            if (part.attr('name')) {
                part.attr('disabled', lock);
            }
        }
        dom.attr('disabled', lock);
    }
};

function lockByStatus(status, book_start, start_time, end_time, current_time) {
    // true means lock, that is true means disabled
    var statusLockMap = {
        // saved but not published
        '0': {
        },
        // published
        '1': {
            'name': true,
            'key': true,
            'description': function () {
                return (current_time >= end_time);
            },
            'pic_url': function () {
                return (current_time >= end_time);
            },
            'place': function() {
                return (current_time >= start_time);
            },
            'book_start': true,
            'book_end': function() {
                return (current_time >= start_time);
            },
            'total_tickets': function() {
                return (current_time >= book_start);
            },
            'start_time': function() {
                return (current_time >= end_time);
            },
            'end_time': function() {
                return (current_time >= end_time);
            },
            'seat_status': function() {
                return (current_time >= book_start);
            }
        }
    }, key;
    for (key in keyMap) {
        var flag = !!statusLockMap[status][key];
        if (typeof statusLockMap[status][key] == 'function') {
            flag = statusLockMap[status][key]();
        }
        lockMap[keyMap[key]]($('#input-' + key), flag);
    }
    showPubTipsByStatus(status);
}

function showPubTipsByStatus(status){
    if(status < 1){
        $('#publishBtn').tooltip({'title': '发布后不能修改“活动名称”、“活动代称”和“订票开始时间”'});
        $('#saveBtn').tooltip({'title': '暂存后可以“继续修改”'});
    }
}