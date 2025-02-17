/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState,onPatched, onMounted } from "@odoo/owl";
import { KsCarousel } from "@ks_dn_advance/js/carousel";

export class ModalDialog extends Component {
    setup() {
        super.setup();
        this.state = useState({
            expand_icon: false,
            pause_icon: false,
        });
        onMounted(() => {
            $('.o_rtl .owl-carousel').css('cssText', 'direction: rtl !important;');
//            $('.owl-carousel').css('cssText', 'direction: ltr !important;');

        })
        onPatched(()=>{
            $('.o_rtl .owl-carousel').css('cssText', 'direction: rtl !important;');
//            $('.owl-carousel').css('cssText', 'direction: ltr !important;');

           this.state.expand_icon == true && this.state.pause_icon == false ?  $('.owl-carousel').trigger('play.owl.autoplay') :$('.owl-carousel').trigger('stop.owl.autoplay');
           this.state.expand_icon == true?  $(".owl-nav").addClass("d-none") : $(".owl-nav").removeClass("d-none");
        })
    }

    expand_icon_click(){
        if(this.state.expand_icon == false){
            this.state.expand_icon = true;
            this.state.pause_icon = false;
        }
        else{
            this.state.expand_icon = false;
            this.state.pause_icon = true;
        }
    }
}

ModalDialog.props = {
    ...KsCarousel.props,
};
ModalDialog.components = { Dialog, KsCarousel };
ModalDialog.template = "ks_dn_advance.ModalDialog";