/** @odoo-module **/

import {useService} from "@web/core/utils/hooks"
import {Component, useState, onWillStart} from "@odoo/owl"
import {session} from "@web/session"
import {maskNumber} from "@asterisk_plus_phone/js/utils"

const uid = session.uid

export class Favorites extends Component {
    static template = 'asterisk_plus_phone.favorites'
    static props = {
        bus: Object,
    }

    constructor() {
        super(...arguments)
        this.bus = this.props.bus
    }

    setup() {
        super.setup()
        this.orm = useService('orm')
        this.action = useService('action')
        this.user = uid
        this.isMaskCallNumber = false
        this.state = useState({
            favorites: [],
        })

        onWillStart(async () => {
            this.isMaskCallNumber = await this.orm.call('asterisk_plus.user', 'get_param', ['mask_call_number'])
            this.getFavorites()
            this.bus.addEventListener('busBugReport', (ev) => this._busBugReport(ev))
        })
    }

    _busBugReport() {
        const state = JSON.stringify(this.state)
        console.log(`[FAVORITES]:\n {state: ${state}}`)
    }

    getFavorites() {
        const fields = [
            "id",
            "name",
            "partner",
            "user",
            "phone_number",
        ]

        this.orm.searchRead("asterisk_plus_phone.favorite", [], fields, {limit: 30}).then((records) => {
            records.forEach(item => {
                item.display_phone_number = this.isMaskCallNumber ? maskNumber(item.phone_number) : item.phone_number
            })
            this.state.favorites = records
        })
    }

    _onClickContactCall(phone_number) {
        this.bus.trigger('busPhoneMakeCall', {phone: phone_number})
    }

    _onClickRemoveFavorite(ev, id) {
        ev.stopPropagation()
        this.orm.unlink("asterisk_plus_phone.favorite", [id], {}).then(() => {
            this.getFavorites()
            this.bus.trigger('busCallsGetFavorites')
        })

    }
}
