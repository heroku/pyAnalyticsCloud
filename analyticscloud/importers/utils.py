def metadata_object(fqname, display_name, api_name, **kwargs):
    kwargs['fullyQualifiedName'] = fqname
    kwargs['label'] = display_name
    kwargs['name'] = api_name

    return kwargs


def new_field(fqname, name, **kwargs):
    field = {
        'fullyQualifiedName': fqname,
        'label': name,
        'name': name,
        'description': name,
        'type': None,
        'precision': 0,
        'scale': 0,
        'defaultValue': "",
        'format': None,
        'isSystemField': False,
        'isUniqueId': False,
        'isMultiValue': False,
        'multiValueSeperator': False,
        'acl': None,
        'fiscalMonthOffset': 0
    }

    field.update(kwargs)

    return field


def metadata_text_field(fqname, display_name, api_name, **kwargs):
    kwargs['type'] = 'Text'
    return metadata_object(fqname, display_name, api_name, **kwargs)


def metadata_numeric_field(fqname, display_name, api_name, precision, scale=2, **kwargs):
    kwargs['type'] = 'Numeric'
    kwargs['precision'] = precision
    kwargs['scale'] = scale
    if 'format' not in kwargs:
        kwargs['format'] = '0.' + '#' * scale

    return metadata_object(fqname, display_name, api_name, **kwargs)


def metadata_date_field(fqname, display_name, api_name, date_format="yyyy-MM-dd", **kwargs):
    kwargs['type'] = 'Date'
    kwargs['format'] = date_format
    return metadata_object(fqname, display_name, api_name, **kwargs)


def metadata_factory(fqname, name=None):
    if name is None:
        name = fqname

    metadata = {
        'fileFormat': {
            "charsetName": "UTF-8",
            "fieldsEnclosedBy": "\"",
            "fieldsDelimitedBy": ",",
            "linesTerminatedBy": "\n",
            "numberOfLinesToIgnore": 1,
        },
        'objects': [{
            'connector': 'HerokuConnectAnalyticsCloudUploader',
            'rowLevelSecurityFilter': None,
            'acl': None,
            'fullyQualifiedName': fqname,
            'name': name,
            'label': name,
            'fields': []
        }]
    }

    return metadata, metadata['objects'][0]['fields']


def exclude_columns(table_columns, excludes):
    if excludes is None:
        return table_columns
    return [col for col in table_columns if col.name not in excludes]
