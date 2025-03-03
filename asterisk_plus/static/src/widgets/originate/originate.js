/** @odoo-module **/
"use strict"

import {CharField} from "@web/views/fields/char/char_field"
import {useService} from "@web/core/utils/hooks"
import {registry} from "@web/core/registry"

export class OriginateCallField extends CharField {
    static template = 'asterisk_plus.OriginateCall'

    setup() {
        super.setup()
        this.orm = useService("orm")
    }

    _onClickOriginateCall(e) {
        e.stopPropagation()
        const args = [this.props.value, this.props.record.resModel, this.props.record.data.id]
        this.orm.call('asterisk_plus.server', 'originate_call', args, {})
    }
}

export class OriginateExtensionField extends CharField {
    static template = 'asterisk_plus.OriginateExtension'

    setup() {
        super.setup()
        this.orm = useService("orm")
    }

    _onClickOriginateExtension() {
        const args = [this.props.value, this.props.record.resModel, this.props.record.data.id]
        this.orm.call('res.partner', 'originate_call', args, {})
    }
}

registry.category("fields").add("originate_call", OriginateCallField)
registry.category("fields").add("originate_extension", OriginateExtensionField)
