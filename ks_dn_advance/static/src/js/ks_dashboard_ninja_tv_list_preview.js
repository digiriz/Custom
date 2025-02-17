/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import {KsListViewPreview} from '@ks_dashboard_ninja/widgets/ks_list_view/ks_list_view';
import {Ksdashboardgraph} from '@ks_dashboard_ninja/components/ks_dashboard_graphs/ks_dashboard_graphs'
import { localization } from "@web/core/l10n/localization";
import {formatDate,formatDateTime} from "@web/core/l10n/dates";
import { formatFloat,formatInteger } from "@web/views/fields/formatters";
import {parseDateTime,parseDate,} from "@web/core/l10n/dates";
import { session } from "@web/session";

patch(KsListViewPreview.prototype,{
    setup(){
        super.setup()
    },

       value(){
            var rec = this.props.record.data;
            if (rec.ks_dashboard_item_type === 'ks_list_view') {
                if(rec.ks_data_calculation_type === "custom"){
                     return super.value();
                } else {
                   this.calculation_type = rec.ks_data_calculation_type
                   return super.value();
                }
            }
        },
         onChartCanvasClick(ev){
            ev.stopPropagation();
    },
});
patch(Ksdashboardgraph.prototype,{
    setup(){
        super.setup()
    },

       prepare_list(){
            var self = this;
            super.prepare_list();
            this.layout = this.item.ks_list_view_layout;


       },

       renderListData(item) {
        var list_view_data = item;
        var datetime_format = localization.dateTimeFormat;
        var date_format = localization.dateFormat;
        if (list_view_data.type === "ungrouped" && list_view_data) {
            if (list_view_data.fields_type) {
                var index_data = list_view_data.fields_type;
                for (var i = 0; i < index_data.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows.length; j++) {
                        var index = index_data[i];
                        var date = list_view_data.data_rows[j]["data"][i];
                        if (date) {
                            if (index === 'date'){
                                list_view_data.data_rows[j]["data"][i] = luxon.DateTime.fromJSDate(new Date(date + " UTC")).toFormat?.(date_format);
                            }else if (index === 'datetime'){
                                list_view_data.data_rows[j]["data"][i] = luxon.DateTime.fromJSDate(new Date(date + " UTC")).toFormat?.(datetime_format);
                            }else{
//                                list_view_data.data_rows[j]["data"][i] = "";
                            }
                        }else{
//                            list_view_data.data_rows[j]["data"][i] = "";
                        }
                    }
                }
            }
        }
        return list_view_data;
    },
        _ksSortAscOrder(e) {
            if($(e.currentTarget).hasClass("ks_dn_asc") || ($(e.target).parent().parent().hasClass("ks_dn_asc"))){
                var self = this;
                var ks_value_offfset = $(e.currentTarget.parentElement.parentElement.parentElement.parentElement.parentElement).find('.ks_pager').find('.ks_counter').find('.ks_value').text();
                var offset = 0;
                var initial_count = 0;
                if (ks_value_offfset)
                {
                    initial_count = parseInt(ks_value_offfset.split('-')[0])
                    offset = parseInt(ks_value_offfset.split('-')[1])
                }

                var item_id = e.currentTarget.dataset.itemId;
                var field = e.currentTarget.dataset.fields;
                var context = {}
                var user_id = session.uid;
                var context = self.ks_dashboard_data['context'];
                context.user_id = user_id;
                context.offset = offset;
                context.initial_count = initial_count;

                var store = e.currentTarget.dataset.store;
                context.field = field;
                context.sort_order = "ASC"
                var ks_domain
                if(this.props?.item?.ks_dashboard_item_type === 'ks_list_view' && this.env.inDialog){
                    this.env.bus.trigger("GET:ParamsForItemFetch", {item_id: parseInt(item_id), isCarouselParentClass: true});
                    ks_domain = this.domainParams
                }
                else
                    ks_domain = self.__owl__.parent.component.ksGetParamsForItemFetch(parseInt(item_id));
                if (store) {
                    self._rpc("/web/dataset/call_kw/ks_dashboard_ninja.item/ks_get_list_data_orderby_extend",{
                        model: 'ks_dashboard_ninja.item',
                        method: 'ks_get_list_data_orderby_extend',
                        args: [
                            [parseInt(item_id)], ks_domain
                        ],
                        kwargs:{context: context}
                    }).then(function(result) {
                        if (result) {
                            result = self.renderListData(result)
                            self.item.ks_list_view_data = result;
                            self.prepare_list()
    //                        $($(".ks_dashboard_main_content").find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").empty();
    //                       / $($(".ks_dashboard_main_content").find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").append($listBody);
                            }
                    }.bind(this));


                    $($(this.ks_list_view.el).find(".ks_sort_up[data-fields=" + field + "]")).removeClass('ks_plus')
                    $($(this.ks_list_view.el).find(".ks_sort_down[data-fields=" + field + "]")).addClass('ks_plus')
                    $($(this.ks_list_view.el).find(".list_header[data-fields=" + field + "]")).removeClass('ks_dn_asc')
                    $($(this.ks_list_view.el).find(".list_header[data-fields=" + field + "]")).addClass('ks_dn_desc')
                }

            }else{
                var self = this;
                var ks_value_offfset = $(e.currentTarget.parentElement.parentElement.parentElement.parentElement.parentElement).find('.ks_pager').find('.ks_counter').find('.ks_value').text();
                var offset = 0;
                var initial_count = 0;
                if (ks_value_offfset)
                {
                    initial_count = parseInt(ks_value_offfset.split('-')[0])
                    offset = parseInt(ks_value_offfset.split('-')[1])
                }
                var item_id = e.currentTarget.dataset.itemId;
                var field = e.currentTarget.dataset.fields;
                var context = self.ks_dashboard_data['context']
                var user_id = session.uid;
                context.user_id = user_id;
                context.offset = offset;
                context.initial_count = initial_count;
                var store = e.currentTarget.dataset.store;
                context.field = field;
                context.sort_order = "DESC";
                var ks_domain
                if(this.props?.item?.ks_dashboard_item_type === 'ks_list_view' && this.env.inDialog){
                    this.env.bus.trigger("GET:ParamsForItemFetch", {item_id: parseInt(item_id), isCarouselParentClass: true});
                    ks_domain = this.domainParams
                }
                else
                    ks_domain = self.__owl__.parent.component.ksGetParamsForItemFetch(parseInt(item_id));
                if (store) {
                    self._rpc("/web/dataset/call_kw/ks_dashboard_ninja.item/ks_get_list_data_orderby_extend",{
                        model: 'ks_dashboard_ninja.item',
                        method: 'ks_get_list_data_orderby_extend',
                        args: [
                            [parseInt(item_id)], ks_domain
                        ],
                        kwargs:{context : context}
                    }).then(function(result) {
                        if (result){
                            result = self.renderListData(result)
                            self.item.ks_list_view_data = result;
                            self.prepare_list()
                        }
                    }.bind(this));
                    $($(this.ks_list_view.el).find(".ks_sort_down[data-fields=" + field + "]")).removeClass('ks_plus')
                    $($(this.ks_list_view.el).find(".ks_sort_up[data-fields=" + field + "]")).addClass('ks_plus')
                    $($(this.ks_list_view.el).find(".list_header[data-fields=" + field + "]")).addClass('ks_dn_asc')
                    $($(this.ks_list_view.el).find(".list_header[data-fields=" + field + "]")).removeClass('ks_dn_desc')
                }

            }
            }


});

