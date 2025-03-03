/** @odoo-module **/
import {registry} from "@web/core/registry"
import {PhoneSysTray} from "@asterisk_plus_phone/components/tray/tray"
import {Phone} from "@asterisk_plus_phone/components/phone/phone"
import {session} from "@web/session"

const uid = session.uid
const serviceRegistry = registry.category("services")
const sysTrayRegistry = registry.category("systray")
const mainComponents = registry.category("main_components")
import {EventBus} from "@odoo/owl"

export const phoneService = {
    async start(env, {}) {
        if (env.services.router.current.pathname.includes("/web")) {
            const phone_enabled = await env.services.orm.call("asterisk_plus.settings", "get_param", ['phone_enabled'])
            const {user_config} = await env.services.orm.call('res.users', 'get_sip_user_config', [uid])

            if (phone_enabled && user_config) {
                let bus = new EventBus()
                sysTrayRegistry.add('phoneSysTray', {Component: PhoneSysTray, props: {bus}})
                mainComponents.add('mainPhone', {Component: Phone, props: {bus}})
            }
        } else {
            console.log(`[Phone] Doesn't work on path: ${env.services.router.current.pathname}`)
        }
    }
}
serviceRegistry.add("phone", phoneService)