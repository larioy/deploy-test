/**
 * Created by kido on 2016/10/11.
 */
function set_ztree(newSet, tree_id, tree_server) {
    var opts = $.extend({
        onClick: function (event, treeId, treeNode) {
            //点击事件
        },
        onAddClick: function (treeId, treeNode) {
            //点击添加按钮事件
        },
        onRemoveClick: function (treeId, treeNode) {
            //点击删除按钮事件
        },
        showRemoveBtn: false,//显示删除按钮
        showAddBtn: false,//显示添加按钮
        asyncUrl: '',//点击加号访问接口地址，获取子级数据
        check: {},//复选框设置
        autoParam: [],//接口参数
        data: {
            key: {
                // name: "displayName"
                name: "name",//树形图显示字段
            }
        },
        enableAsyn: true,//开启加号接口访问
        onCheck: function (event, treeId, treeNode) {
        }//选中事件
    }, newSet);
    var viewSetting;

    var addHoverDom = function (treeId, treeNode) {
        var aObj = $("#" + treeNode.tId + "_a");
        if ($("#diyBtn_" + treeNode.id).length > 0) return;
        var editStr = "<a class='treeAdd' style='width:18px;margin-left:3px;' id='diyBtn_" + treeNode.id
            + "'onfocus='this.blur();'></a>";
        aObj.append(editStr);
        var btn = $("#diyBtn_" + treeNode.id);
        if (btn) btn.bind("click", function () {
            opts.onAddClick(treeId, treeNode);
        });
    };

    var removeHoverDom = function (treeId, treeNode) {
        $("#diyBtn_" + treeNode.id).unbind().remove();
        $("#diyBtn_space_" + treeNode.id).unbind().remove();
    };

    if (opts.showAddBtn) {
        viewSetting = {
            addHoverDom: addHoverDom,
            removeHoverDom: removeHoverDom
        };
    }
    else {
        viewSetting = {};
    }

    var setting = {
        callback: {
            onClick: opts.onClick,
            beforeRemove: opts.onRemoveClick,
            onCheck: opts.onCheck
        },
        async: {
            enable: opts.enableAsyn,
            type: "get",
            url: opts.asyncUrl,
            autoParam: opts.autoParam,
            otherParam: opts.otherParam
        },
        edit: {
            enable: true,
            showRemoveBtn: opts.showRemoveBtn,
            showRenameBtn: false,
            removeTitle: "删除组织",
            drag: {
                isCopy: false,
                isMove: false
            }
        },
        data: opts.data,
        view: viewSetting,
        check: opts.check
    };
    $.fn.zTree.init($(tree_id), setting, tree_server);
}




