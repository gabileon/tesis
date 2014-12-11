from math import floor

def build_rfc3339_phrase(datetime_obj):
    datetime_phrase = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')
    us = datetime_obj.strftime('%f')

    seconds = -10800

    if seconds is None:
        datetime_phrase += 'Z'
    else:
        # Append: decimal, 6-digit uS, -/+, hours, minutes
        datetime_phrase += ('.%.6s%s%02d:%02d' % (
                            us,
                            ('-' if seconds < 0 else '+'),
                            abs(int(floor(seconds / 3600))),
                            abs(seconds % 3600)
                            ))

    return datetime_phrase