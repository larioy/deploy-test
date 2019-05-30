/**
 * Created by Iven on 2016/10/24.
 */
var selectItems = [];
var height = auto_height(195);
var height_add = auto_height(430);
var dataSource_add = [
//    {account_name:"iven",mail_address:"iven@canway.net",id:1234}
];
$(function () {
    $("#user_business_list").css("height", height);
    get_user_business_list();
});

$('.ui-dialog-title').css({"fontSize":"15px"});

var grid_option_add = {
    pageable:false,
    selectable: "multiple",
    height: height_add,
    dataSource: {
        data: dataSource_add
    },
    columns:[
        {
            title: '<input type=\'checkbox\' id=\'businessIds\'  />', width: 30,
            template: '<input type="checkbox" class="checkbox"  name="businessId" value="#=id #" id="#=id #" />'
        },
        {field: 'business_name', title: '业务'}
    ]
};


var user_business_grid = set_table("#user_business_list", grid_option_add);
user_business_grid.table.on("click", ".checkbox", selectRow);

function get_user_business_list() {
    show_loading();
    $.post(site_url+"get_user_business_list", {
    }, function (res) {
        close_loading();
        if (res.is_success) {
            dataSource_add.splice(0, dataSource_add.length);
            Array.prototype.push.apply(dataSource_add, res.data);
            user_business_grid.dataSource.read();
        }
        else {
            app_alert(res.message);
        }
    })
}


//全选功能
$("#businessIds").on("click", function () {
    selectItems.splice(0, selectItems.length);
    if ($(this).is(":checked")) {
        $(".checkbox").each(function () {
            $(this).prop("checked", true); //此处设置每行的checkbox选中，必须用prop方法
            //$(this).closest("tr").addClass("k-state-selected");
            var row = $(this).closest("tr"),
                dataItem = user_business_grid.dataItem(row);
            selectItems.push(dataItem);
        });
    }
    else {
        $(".checkbox").each(function () {
            $(this).prop("checked", false); //此处设置每行的checkbox不选中，必须用prop方法
            //$(this).closest("tr").removeClass("k-state-selected");  //设置grid 每一行不选中
        });
    }
});

//勾选功能
function selectRow() {
    var checked = this.checked,
        row = $(this).closest("tr");

    if (checked) {
        selectItems.push(user_business_grid.dataItem(row));
        //row.addClass("k-state-selected");
    }
    else {
        selectItems.splice(selectItems.indexOf(user_business_grid.dataItem(row)), 1);
        //row.removeClass("k-state-selected");
    }
}
