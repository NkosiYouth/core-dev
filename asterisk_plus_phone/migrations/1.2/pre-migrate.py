import logging
from odoo.tools.sql import rename_column

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info('Migrating contact_searching to transfer_contact_search')
    try:
        rename_column(cr, 'asterisk_plus_settings', 'contact_searching', 'transfer_contact_search')
    except Exception as e:
        logger.error('Migration error: %s.', e)
        cr.rollback()
    logger.info('Transfer Contact Search migrated.')
