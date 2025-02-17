/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Component, onWillStart, useState ,onMounted, onWillRender, useRef, onWillPatch, onRendered, useEffect, onWillUpdateProps  } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { isBrowserChrome, isMobileOS } from "@web/core/browser/feature_detection";
import { Ksdashboardtile } from '@ks_dashboard_ninja/components/ks_dashboard_tile_view/ks_dashboard_tile';
import { Ksdashboardtodo } from '@ks_dashboard_ninja/components/ks_dashboard_to_do_item/ks_dashboard_to_do';
import { Ksdashboardkpiview } from '@ks_dashboard_ninja/components/ks_dashboard_kpi_view/ks_dashboard_kpi';
import { Ksdashboardgraph } from '@ks_dashboard_ninja/components/ks_dashboard_graphs/ks_dashboard_graphs';

export class KsCarousel extends Component{
    setup(){
        var self = this;
        this.carousel = useRef("carousel")
        onMounted(this._mounted);
        self.ksRenderTvDashboardItems(self.props.items)
    }
    ksRenderTvDashboardItems(items){
        var self = this;
        this.ks_dashboard_data = self.props.dashboard_data
        this.tiles = [];
        this.kpi = [];
        this.graph = [];
        this.to_do = [];
        for (var i = 0; i < items.length; i++) {
            if (items[i].ks_dashboard_item_type === 'ks_tile') {
                this.tiles.push(items[i]);
            } else if (items[i].ks_dashboard_item_type === 'ks_kpi') {
                this.kpi.push(items[i]);
            } else if (items[i].ks_dashboard_item_type === 'ks_to_do') {
                this.to_do.push(items[i])
           } else {
                this.graph.push(items[i])
           }
        }


    }
    _renderTiles(){
        var self = this;
        this.tile_item = []
        if (isMobileOS()){
        var count  =  Math.round(this.tiles.length)
        var kscontainer =[]
        for(var i = 1; i<= count; i++){
            var ks_tiles = this.tiles.splice(0,1);
            var container = [];
            for (var j = 0; j<ks_tiles.length; j++){
                var item_data = ks_tiles[j];
                    item_data.ks_tv_play = true
                    self.ksAllowItemClick = false

                    container.push(item_data);
            }
            kscontainer.push(container)
            this.tiles.push(kscontainer)
        }
        }else{
        var count  =  Math.round(this.tiles.length/2)
        var kscontainer =  []
        for(var i = 1; i<= count; i++){
            var ks_tiles = this.tiles.splice(0,2);
            var container = [];
            for (var j = 0; j<ks_tiles.length; j++){
                var item_data = ks_tiles[j];
                    item_data.ks_tv_play = true
                    self.ksAllowItemClick = false

                container.push(item_data);
            }
            kscontainer.push(container)
            if (i%2 === 0){
                this.tile_item.push(kscontainer);
                kscontainer = []
            }
        }
        if(kscontainer.length){
            this.tile_item.push(kscontainer);
        }
        }

    }
    _mounted(){
        var self = this;
        $("#carousel_graph").append(self.carousel.el)
//            $(".ks_dashboard_main_content").append(self.carousel.el)
        $('.owl-carousel').find(".grid-stack-item.ks_chart_container").each(function(index,item){
            $(item).removeClass("grid-stack-item")
            $(item).addClass("ks-tv-item")
            item.style.pointerEvents = 'none'
            $(item).find(".ks_dashboard_item_button_container").remove()
        })
        $('.owl-carousel').find(".ks_dashboard_item_button_container").each(function(index,item){
            $(item).remove()
        })
        $('.owl-carousel').find(".ks_list_view_container").each(function(index,item){
            $(item).parent().addClass("ks-tv-item")
        })

        var speed = self.props.dashboard_data.ks_croessel_speed ? parseInt(self.props.dashboard_data.ks_croessel_speed) : 5000
        $('.ks_float_tv').removeClass('d-none');

        $('.owl-carousel').owlCarousel({
            rtl: $('.o_rtl').length>0,
            loop:true,
            nav:true,
            dots:false,
            items : 1,
            margin: 15,
            autoplay:false,
            autoplayTimeout:speed,
            slideBy: 1,
            responsiveClass: true,
            autoplayHoverPause: true,
            navText: ["<img src='/ks_dn_advance/static/description/images/left.png'>", "<img src='/ks_dn_advance/static/description/images/right.png'>"],
        });
        if (self.props.dashboard_data.ks_dashboard_background_color != undefined){
            $('.owl-carousel').find('.ks_chart_container').each(function() {
                var currentElement = $(this);
                if (self.props.dashboard_data.ks_dark_mode_enable == true){
                    currentElement.children().css({"backgroundColor": '#2a2a2a'});
                }
                else{
                    currentElement.children().css({"backgroundColor": self.props.dashboard_data.ks_dashboard_background_color.split(',')[0]});
                }
            });
        }
        function updateCurrentItemName(itemId) {
            var activeItem = self.props.items.find(item => item.id == parseInt(itemId,10));
//                var displayStr = itemId + activeItem.ks_ai_analysis
            $('#item_explanation').text(activeItem.ks_ai_analysis || 'No explanation available');
        }
        const currentItem = $(".owl-item.active");
        const itemId = currentItem[0].firstChild.id;
        updateCurrentItemName(itemId);

            $(".owl-nav").on('click', '.owl-next', function () {
                const currentItem = $(".owl-item.active");
                const itemId = currentItem[0].firstChild.id;
                updateCurrentItemName(itemId);
            });

            $(".owl-nav").on('click', '.owl-prev', function () {
                const currentItem = $(".owl-item.active");
                const itemId = currentItem[0].firstChild.id;
                updateCurrentItemName(itemId);
            });
        }
        ksStopTvDashboard(e){
          var self =this;
            $('.owl-carousel').owlCarousel('destroy');
            $(self.carousel.el).remove()
         this.ksAllowItemClick = true;
         this.env.services.dialog.closeAll()
             }
        speak_once(ev,item){
            let x = 0;
        }
};
KsCarousel.props = {
    items : {type:Object,Optional:true},
    dashboard_data:{type:Object,Optional:true},
    ksdatefilter :{type:String,Optional:true},
    pre_defined_filter : {type:Object,Optional:true},
    custom_filter:{type:Object,Optional:true},
    close:{type:Function,Optional:true},
    selectedItems: { type: Function, optional: true }
}
KsCarousel.components = { Ksdashboardtile,  Ksdashboardgraph, Ksdashboardkpiview, Ksdashboardtodo};
KsCarousel.template = "ks_dn_advance.KsCarousel";