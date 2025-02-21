def status_translate(status):
    translations = {
        'open': 'Open',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    return translations.get(status, status) 