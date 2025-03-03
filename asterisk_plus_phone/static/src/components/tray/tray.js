/** @odoo-module **/
"use strict"
import {useService} from "@web/core/utils/hooks"
import {browser, setFocus} from "@asterisk_plus_phone/js/utils"
import {Component, useState, onMounted, onWillStart, markup, useRef} from "@odoo/owl"
import {loadJS} from "@web/core/assets"

export class PhoneSysTray extends Component {
    static template = 'asterisk_plus_phone.menu'
    static props = {
        bus: Object,
    }

    constructor() {
        super(...arguments)
        this.bus = this.props.bus
        this.state = useState({
            isDisplay: false,
            inCall: false,
            isContextMenu: false,
            isReportModal: false,
        })
        this.sentry_enabled = false
        this.rMenu = useRef('rMenu')
        this.bugDescription = useRef('bugDescription')
        this.sound = false
        this.microphone = false
        this.message = 'For better user experience grant permission for: '
        this.browser = navigator.userAgent.includes("Firefox") ? browser.firefox : browser.chrome
    }

    setup() {
        super.setup()
        this.notification = useService("notification")
        this.orm = useService("orm")
        // Disable Permission Check
        // this.permissionsChecked = localStorage.getItem('asterisk_plus_phone_permissions_checked')
        this.permissionsChecked = 'true'

        onMounted(() => {
            this.bus.addEventListener('busTraySetState', ({detail: {isDisplay, inCall}}) => {
                this.state.isDisplay = isDisplay
                this.state.inCall = inCall
            })
            if (!this.permissionsChecked) {
                // Check sound permission
                this.testPlayer.play().then(() => {
                    this.sound = true
                    this.checkPermissions()
                }).catch((e) => {
                    this.checkPermissions()
                })
            }
            const self = this
            this.orm.call("asterisk_plus.settings", "get_param", ['sentry_enabled']).then((response) => {
                if (response === true) {
                    self.sentry_enabled = true
                    self.rMenu.el.addEventListener("focusout", function () {
                        self.state.isContextMenu = false
                    })
                    loadJS('https://js-de.sentry-cdn.com/9e7c3efe3d24ce38c0a454974408187b.min.js')
                }
            })
        })

        onWillStart(async () => {
            if (this.permissionsChecked) return
            this.testPlayer = new Audio()
            this.testPlayer.src = "/asterisk_plus_phone/static/src/sounds/mute.mp3"
            this.testPlayer.volume = 0.5
            const self = this
            // Check microphone permission for Chrome
            if (this.browser === browser.chrome) {
                const permissionStatus = await navigator.permissions.query({name: 'microphone'})
                if (permissionStatus.state === "granted") {
                    this.microphone = true
                }
                // Check microphone permission for Firefox
            } else if (this.browser === browser.firefox) {
                navigator.mediaDevices
                    .getUserMedia({video: false, audio: true})
                    .then((stream) => {
                        stream.getTracks().forEach(function (track) {
                            track.stop()
                            self.microphone = true
                        })
                    })
                    .catch((err) => {
                        console.error(`you got an error: ${err}`)
                    })
            }
        })
    }

    checkPermissions() {
        if (!this.microphone || !this.sound) {
            this.notify()
        }
        localStorage.setItem('asterisk_plus_phone_permissions_checked', 'true')
    }

    notify() {
        this.message += this.sound ? '' : '<br/>&emsp; - Sound'
        this.message += this.microphone ? '' : '<br/>&emsp; - Microphone'
        this.message += '<br/><a href="https://help.odoopbx.com/en/articles/8945386-browser-configuration-for-asterisk-plus-phone" target="_blank" style="text-decoration: underline;">See documentation how do this!</a>'
        this.notification.add(this.message, {title: 'Phone', sticky: true, type: 'warning', messageIsHtml: true})
    }

    _onClick() {
        this.bus.trigger('busPhoneToggleDisplay')
    }

    _onClickHangUp() {
        this.bus.trigger('busPhoneHangUp')
        this.state.isDisplay = false
        this.state.inCall = false
    }

    _onContextmenu(ev) {
        if (this.sentry_enabled) {
            ev.preventDefault();
            this.state.isContextMenu = true
            setFocus(this.rMenu.el)
        }
    }

    _onClickBugReport() {
        this.state.isContextMenu = false
        this.state.isReportModal = true
    }

    _onClickCloseReport() {
        this.state.isReportModal = false
        this.bugDescription.el.value = ''
        this.bugDescription.el.style.border = ''
    }

    _onClickSendReport() {
        const bugDescription = this.bugDescription.el.value
        if (!bugDescription) {
            this.notification.add('Missing "Bug Description"', {title: 'Phone', sticky: false, type: 'warning'})
            this.bugDescription.el.style.border = '2px solid #d92929'
        } else {
            this.state.isReportModal = false
            this.notification.add('Report sent successfully!', {title: 'Phone', sticky: false, type: 'info'})
            this.bus.trigger('busBugReport')
            setTimeout(() => Sentry.captureMessage(`[Phone] - Bug report: ${bugDescription}`), 1500)
            this.bugDescription.el.style.border = ''
            this.bugDescription.el.value = ''

        }
    }
}