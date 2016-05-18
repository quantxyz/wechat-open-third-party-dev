$(function () {
    $('#container').on('click', '#show_add', function () {
        $('#add_customvalue').show();
    }).on('click', '#show_edit', function () {
        $('#edit_customvalue').show();
        $('#e_id').val($(this).attr('data-id'));
        $('#e_value').val($(this).attr('data-v'));
        $('#e_copyvalue').val($(this).attr('data-v'));
    }).on('click', '#add_action', function() {
        var a_value = $('#a_value').val();
        if (a_value.length<2) {
            $('#a_error').text('请输入正确的业务类型！');
            $('#a_error').show();
            return;
        }
        $.post('/wxorder/add_customvalue', { name: 'bus_type', value: a_value },
            function(response){
                $('.weui_dialog_confirm').hide();
                if(response=='success') {

                    $('#list_type').load('/wxorder/list_customvalue #list_type');
                    $('#toast_success').show();
                    setTimeout(function () {
                        $('#toast_success').hide();
                    }, 2000);
                } else {
                    $('#toast_fail').show();
                    setTimeout(function () {
                        $('#toast_fail').hide();
                    }, 2000);
                }
        })
    }).on('click', '#a_value', function(){
        $('#a_error').hide();
    }).on('click', '#e_value', function(){
        $('#e_error').hide();
    }).on('click', '#cancel', function() {
        $('.weui_dialog_confirm').hide();
    }).on('click', '#edit_action', function() {
        var e_id = $('#e_id').val();
        var e_value = $('#e_value').val();
        var e_copyvalue = $('#e_copyvalue').val();
        if (e_value == e_copyvalue) {
            $('.weui_dialog_confirm').hide();
            return;
        }
        if (e_value.length<2) {
            $('#e_error').text('请输入正确的业务类型！');
            $('#e_error').show();
            return;
        }
        $.post('/wxorder/edit_customvalue', { id: parseInt(e_id), value: e_value },
            function(response){
                $('.weui_dialog_confirm').hide();
                if(response=='success') {
                    $('#list_type').load('/wxorder/list_customvalue #list_type');
                    $('#toast_success').show();
                    setTimeout(function () {
                        $('#toast_success').hide();
                    }, 2000);
                } else {
                    $('#toast_fail').show();
                    setTimeout(function () {
                        $('#toast_fail').hide();
                    }, 2000);
                }
        });
    }).on('click', '#sync_techuser', function() {
        $('#loadingToast').show();
        $.post('/wxorder/sync_techuser',
            function(response){
                if(response=='success') {
                    $('#list_techuser').load('/wxorder/list_techuser #list_techuser');
                    $('#loadingToast').hide();
                    $('#toast_success').show();
                    setTimeout(function () {
                        $('#toast_success').hide();
                    }, 1000);
                } else {
                    $('#loadingToast').hide();
                    $('#toast_fail').show();
                    setTimeout(function () {
                        $('#toast_fail').hide();
                    }, 1000);
                }
        })
    }).on('click', '#showActionSheet', function () {
        var name=$(this).attr('data-name');
        $('#v_name').text(name);
        $('#e_name').val(name);
        $('#copy_ename').val(name);

        var mobile=$(this).attr('data-m');
        $('#e_mobile').val(mobile);
        $('#copy_emobile').val(mobile);
        $('#tu_id').val($(this).attr('data-id'));
        if (mobile.length==0) mobile='未填写...';
        $('#v_mobile').text(mobile);
        var mask = $('#mask');
        var weuiActionsheet = $('#weui_actionsheet');
        weuiActionsheet.addClass('weui_actionsheet_toggle');
        mask.show()
            .focus()//加focus是为了触发一次页面的重排(reflow or layout thrashing),使mask的transition动画得以正常触发
            .addClass('weui_fade_toggle').one('click', function () {
            hideActionSheet(weuiActionsheet, mask);
        });
        $('#actionsheet_cancel').one('click', function () {
            hideActionSheet(weuiActionsheet, mask);
        });
        $('#view_techuser').one('click', function() {
            hideActionSheet(weuiActionsheet, mask);
            $('#v_dialog').show();
        });
        $('#edit_techuser').one('click', function() {
            hideActionSheet(weuiActionsheet, mask);
            $('#e_dialog').show();
        });
        mask.unbind('transitionend').unbind('webkitTransitionEnd');

        function hideActionSheet(weuiActionsheet, mask) {
            weuiActionsheet.removeClass('weui_actionsheet_toggle');
            mask.removeClass('weui_fade_toggle');
            mask.on('transitionend', function () {
                mask.hide();
            }).on('webkitTransitionEnd', function () {
                mask.hide();
            })
        }
    });
    $('#v_dialog').on('click', '#ok', function() {
       $('#v_dialog').hide();
    });
    $('#e_dialog').on('click', '#cancel', function() {
        $('#e_dialog').hide();
    }).on('click', '#ce_techuser', function() {
        var name = $('#e_name').val();
        var mobile = $('#e_mobile').val();
        var id = $('#tu_id').val();
        if (name==$('#copy_ename').val() && mobile==$('#copy_emobile').val()){
            $('#e_dialog').hide();
            return;
        }
        var error = '';
        if (name.length<2) {error+='姓名不正确，请重新输入';}
        if (mobile.length>0 && mobile.length!=11) {error+='\n手机号码格式错误！';}
        if (error.length>0) {$('#e_error').text(error).show(); return;}
        $.post('/wxorder/edit_techuser',
            { id: parseInt(id), name: name, mobile:mobile },
            function(response) {
                $('.weui_dialog_confirm').hide();
                if(response=='success') {
                    $('#list_techuser').load('/wxorder/list_techuser #list_techuser');
                    $('#toast_success .weui_toast_content').text('更新成功！');
                    $('#toast_success').show();
                    setTimeout(function () {
                        $('#toast_success').hide();
                    }, 2000);
                } else {
                    $('#toast_fail .weui_toast_content').text('更新失败，请稍后重试！');
                    $('#toast_fail').show();
                    setTimeout(function () {
                        $('#toast_fail').hide();
                    }, 2000);
                }
            }
        );
    }).on('click', '#e_name', function() {
        $('#e_error').hide();
    }).on('click', '#e_mobile', function() {
        $('#e_error').hide();
    });
    $('#msg').on('click', '#ok', function() {
        $('#msg').show();
    });
    $('#add_orderinfo').on('change', '#id_tech_user', function() {
        var t_id=$('#id_tech_user option').not(function(){ return !this.selected }).val();
        if (parseInt(t_id)>0) {
            $('#sub_action').text('派单')
        } else {
            $('#sub_action').text('保存')
        }
    });
    $('#msg').on('click', '#ok', function() {
        $('#msg').hide();
        $('#sec_addorder').show();
    });
    $('#list_orderinfo').on('click', '.weui_navbar_item', function () {
        $(this).addClass('weui_bar_item_on').siblings('.weui_bar_item_on').removeClass('weui_bar_item_on');
        $('#list_cont .section').eq($(this).index()).addClass('on').siblings('.on').removeClass('on');

    });
    $('#eval_orderinfo').on('click', '#need_remark', function () {
        $('#id_ce_remark').attr('required', 'required')
    })

    // .container 设置了 overflow 属性, 导致 Android 手机下输入框获取焦点时, 输入法挡住输入框的 bug
    // 相关 issue: https://github.com/weui/weui/issues/15
    // 解决方法:
    // 0. .container 去掉 overflow 属性, 但此 demo 下会引发别的问题
    // 1. 参考 http://stackoverflow.com/questions/23757345/android-does-not-correctly-scroll-on-input-focus-if-not-body-element
    //    Android 手机下, input 或 textarea 元素聚焦时, 主动滚一把
    if (/Android/gi.test(navigator.userAgent)) {
        window.addEventListener('resize', function () {
            if (document.activeElement.tagName == 'INPUT' || document.activeElement.tagName == 'TEXTAREA') {
                window.setTimeout(function () {
                    document.activeElement.scrollIntoViewIfNeeded();
                }, 0);
            }
        })
    }
});
