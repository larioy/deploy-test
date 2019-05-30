/**
 * Created by kido on 2016/10/14.
 */
function set_table(table_id, new_option) {
    var table_option = $.extend({
        //height:100,
        pageable: {
            pageSize: 10, //每页显示的记录数目,如果要显示分页，必须设置pageSize
            pageSizes: true,
            refresh: true, //显示刷新
            info: true, //显示分页信息，如“显示条目 1 - 4 共 9”
            buttonCount: 5,
            previousNext: true
        }, //隐藏分页
        sortable: true, //表头排序
        autoBind: false,
        dataSource: {
            data: []
        },
        columns: []
    }, new_option);
    return $(table_id).kendoGrid(table_option).data("kendoGrid");
}
