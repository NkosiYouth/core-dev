/** @odoo-module **/

import {useService} from "@web/core/utils/hooks"
import {Component, useState, onWillStart} from "@odoo/owl"
import {session} from "@web/session"
import {maskNumber} from "@asterisk_plus_phone/js/utils"

const uid = session.uid

class CallDetail extends Component {
    static template = 'asterisk_plus_phone.call_detail'
    static props = {
        call: Object
    }

    constructor() {
        super(...arguments)
        this.state = useState({
            call: this.props.call,
        })
        this.isMaskCallNumber = false
    }

    setup() {
        super.setup()
        this.orm = useService('orm')
        this.action = useService('action')
        this.user = uid

        onWillStart(async () => {
            this.isMaskCallNumber = await this.orm.call('asterisk_plus.user', 'get_param', ['mask_call_number'])
            await this.getCall(this.state.call.id)
        })
    }

    async getCall(id) {
        const fields = [
            "id",
            "duration_human",
            "called_number",
            "calling_number",
            "answered_user",
            "calling_user",
            "partner",
            "direction",
            "started"
        ]
        const [call] = await this.orm.searchRead("asterisk_plus.call", [["id", "=", id]], fields)
        const answered_user_id = call.answered_user ? call.answered_user[0] : false
        const caller_number = answered_user_id === this.user ? call.calling_number : call.called_number
        call.display_caller_number = this.isMaskCallNumber ? maskNumber(caller_number) : caller_number
        this.state.call = call
    }

    async _createPartner() {
        await this.getCall(this.state.call.id)
        if (this.state.call.partner) {
            this.action.doAction({
                res_id: this.state.call.partner[0],
                res_model: "res.partner",
                target: 'new',
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
            })
        } else {
            const answered_user = this.state.call.answered_user ? this.state.call.answered_user[0] : false
            const phone = answered_user === this.user ? this.state.call.calling_number : this.state.call.called_number
            let context = {
                call_id: this.state.call.id,
                default_phone: phone,
                default_name: `Partner ${phone}`
            }
            this.action.doAction({
                context,
                res_model: 'res.partner',
                target: 'new',
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
            })
        }
    }

    _OpenInCallHistory() {
        this.action.doAction({
            res_id: this.state.call.id,
            res_model: 'asterisk_plus.call',
            target: 'new',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
        })
    }
}

export class Calls extends Component {
    static template = 'asterisk_plus_phone.calls'
    static props = {
        bus: Object,
    }
    static components = {CallDetail}

    constructor() {
        super(...arguments)
        this.bus = this.props.bus
    }

    setup() {
        super.setup()
        this.orm = useService('orm')
        this.action = useService('action')
        this.notification = useService('notification')
        this.user = uid
        this.favorites = []
        this.isMaskCallNumber = false
        this.state = useState({
            calls: [],
            call: null,
        })

        onWillStart(async () => {
            this.bus.addEventListener('busCallsGetCalls', (ev) => this._getCalls(ev))
            this.bus.addEventListener('busCallsGetFavorites', (ev) => this._getFavorites(ev))
            this.bus.addEventListener('busBugReport', (ev) => this._busBugReport(ev))
            await this._getFavorites()
            this.isMaskCallNumber = await this.orm.call('asterisk_plus.user', 'get_param', ['mask_call_number'])
        })
    }

    _getCalls() {
        this.state.calls = []
        const fields = [
            "id",
            "called_number",
            "calling_number",
            "answered_user",
            "calling_user",
            "partner",
            "direction",
            "started"
        ]
        this.orm.searchRead(
            "asterisk_plus.call",
            ["|", ["calling_user", "=", this.user], ["answered_user", "=", this.user]],
            fields,
            {order: "id desc", limit: 20}
        ).then((records) => {
            records.forEach(item => {
                const answered_user = item.answered_user ? item.answered_user[0] : false
                const call_number = answered_user === this.user ? item.calling_number : item.called_number
                item.display_caller_number = this.isMaskCallNumber ? maskNumber(call_number) : call_number
                item.favorite = this.favorites.includes(call_number)
                const local_time = new Date(`${item.started} UTC`).toLocaleTimeString("en-GB")
                item.started = `${item.started.split(' ')[0]} ${local_time}`
            })
            this.state.calls = records
        })
    }

    async _getFavorites() {
        this.favorites = []
        const favorites = await this.orm.searchRead('asterisk_plus_phone.favorite', [], ['phone_number'])
        favorites.forEach((el) => this.favorites.push(el.phone_number))
        this.state.calls.forEach(item => {
            const answered_user = item.answered_user ? item.answered_user[0] : false
            const call_number = answered_user === this.user ? item.calling_number : item.called_number
            item.display_caller_number = this.isMaskCallNumber ? maskNumber(call_number) : call_number
            item.favorite = this.favorites.includes(call_number)
        })
    }

    _busBugReport() {
        const state = JSON.stringify(this.state)
        console.log(`[CALLS]:\n {state: ${state}}`)
    }

    _onClickContactCall(phoneNumber) {
        this.bus.trigger('busPhoneMakeCall', {phone: phoneNumber})
    }

    async _onClickFavorite(call) {
        const kwargs = {}
        const answered_user = call.answered_user ? call.answered_user[0] : false
        kwargs.phone_number = answered_user === this.user ? call.calling_number : call.called_number
        if (call.partner) {
            kwargs.partner = call.partner[0]
        } else if (call.calling_user && call.answered_user) {
            kwargs.user = answered_user === this.user ? call.calling_user[0] : call.answered_user[0]
        } else {
            kwargs.name = kwargs.phone_number
        }

        const domain = [["phone_number", "=", kwargs.phone_number]]
        const getFavorite = await this.orm.search('asterisk_plus_phone.favorite', domain)

        if (getFavorite.length === 0) {
            await this.orm.create('asterisk_plus_phone.favorite', [kwargs])
            this.notification.add('Added to Favorite!', {title: 'Phone', type: 'info'})
            this._getFavorites()
        } else {
            await this.orm.unlink("asterisk_plus_phone.favorite", getFavorite, {})
            await this._getFavorites()
            this.notification.add('Removed to Favorite!', {title: 'Phone', type: 'info'})
        }
    }

    _open_detail(call) {
        this.state.call = call
    }

    _close_call_detail() {
        this.state.call = null
        this._getCalls()
    }
}
